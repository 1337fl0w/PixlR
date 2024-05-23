import numpy as np
from PIL import Image
from typing import Callable
from enum import Enum


class SortMethod(Enum):
    LUMINOSITY = 1
    HUE = 2
    SATURATION = 3


def sort_pixels(image: Image, value: Callable, condition: Callable, rotation: int = 0) -> Image:
    image = image.convert("RGBA")  # Ensure image is in RGBA format to handle transparency
    pixels = np.rot90(np.array(image), rotation)

    # Separate alpha channel and RGB channels
    alpha_channel = pixels[:, :, 3]
    pixels_rgb = pixels[:, :, :3]

    values = value(pixels_rgb)
    edges = np.apply_along_axis(lambda row: np.convolve(row, [-1, 1], 'same'), 0, condition(values))
    intervals = [np.flatnonzero(row) for row in edges]

    for row, key in enumerate(values):
        order = np.split(key, intervals[row])
        for index, interval in enumerate(order[1:]):
            order[index + 1] = np.argsort(interval) + intervals[row][index]
        order[0] = range(order[0].size)
        order = np.concatenate(order)

        for channel in range(3):
            pixels_rgb[row, :, channel] = pixels_rgb[row, order.astype('uint32'), channel]

    # Recombine RGB and alpha channels
    sorted_pixels = np.dstack((pixels_rgb, alpha_channel))

    # Mask the sorted pixels with the original alpha channel
    sorted_pixels[:, :, 3] = alpha_channel

    return Image.fromarray(np.rot90(sorted_pixels, -rotation))


def pixel_sort(image, threshold=100, sort_method=SortMethod.LUMINOSITY, direction=1):
    sort_fraction = threshold / 255  # Convert threshold to a fraction between 0 and 1

    def luminosity(pixels):
        return np.average(pixels, axis=2) / 255

    def hue(pixels):
        r, g, b = np.split(pixels, 3, axis=2)
        return np.arctan2(np.sqrt(3) * (g - b), 2 * r - g - b)[:, :, 0]

    def saturation(pixels):
        r, g, b = np.split(pixels, 3, axis=2)
        maximum = np.maximum(r, np.maximum(g, b))
        minimum = np.minimum(r, np.minimum(g, b))
        epsilon = 1e-10  # Small value to avoid division by zero
        return ((maximum - minimum) / (maximum + epsilon))[:, :, 0]

    value_map = {
        SortMethod.LUMINOSITY: luminosity,
        SortMethod.HUE: hue,
        SortMethod.SATURATION: saturation
    }

    def condition(lum):
        return (lum > (1 - sort_fraction) / 2) & (lum < (1 + sort_fraction) / 2)

    return sort_pixels(image, value_map[sort_method], condition, direction)
