import os
import random
import urllib

import dotenv
import requests

import download_pics
import vk_api


def get_pics_max_number():
    temp_url = f'https://xkcd.com/info.0.json'
    response = requests.get(temp_url)
    response.raise_for_status()
    img_last_num = response.json()['num']
    return img_last_num


def get_pic_from_xkcd(numb, path):
    temp_url = f'https://xkcd.com/{numb}/info.0.json'
    response = requests.get(temp_url)
    response.raise_for_status()
    response = response.json()
    img_url = response['img']
    img_comment = response['alt']
    img_name = os.path.split(urllib.parse.urlsplit(img_url)[2])[-1]
    img_path = download_pics.load_and_save_one_size_and_extension_img_from_url(url=img_url,
                                                                               path=os.path.join(path, img_name))
    return img_path, img_comment


if __name__ == "__main__":
    dotenv.load_dotenv()
    my_vk_key = os.getenv('MY_VK_KEY')
    my_vk_group_id = os.getenv('MY_GROUP_ID')

    base_path = os.getcwd()
    dir_name = 'images'
    image_path = os.path.join(base_path, dir_name)
    os.makedirs(image_path, exist_ok=True)

    random_img_num = random.randint(0, get_pics_max_number())
    img_path, img_comment = get_pic_from_xkcd(random_img_num, image_path)
    try:
        vk_api.create_post_on_group_wall(group_id=my_vk_group_id,
                                         img_path=img_path,
                                         img_comment=img_comment,
                                         my_vk_key=my_vk_key)
    except Exception as e:
        print(f'Error: {e}')
    finally:
        os.remove(image_path)

