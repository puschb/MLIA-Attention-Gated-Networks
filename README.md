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

First clone the repository, then cd into the directory and run `source env.sh` to setup the environment and install packages. After the packages are installed, go to the torchsample/callbacks.py file in your site packages (ENV/lib/python3.11/site-packages/torchsample/callbacks.py) and change the following import line `from collections import Iterable` to `from collections.abc import Iterable`. To train the Attention U-Net on Rivanna, run `sbatch train.slurm`.  After running the training script, the resulting training plots will be in figs/model\_name (unet\_ct\_multi\_att\_dsv for the Attention U-net) and the model checkpoints will be in checkpoints/experiment\_unet\_ct\_multi\_att\_dsv\_segmentation. To run hyperparameter tuning, run `sbatch tune.slurm`.

<!-- 
After the packages are installed, go to the torchsample/callbacks.py file in your site packages and change the following import line
from collections import Iterable
to
from collections.abc import Iterable
-->

