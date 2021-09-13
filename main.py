import requests
import datetime
from pprint import pprint
import dpath.util
import os
from tqdm import tqdm
from time import sleep
import json



class Vk_downlaod_photo:
    url = 'https://api.vk.com/method/photos.get'

    def get_photos_vk(self, offset=0,):
        user_id = input('Введите ID пользователя, фотографии которого вы хотите импортировать:\n')
        album = input(
            'Введите название альбома (wall, profile или saved), фотографии из которого вы хотите импортировать.\n')
        count = input('Укажите максимальное число фотографий (не более 1000), которых нужно импортировать:\n')
        self.params = {
            'user_id': user_id,
            'access_token': Menu.vk_token,
            'extended': 1,
            'offset': offset,
            'count': count,
            'photo_size': 1,
            'no_service_albums': 0,
            'need_hidden': 0,
            'skip_hidden': 0,
            'v': Menu.api_vk_version,
            'album_id': album
        }

        try:
            imported_json = requests.get(Menu.url_vk, params=self.params)
            imported_json = imported_json.json()

            if int(dpath.util.get(imported_json, "response/count")) == 0:
                print('Фотографий в указанном альбоме не обнаружено!\n')
                return
            else:
                print(
                    f'Всего в профиле указанного пользователя обнаружено {dpath.util.get(imported_json, "response/count")} фото.\n')
                print('Начинаю граббинг фото!\n')

                result_json = []
                list_of_filenames = []
                list_of_sizes = ['z', 'y', 'x', 'm', 's','w']
                for photo in tqdm(dpath.util.get(imported_json, 'response/items'), desc='Photos grabbing'):
                    sleep(.1)
                    finder_status = False
                    for letter in list_of_sizes:
                        for size in photo['sizes']:
                            if dpath.util.get(size, 'type') == letter:
                                file_name = str(dpath.util.get(photo['likes'], 'count')) + '.jpg'
                                if file_name in list_of_filenames:
                                    file_name = str(dpath.util.get(photo['likes'], 'count')) + '_' + str(
                                        datetime.date.today()) + '.jpg'
                                if finder_status:
                                    continue
                                list_of_filenames.append(file_name)
                                Menu.url_dict[file_name] = dpath.util.get(size, 'url')
                                name_dict = {
                                    'file_name': file_name,
                                    'size': letter
                                }
                                result_json.append(name_dict)
                                finder_status = True

                    result_file = open('result.json', 'w+', encoding='utf-8')
                    json.dump(result_json, result_file, ensure_ascii=False, indent=4)
                    result_file.close()
                    print('Отчет о загруженных фотографияк сформирован в файл result.json')
                    print()

                    Menu.choose_resource_for_export(self)
                    return

        except KeyError:
            print(
                'Произошла ошибка. Возможно профиль или альбом закрыт настройками приватности или альбома не существует. '
                'Проверьте правильность написания альбома и его доступность из вашего профиля.\n')
            return


class YandexUploader:
    def yd_upload(self):
        path = Menu.dir_name + '/'
        headers = {'Content-Type': 'application/json', 'Authorization': 'OAuth {}'.format(Menu.yandex_token)}
        for filename, url in tqdm(Menu.url_dict.items(), desc='Photos uploading'):
            sleep(.1)
            params = {'path': path + filename, 'url': url, 'overwrite': 'true', }
            response = requests.post('https://cloud-api.yandex.net/v1/disk/resources/upload', headers=headers,
                                     params=params)
            response.raise_for_status()
            if response.status_code != 202:
                print(f'Не удалось загрузить файл {filename} на Яндекс Диск')


class Menu:
    url_vk = 'https://api.vk.com/method/photos.get'
    api_vk_version = '5.131'
    url_dict = {}
    dir_name = ''
    vk_token = ''
    yandex_token = ''
    service_account_file = 'picsgrabber-114c6c5758b2.json'

    import_resource_dict = {'да': Vk_downlaod_photo.get_photos_vk, 'нет': False}

    def greeting(self):
        print()
        import_resource = input('Выберите ресурс, из  которого хотите импортировать фотографии:\n'
                                'да - Импортировать фото из Вкондакте\n'
                                'нет - Завершить выполнение программы\n')
        if import_resource == 'нет':
            print('Спасибо за использование! До свидания!\n')
            exit()
        elif import_resource in self.import_resource_dict:
            self.import_resource_dict[import_resource](self)
        else:
            print(f'Команды {import_resource} не существует.\n')

    export_resource_dict = {'да': YandexUploader.yd_upload, 'нет': False}

    def choose_resource_for_export(self):
        export_resource = input('Выберите ресурс, в который хотите экспортировать фотографии:\n'
                                'да - Импортировать фото в Yandex Disc\n'
                                'нет - Завершить выполнение программы\n')
        if export_resource == 'нет':
            print('Спасибо за использование! До свидания!\n')
            exit()
        elif export_resource in self.export_resource_dict:
            self.export_resource_dict[export_resource](self)
        else:
            print(f'Команды {export_resource} не существует.\n')

if __name__ == '__main__':
    my_menu = Menu()
    my_vk_grabber = Vk_downlaod_photo()
    my_yandex_uploader = YandexUploader()
    while True:
        my_menu.greeting()


