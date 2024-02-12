""" This code creates different versions of the same face image in order to 
help with accurately performing facial recognition. 
"""

from imgaug import augmenters as iaa
import imageio.v2 as imageio
import matplotlib.pyplot as plt
import os
import sys
from rich.console import Console
from rich import print
from module import MyKwargs
from module import CheckParams

import glob


def primeAugmentations():
    # Define a sequence of augmentations
    seq = iaa.Sequential(
        [
            iaa.Fliplr(0.5),  # horizontal flips
            iaa.Crop(percent=(0, 0.1)),  # random crops
            iaa.Sometimes(0.5, iaa.GaussianBlur(sigma=(0, 0.5))),
            iaa.contrast.LinearContrast((0.75, 1.5)),
            iaa.AdditiveGaussianNoise(loc=0, scale=(0.0, 0.05 * 255), per_channel=0.5),
            iaa.Multiply((0.8, 1.2), per_channel=0.2),
            iaa.Affine(
                scale={"x": (0.8, 1.2), "y": (0.8, 1.2)},
                translate_percent={"x": (-0.2, 0.2), "y": (-0.2, 0.2)},
                rotate=(-25, 25),
                shear=(-8, 8),
            ),
        ],
        random_order=True,
    )  # apply augmenters in random order
    return seq


def performAugmentations(**kwargs):
    print(kwargs)

    seq = kwargs.get("seq", None)
    io_image = kwargs.get("io_image", None)
    base_name = kwargs.get("base_name", None)
    save_path = kwargs.get("save_path", "images_augmented")
    save_images = kwargs.get("save_images", 1)
    show_images = kwargs.get("show_images", 0)

    if not os.path.exists(save_path):
        os.makedirs(save_path)

    augmented_images = []

    for i in range(10):
        augmented_images.append(seq.augment_image(io_image))

    for idx, aug_image in enumerate(augmented_images):
        if save_images == True:
            path = os.path.join(save_path, f"{base_name}-{idx}.jpg")
            print(f"saving: {path}")
            imageio.imwrite(path, aug_image)  # Save augmented image
        if show_images == True:
            plt.imshow(aug_image)  # Display augmented image
            plt.show()


if __name__ == "__main__":
    # Process command-line arguments into kwargs...

    args, kwargs = MyKwargs(sys.argv)

    if not CheckParams(
        kwargs, ["file_name", "src_path", "save_path", "show_images", "save_images"]
    ):
        exit(1)  # Exit if required parameters are missing

    print(kwargs)

    file_name = kwargs["file_name"]
    save_path = kwargs["save_path"]
    src_path = kwargs["src_path"]
    show_images = kwargs.get("show_images", 0)
    save_images = kwargs.get("save_images", 1)

    input_file = os.path.join(src_path, file_name)

    if os.path.isfile(input_file):
        # Load your image
        io_image = imageio.imread(input_file)
        seq = primeAugmentations()
        performAugmentations(
            seq=seq,
            io_image=io_image,
            base_name=file_name[:-4],
            save_path=save_path,
            save_images=save_images,
            show_images=show_images,
        )
