import requests


def post_request_to_vk_api(method, parameters, access_token, v='5.130'):
    url = f'https://api.vk.com/method/{method}'
    data = {
        'access_token': access_token,
        'v': v
    }
    data.update(parameters)
    response = requests.post(url=url, data=data)
    # Если от вк придет ответ отличный от 200 - могли ошибиться в url или еще что-то, то сработает raise_for_status
    response.raise_for_status()
    response = response.json()
    # Если ошибка в теле запроса - обработаем вручную
    if not response.get('error'):
        raise requests.HTTPError(f'{response["error"]}')
    return response


def get_url_to_upload_photo(group_id, vk_key):
    method = 'photos.getWallUploadServer'
    parameters = {'group_id': group_id}
    response = post_request_to_vk_api(method=method, parameters=parameters, access_token=vk_key)
    return response['response']['upload_url'], response['response']['album_id'], response['response']['user_id']


def upload_photo_on_wall(image_path, upload_url):
    with open(image_path, 'rb') as file:
        parameters = {
            'photo': file,
            'content_type': 'multipart/form-data'
        }
        response = requests.post(url=upload_url, files=parameters)
        response.raise_for_status()
        response = response.json()
        # Если пришел пустой массив с фото - значит где-то ошибка
        if not response.get('photo'):
            raise ValueError(f'photo is empty: {response}')
    return response['server'], response['photo'], response['hash']


def save_wall_photo(group_id, photo, server, photo_hash, vk_key):
    method = 'photos.saveWallPhoto'
    parameters = {
        'group_id': group_id,
        'photo': photo,
        'server': server,
        'hash': photo_hash
    }
    response = post_request_to_vk_api(method=method, parameters=parameters, access_token=vk_key)
    return response


def create_wall_post_in_group(group_id, message, attachments_type, owner_id, media_id, vk_key):
    method = 'wall.post'
    parameters = {
        'owner_id': f'-{group_id}',
        'from_group': 1,
        'message': message,
        'attachments': f'{attachments_type}{owner_id}_{media_id}'
    }
    response = post_request_to_vk_api(method=method, parameters=parameters, access_token=vk_key)
    return response


def create_post_on_group_wall(group_id, img_path, img_comment, vk_key):
    upload_url, album_id, user_id = get_url_to_upload_photo(group_id=group_id, vk_key=vk_key)
    server, photo, photo_hash = upload_photo_on_wall(img_path, upload_url)
    status = save_wall_photo(group_id=group_id, photo=photo, server=server, photo_hash=photo_hash, vk_key=vk_key)
    create_wall_post_in_group(group_id=group_id,
                              message=img_comment,
                              attachments_type='photo',
                              owner_id=status['response'][0]['owner_id'],
                              media_id=status['response'][0]['id'],
                              vk_key=vk_key)

