import math
import torch.nn as nn
from .utils import unetConv2, UnetUp2_CT, UnetDsv2, UnetGridGatingSignal2
import torch.nn.functional as F
from models.networks_other import init_weights
from models.layers.grid_attention_layer import GridAttentionBlock2D

class attention_unet_2d(nn.Module):

    def __init__(self, feature_scale=4, n_classes=21, is_deconv=True, in_channels=3, is_batchnorm=True, 
        nonlocal_mode='concatenation', attention_dsample = (2,2)): #TODO: check attention_dsample
        super(attention_unet_2d, self).__init__()
        self.is_deconv = is_deconv
        self.in_channels = in_channels
        self.is_batchnorm = is_batchnorm
        self.feature_scale = feature_scale

        filters = [64, 128, 256, 512, 1024]
        filters = [int(x / self.feature_scale) for x in filters]

        # downsampling
        # default kernalsize = 3 and default padding size = 1
        self.conv1 = unetConv2(self.in_channels, filters[0], self.is_batchnorm)
        self.maxpool1 = nn.MaxPool2d(kernel_size=2)

        self.conv2 = unetConv2(filters[0], filters[1], self.is_batchnorm)
        self.maxpool2 = nn.MaxPool2d(kernel_size=2)

        self.conv3 = unetConv2(filters[1], filters[2], self.is_batchnorm)
        self.maxpool3 = nn.MaxPool2d(kernel_size=2)

        self.conv4 = unetConv2(filters[2], filters[3], self.is_batchnorm)
        self.maxpool4 = nn.MaxPool2d(kernel_size=2)

        self.center = unetConv2(filters[3], filters[4], self.is_batchnorm)
        self.gating = UnetGridGatingSignal2(filters[4], filters[4], kernel_size=1, is_batchnorm=self.is_batchnorm)

        #attention blocks
        self.attentionblock2 = MultiAttentionBlock2d(in_size=filters[1], gate_size=filters[2], inter_size=filters[1],
                                nonlocal_mode=nonlocal_mode, sub_sample_factor=attention_dsample)
        self.attentionblock3 = MultiAttentionBlock2d(in_size=filters[2], gate_size=filters[3], inter_size=filters[2],
                                nonlocal_mode=nonlocal_mode, sub_sample_factor=attention_dsample)
        self.attentionblock4 = MultiAttentionBlock2d(in_size=filters[3], gate_size=filters[4], inter_size=filters[3],
                                nonlocal_mode=nonlocal_mode, sub_sample_factor=attention_dsample)

        # upsampling
        self.up_concat4 = UnetUp2_CT(filters[4], filters[3], self.is_batchnorm)
        self.up_concat3 = UnetUp2_CT(filters[3], filters[2], self.is_batchnorm)
        self.up_concat2 = UnetUp2_CT(filters[2], filters[1], self.is_batchnorm)
        self.up_concat1 = UnetUp2_CT(filters[1], filters[0], self.is_batchnorm)

        # deep supervision
        self.dsv4 = UnetDsv2(in_size=filters[3], out_size=n_classes, scale_factor=8)
        self.dsv3 = UnetDsv2(in_size=filters[2], out_size=n_classes, scale_factor=4)
        self.dsv2 = UnetDsv2(in_size=filters[1], out_size=n_classes, scale_factor=2)
        self.dsv1 = nn.Conv3d(in_channels=filters[0], out_channels=n_classes, kernel_size=1)

        # final conv (without any concat)
        self.final = nn.Conv2d(filters[0], n_classes, 1)

        # initialise weights
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                init_weights(m, init_type='kaiming')
            elif isinstance(m, nn.BatchNorm2d):
                init_weights(m, init_type='kaiming')


    def forward(self, inputs):
        conv1 = self.conv1(inputs)
        maxpool1 = self.maxpool1(conv1)

        conv2 = self.conv2(maxpool1)
        maxpool2 = self.maxpool2(conv2)

        conv3 = self.conv3(maxpool2)
        maxpool3 = self.maxpool3(conv3)

        conv4 = self.conv4(maxpool3)
        maxpool4 = self.maxpool4(conv4)

        center = self.center(maxpool4)
        gating = self.gating(center)

        #attention + upscaling
        g_conv4, att4 = self.attentionblock4(conv4, gating)
        up4 = self.up_concat4(g_conv4, center)
        g_conv3, att3 = self.attentionblock3(conv3, up4)
        up3 = self.up_concat3(g_conv3, up4)
        g_conv2, att2 = self.attentionblock2(conv2, up3)
        up2 = self.up_concat2(g_conv2, up3)
        up1 = self.up_concat1(conv1, up2)

        #deep supervision
        dsv4 = self.dsv4(up4)
        dsv3 = self.dsv3(up3)
        dsv2 = self.dsv2(up2)
        dsv1 = self.dsv1(up1)
        final = self.final(torch.cat([dsv1,dsv2,dsv3,dsv4], dim=1))

        return final

    @staticmethod
    def apply_argmax_softmax(pred):
        log_p = F.softmax(pred, dim=1)

        return log_p

class MultiAttentionBlock2d(nn.Module):
    def __init__(self, in_size, gate_size, inter_size, nonlocal_mode, sub_sample_factor):
        super(MultiAttentionBlock2d, self).__init__()
        self.gate_block_1 = GridAttentionBlock2D(in_channels=in_size, gating_channels=gate_size,
                                                 inter_channels=inter_size, mode=nonlocal_mode,
                                                 sub_sample_factor= sub_sample_factor)
        self.gate_block_2 = GridAttentionBlock2D(in_channels=in_size, gating_channels=gate_size,
                                                 inter_channels=inter_size, mode=nonlocal_mode,
                                                 sub_sample_factor=sub_sample_factor)
        self.combine_gates = nn.Sequential(nn.Conv2d(in_size*2, in_size, kernel_size=1, stride=1, padding=0),
                                           nn.BatchNorm2d(in_size),
                                           nn.ReLU(inplace=True)
                                           )

        # initialise the blocks
        for m in self.children():
            if m.__class__.__name__.find('GridAttentionBlock2D') != -1: continue
            init_weights(m, init_type='kaiming')

    def forward(self, input, gating_signal):
        gate_1, attention_1 = self.gate_block_1(input, gating_signal)
        gate_2, attention_2 = self.gate_block_2(input, gating_signal)

        #TODO: check if this causes an error
        return self.combine_gates(torch.cat([gate_1, gate_2], 1)), torch.cat([attention_1, attention_2], 1)












