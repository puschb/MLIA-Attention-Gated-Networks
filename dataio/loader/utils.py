import nibabel as nib
import numpy as np
import os
from utils.util import mkdir
import SimpleITK as sitk

def is_image_file(filename):
    return any(filename.endswith(extension) for extension in [".nii.gz"])


def load_nifti_img(filepath, dtype):
    '''
    NIFTI Image Loader
    :param filepath: path to the input NIFTI image
    :param dtype: dataio type of the nifti numpy array
    :return: return numpy array
    '''
    nim = nib.load(filepath)
    out_nii_array = np.array(nim.get_data(),dtype=dtype)
    out_nii_array = np.squeeze(out_nii_array) # drop singleton dim in case temporal dim exists
    meta = {'affine': nim.get_affine(),
            'dim': nim.header['dim'],
            'pixdim': nim.header['pixdim'],
            'name': os.path.basename(filepath)
            }

    return out_nii_array, meta
def is_mhd_file(x):
    return x.endswith('.mhd')

def load_mhd_image(filepath):
    itk_image = sitk.ReadImage(filepath)
    np_image = sitk.GetArrayFromImage(itk_image)
    spacing = itk_image.GetSpacing()
    origin = itk_image.GetOrigin()
    
    return np_image, spacing, origin

def one_hot_encode(target, n_classes):
    one_hot_encoded = np.zeros((n_classes, target.shape[0], target.shape[1]), dtype=np.uint8)
    for i in range(target.shape[0]):
        for j in range(target.shape[1]):
            one_hot_encoded[target[i, j], i, j] = 1
    return one_hot_encoded


def write_nifti_img(input_nii_array, meta, savedir):
    mkdir(savedir)
    affine = meta['affine'][0].cpu().numpy()
    pixdim = meta['pixdim'][0].cpu().numpy()
    dim    = meta['dim'][0].cpu().numpy()

    img = nib.Nifti1Image(input_nii_array, affine=affine)
    img.header['dim'] = dim
    img.header['pixdim'] = pixdim

    savename = os.path.join(savedir, meta['name'][0])
    print('saving: ', savename)
    nib.save(img, savename)


def check_exceptions(image, label=None):
    if label is not None:
        if image.shape != label.shape:
            print('Error: mismatched size, image.shape = {0}, '
                  'label.shape = {1}'.format(image.shape, label.shape))
            #print('Skip {0}, {1}'.format(image_name, label_name))
            raise(Exception('image and label sizes do not match'))

    if image.max() < 1e-6:
        print('Error: blank image, image.max = {0}'.format(image.max()))
        #print('Skip {0} {1}'.format(image_name, label_name))
        raise (Exception('blank image exception'))

if __name__ == '__main__':
    img, _, _ = load_mhd_image('/home/bhx5gh/Documents/MLIA/MLIA-Attention-Gated-Networks/data/Segmentation_data/Training/Labels/seg_0.mhd')
    unique, counts = np.unique(arr, return_counts=True)
    print(unique, counts)
