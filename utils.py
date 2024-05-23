from PIL import Image


def load_image(file_path):
    return Image.open(file_path)


def save_image(image, file_path):
    image.save(file_path)
