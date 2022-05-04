import requests
import time
import json

class VK_users:
    with open('token.txt', 'r') as file_token:
        vk_token = file_token.read().strip()
    url = 'https://api.vk.com/method/'
    def __init__(self, version):
        self.params = {'access_token': self.vk_token,
                       'v': version}

    def get_photos(self, user_id):
        # Получаем json файл с данными по пяти фотографий пользователя
        url_get_photos = self.url + 'photos.get'
        get_params = {'extended': '1', 'owner_id': user_id, 'album_id': 'profile', 'count': '5'}
        res = requests.get(url_get_photos, params={**self.params, **get_params}).json()
        res = res['response']['items']
        return res

    def get_max_size(self, res):
        # Ищем максимальное расширение фотографий в json файле
        i = 0
        max_list1 = []
        while i < len(res):
            max_dict = {}
            lname = str(res[i]['likes']['count'])
            dname = str(res[i]['date'])
            for photo in res[i]['sizes']:
                type = photo['type']
                url = photo['url']
                max_dict.update({photo['height'] * photo['width']: [{'lname': lname},\
                                {'dname': dname}, {'type': type}, {'url': url}]})
                best_photo = max(max_dict.items(), key=lambda x: x[0])
            i += 1
            max_list1.append(best_photo)
        return max_list1

    def json_photos_file(self):
        temp = {'file_name': '0',
             'size': '0'}
        json_file = []
        url_to_download = []
        i = 0
        while i < len(max_list):
            lname = str(max_list[i][1][0]['lname'])
            dname = str(max_list[i][1][1]['dname'])
            size = max_list[i][1][2]['type']
            url = max_list[i][1][3]['url']
            if str(lname) not in temp['file_name']:
                temp1 = {'file_name': str(lname) + '.jpg', 'size': size}
                temp2 = {'file_name': str(lname) + '.jpg', 'url': url}
                temp.update(temp1)
                json_file.append(temp1)
                url_to_download.append(temp2)
            elif lname in temp['file_name']:
                temp1 = {'file_name': str(dname) + '.jpg', 'size': size}
                temp2 = {'file_name': str(dname) + '.jpg', 'url': url}
                temp.update(temp1)
                json_file.append(temp1)
                url_to_download.append(temp2)
            i += 1
        return [url_to_download, json_file]

    def create_json_file(self):
        res = self.json_photos_file()
        with open('photo.json', 'w', encoding='utf-8') as outfile:
            json.dump(res[1], outfile)


class YaUploader:
    def __init__(self, token: str):
        self.token = token

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token)
                }

    def add_folder(self):
        # Добавляем папку в корневой каталог Яндекс.Диск
        put_folder_url = "https://cloud-api.yandex.net/v1/disk/resources"
        headers = self.get_headers()
        params = {"path": "py-52"}
        response = requests.put(put_folder_url, headers=headers, params=params)
        return response

    def get_upload_link(self, yadisk_file_path: str):
        # Получаем ссылку на размещение файла в папке py-52 на Яндекс.Диск
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        headers = self.get_headers()
        params = {"path": "py-52/" + yadisk_file_path, "overwrite": "true"}
        response = requests.get(upload_url, headers=headers, params=params)
        # pprint(response.json())
        return response.json()

    def upload(self, url_and_json):
        # Загружаем фотографии максимального разрешения на
        # Яндекс.Диск по средствам ссылок из VK
        i = 0
        while i < len(url_and_json[0]):
            print(f"Записть фотографии {url_and_json[1][i]['file_name']} на Яндекс.Диск ({i + 1}/5)")
            href_json = self.get_upload_link(yadisk_file_path=url_and_json[1][i]['file_name'])
            href = href_json['href']
            response = requests.put(href, url_and_json[0][i]['url'])
            response.raise_for_status()
            if response.status_code == 202:
                print('Success')
            time.sleep(0.33)
            i += 1
        print('Запись файла с данными о фотографиях на Яндекс.Диск')
        href_json = self.get_upload_link(yadisk_file_path='photo.json')
        href = href_json['href']
        response = requests.put(href, data=open('photo.json', 'rb'))
        response.raise_for_status()
        if response.status_code == 202:
            print('Success')


if __name__ == '__main__':
    id_vk_user = input('Введите id пользователя VK: ')
    ya_token = input('Введите токе с полигона Яндекс.Диска: ')

    VK_user = VK_users('5.131')
    max_list = VK_user.get_max_size(VK_user.get_photos(id_vk_user))
    url_and_json = VK_users.json_photos_file(max_list)
    VK_user.create_json_file()

    Ya_uploader = YaUploader(token=ya_token)
    Ya_uploader.add_folder()
    Ya_uploader.upload(url_and_json)





