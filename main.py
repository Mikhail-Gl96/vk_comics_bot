import os
import random

import dotenv
import requests

import download_pics
import vk_api


def get_pics_max_number():
    temp_url = f'https://xkcd.com/info.0.json'
    try:
        response = requests.get(temp_url)
        img_last_num = response.json()['num']
        return img_last_num
    except Exception as e:
        print(f'Error: {e}')


def get_pic_from_xkcd(numb, path):
    temp_url = f'https://xkcd.com/{numb}/info.0.json'
    try:
        response = requests.get(temp_url).json()
        img_url = response['img']
        img_comment = response['alt']
        img_path = download_pics.load_and_save_img_from_url(img_url, path=os.path.join(path, img_url.split('/')[-1]))
        return {'path': img_path, 'comment': img_comment}
    except Exception as e:
        print(f'Error: {e}')


if __name__ == "__main__":
    dotenv.load_dotenv()
    my_vk_key = os.getenv('MY_VK_KEY')
    my_vk_group_id = os.getenv('MY_GROUP_ID')

    base_path = os.getcwd()
    dir_name = 'images'
    image_paths = os.path.join(base_path, dir_name)
    os.makedirs(image_paths, exist_ok=True)

    random_img_num = random.randint(0, get_pics_max_number())
    current_img = get_pic_from_xkcd(random_img_num, image_paths)
    vk_api.create_post_on_group_wall(group_id=my_vk_group_id,
                                     current_img=current_img,
                                     my_vk_key=my_vk_key)
    os.remove(current_img['path'])

