import requests


def request_to_vk_api_post(method, parameters, access_token, v='5.130'):
    url = f'https://api.vk.com/method/{method}'
    data = {
        'access_token': access_token,
        'v': v
    }
    data.update(parameters)
    response = requests.post(url=url, data=data)
    # Если от вк придет ответ отличный от 200 - могли ошибиться в url или еще что-то, то сработает raise_for_status
    response.raise_for_status()
    response_jsonify = response.json()
    # Если ошибка в теле запроса - обработаем вручную
    if 'error' in response_jsonify.keys():
        raise ConnectionError(f'{response_jsonify["error"]}')
    return response_jsonify


def get_url_to_upload_photo(group_id, my_vk_key):
    method = 'photos.getWallUploadServer'
    parameters = {'group_id': group_id}
    response = request_to_vk_api_post(method=method, parameters=parameters, access_token=my_vk_key)
    return response['response']['upload_url'], response['response']['album_id'], response['response']['user_id']


def upload_photo_on_wall(image_path, upload_url):
    with open(image_path, 'rb') as file:
        parameters = {
            'photo': file,
            'content_type': 'multipart/form-data'
        }
        response = requests.post(url=upload_url, files=parameters)
        response.raise_for_status()
        response_jsonify = response.json()
        # Если пришел пустой массив с фото - значит где-то ошибка
        if 'photo' in response_jsonify.keys() and response_jsonify['photo'] == "[]":
            raise ValueError(f'photo is empty: {response_jsonify}')
    return response_jsonify['server'], response_jsonify['photo'], response_jsonify['hash']


def save_wall_photo(group_id, photo, server, hash, my_vk_key):
    method = 'photos.saveWallPhoto'
    parameters = {
        'group_id': group_id,
        'photo': photo,
        'server': server,
        'hash': hash
    }
    response = request_to_vk_api_post(method=method, parameters=parameters, access_token=my_vk_key)
    return response


def create_wall_post_in_group(group_id, message, attachments_type, owner_id, media_id, my_vk_key):
    method = 'wall.post'
    parameters = {
        'owner_id': f'-{group_id}',
        'from_group': 1,
        'message': message,
        'attachments': f'{attachments_type}{owner_id}_{media_id}'
    }
    response = request_to_vk_api_post(method=method, parameters=parameters, access_token=my_vk_key)
    return response


def create_post_on_group_wall(group_id, current_img, my_vk_key):
    upload_url, album_id, user_id = get_url_to_upload_photo(group_id=group_id, my_vk_key=my_vk_key)
    server, photo, hash = upload_photo_on_wall(current_img['path'], upload_url)
    status = save_wall_photo(group_id=group_id, photo=photo, server=server, hash=hash, my_vk_key=my_vk_key)
    create_wall_post_in_group(group_id=group_id,
                              message=current_img['comment'],
                              attachments_type='photo',
                              owner_id=status['response'][0]['owner_id'],
                              media_id=status['response'][0]['id'],
                              my_vk_key=my_vk_key)

