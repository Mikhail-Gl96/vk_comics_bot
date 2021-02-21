import requests
from PIL import Image


def load_and_save_one_extension_img_from_url(url, path):
    response = requests.get(url=url, verify=False, stream=True)
    response.raise_for_status()
    image = Image.open(response.raw)
    rgb_im = image.convert('RGB')
    rgb_im.save(f'{path}')
    return path
