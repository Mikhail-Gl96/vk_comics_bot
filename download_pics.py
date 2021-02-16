import requests
from PIL import Image


def load_and_save_img_from_url(url, path):
    response = requests.get(url=url, verify=False, stream=True)
    response.raise_for_status()
    try:
        image = Image.open(response.raw)
        image.thumbnail((1080, 1080))
        rgb_im = image.convert('RGB')
        rgb_im.save(f'{path}')
        return path
    except IOError:
        print(f"Unable to open image from {url}")
