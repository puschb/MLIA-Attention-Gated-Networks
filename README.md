# Attention Gated Networks <br /> (Image Classification & Segmentation)

Pytorch implementation of attention gates used in U-Net and VGG-16 models. The framework can be utilised in both medical image classification and segmentation tasks. 

<p align="center">
    <img src="figures/figure1.png" width="640"> <br />
    <em> The schematics of the proposed Attention-Gated Sononet</em>
</p>

<p align="center">
    <img src="figures/figure2.jpg" width="640"> <br />
    <em> The schematics of the proposed additive attention gate</em>
</p>

### References:

1) "Attention-Gated Networks for Improving Ultrasound Scan Plane Detection", MIDL'18, Amsterdam <br />
[Conference Paper](https://openreview.net/pdf?id=BJtn7-3sM) <br />
[Conference Poster](https://www.doc.ic.ac.uk/~oo2113/posters/MIDL2018_poster_Jo.pdf)

2) "Attention U-Net: Learning Where to Look for the Pancreas", MIDL'18, Amsterdam <br />
[Conference Paper](https://openreview.net/pdf?id=Skft7cijM) <br />
[Conference Poster](https://www.doc.ic.ac.uk/~oo2113/posters/MIDL2018_poster.pdf)

### Installation and Running
<!-- pip install -r requirements.txt -->
<!-- pip install -e . -->

First clone the repository, then cd into the directory and run `source env.sh` to setup the environment and install packages. After the packages are installed, go to the torchsample/callbacks.py file in your site packages (ENV/lib/python3.11/site-packages/torchsample/callbacks.py) and change the following import line `from collections import Iterable` to `from collections.abc import Iterable`.

#### Training on Rivanna
##### Training with Interactive Environment
To train the model run the following command: `python train_segmentation.py -c configs/config_attn_unet_segmentation.json`.
After running the training script, the resulting training plots will be in figs/model\_name (unet\_ct\_multi\_att\_dsv for the Attention U-net) and the model checkpoints will be in checkpoints/experiment\_unet\_ct\_multi\_att\_dsv\_segmentation. 

To train the model with hyperparameter search run the following command: `python tune_segmentation.py -c configs/config_attn_unet_segmentation.json`

##### Training with SLURM
 To train the Attention U-Net on Rivanna, run `sbatch train.slurm`. The terminal outputs for the job will be in the segmentation-[RIVANNA_USER_ID]-[SLURM_JOB_ID].err and segmentation-[RIVANNA_USER_ID]-[SLURM_JOB_ID].out files. After running the training script, the resulting training plots will be in figs/model\_name (unet\_ct\_multi\_att\_dsv for the Attention U-net) and the model checkpoints will be in checkpoints/experiment\_unet\_ct\_multi\_att\_dsv\_segmentation. 
 
 To run hyperparameter tuning, run `sbatch tune.slurm`. The terminal outputs for the job will be in the tune-[RIVANNA_USER_ID]-[SLURM_JOB_ID].err and tune-[RIVANNA_USER_ID]-[SLURM_JOB_ID].out files.

 #### Visualizing Attention Maps
 To visualize attention maps run `python visualize_attention_mlia.py -c [CONFIG_NAME] -p [CHECKPOINT_NAME] -e [EXPERIMENT_NAME]`
 
 Ex. `python visualize_attention_mlia.py -c config_attn_unet_segmentation -p 049_net_S -e experiment_unet_ct_multi_att_dsv_segmentation`

<!-- 
After the packages are installed, go to the torchsample/callbacks.py file in your site packages and change the following import line
from collections import Iterable
to
from collections.abc import Iterable
-->

