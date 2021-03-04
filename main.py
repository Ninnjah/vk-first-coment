# -*- coding: utf-8 -*-

import os
import time
import json
import urllib
from datetime import datetime as dt
import vk_api


def get_id(link):
    '''
    Извлекает ID пользователя из ссылки на его профиль link
    
    link = ссылка на профиль пользователя(строка)
    '''
    
    return link.strip('/')[-1]


def get_token():
    '''
    Берет ТОКЕН с разрешением на отправку сообщений через приложение
    Возвращает этот ТОКЕН
    При неудаче возвращает False
    '''
    username = input('Введите логин: ')
    password = input('Введите пароль: ')
    url = "https://oauth.vk.com/token?grant_type=password&client_id=3697615&client_secret=AlVXZFMUqyrnABp8ncuU&username=%s&password=%s" % (username, password)

    try:
        TOKEN = urllib.request.urlopen(url).read()
        TOKEN = json.loads(TOKEN)['access_token']
        return TOKEN
    except urllib.error.HTTPError as err:
        if err.code == 401:
            print('!!! Неверный логин или пароль !!!')
        elif err.code == 404:
            print('!!! Связь с сервером не установлена !!!')
        else:
            print('!!! ОШИБКА !!!')
        return False


def text_edit():
    '''
    Принимает текст от пользователя 
    пока он не введет 'done'
    
    возвращает список строк
    '''
    TEXT = []
    print('-'*48)
    print(' Для выхода введи "done"\n',
          'Для ввода всего текста заного введи "retry"\n',
          '-'*48)
    
    while True:
        cmd = input()
        if cmd == 'retry':
            if input('Начать ввод текста заного? (y/n): ') in 'Yy':
                text_edit()
        elif cmd == 'done':
            break
        else:
            TEXT.append(cmd)
    
    return TEXT


def set_message():
    '''
    Запускает редктор текста и преобразовывает полученный список в
    строку с переходом на новую линию перед каждым элементом списка
    кроме последнего
    '''
    os.system('cls||clear')
    print('\nВвод сообщения для рассылки')
    MESSAGE = ''
    TEXT = text_edit()
    config_file = os.path.join(os.getcwd(), 'config.json')
    
    for index, line in enumerate(TEXT):
        if index != len(TEXT) - 1:
            MESSAGE += line + '\n'
        else:
            MESSAGE += line
    
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as read_file:
            data = json.load(read_file)
            
        data = {
                'message' : MESSAGE,
                'ids'     : data['ids'],
                'delay'   : data['delay'],
        }
        with open(config_file, 'w', encoding='utf-8') as write_file:
            write_file.write(json.dumps(data))
    
    return MESSAGE


def set_id():
    '''
    Запускает редактор для ввода ссылок профилей пользователей ВК
    Вернет список состоящий только из id пользователей
    '''
    os.system('cls||clear')
    print('\nВвод ссылок профилей ВК')
    IDS_LINKS = text_edit()
    IDS = []
    config_file = os.path.join(os.getcwd(), 'config.json')
    
    for id in IDS_LINKS:
        IDS.append(vk.users.get(users_id=get_id(id))[0]['id'])
    
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as read_file:
            data = json.load(read_file)
            
        data = {
                'message' : data['ids'],
                'ids'     : IDS,
                'delay'   : data['delay'],
        }
        with open(config_file, 'w', encoding='utf-8') as write_file:
            write_file.write(json.dumps(data))
    return IDS


def check_config():
    '''
    Проверяет существование конфиг файла и берет данные если он есть
    возвращает словарь с данными из конфиг файла если он есть
    если его нет то возвращает словарь дефолтными значениями
    '''
    config_file = os.path.join(os.getcwd(), 'config.json')
    
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as read_file:
            data = json.load(read_file)
        return data
    else:
        data = {
                'message' : set_message(),
                'ids'     : set_id(),
                'delay'   : 1,
        }
        with open(config_file, 'w', encoding='utf-8') as write_file:
            write_file.write(json.dumps(data))
        
        return data


def send(id_):
    '''
    Отправляет сообщение пользователю ВК с проверкой капчи
    id_ = индекс ID пользователя в списке
    '''
    vk_id = IDS[id_]
    
    try:
        vk.messages.send(
            user_id=vk_id,
            message=MESSAGE,
            random_id=0
        )
    except vk_api.exceptions.Captcha as captcha:
        print('Ошибка!\nВылезла капча..')
        
        captcha.sid
        with open('captcha.png', 'wb') as img:
            img.write(captcha.get_image())
        os.system('captcha.png')
        
        key = ''
        while key == '':
            key = input('Введите ответ: ')
        
        captcha.try_again(key)


if __name__ == '__main__':

    TOKEN_PATH = os.path.join(os.getcwd(), 'token.dat')

    # Получаем ТОКЕН доступа
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'r') as token_file:
            TOKEN = token_file.read()
        print('Токен был загружен!\n')
    else:
        while True:
            TOKEN = get_token()
            if not TOKEN:
                pass
            else:
                break
        if input('Сохранить токен? (y/n): ') in 'Yy':
            with open(TOKEN_PATH, 'w') as token_file:
                token_file.write(TOKEN)
            print('Токен был загружен!\n')

    # Запускаем сессию ВК
    vk = vk_api.VkApi(token=TOKEN).get_api()
    
    data = check_config()
    
    DELAY = data['delay']
    MESSAGE = data['message']
    IDS = data['ids']
    
    cmd = ''
    while cmd != 'start':
        os.system('cls||clear')
        print('Команды :\n', 
              '!token - Удаление токена\n',
              '!message - Запись сообщения\n',
              '!id - Запись ссылок профилей\n',
              'start - для начала\n',
              '-' * 32)
        cmd = input('Введи команду: ')
        
        if cmd == '!token':
            if input('Удалить ТОКЕН доступа? (y/n): ') in 'Yy':
                os.remove(os.path.join(os.getcwd(), 'token.dat'))
                print('ТОКЕН успешно удален!')
        elif cmd == '!message':
            MESSAGE = set_message()
        elif cmd == '!id':
            IDS = set_id()
    
    
    # Вводим время начала рыссылки
    while True:
        start_time = input('Введите время начала рассылки в формате "ЧЧ:ММ": ')
        if start_time == '':
            start_time = dt.timestamp(
                dt.combine(dt.date(dt.now()), 
                            dt.time(dt.strptime('0:00', '%H:%M')))
                            )
            break
        try:
            start_time = dt.timestamp(
                dt.combine(dt.date(dt.now()), 
                            dt.time(dt.strptime(start_time, '%H:%M'))
                            )
                )
            break
        except ValueError:
            print('Неверный формат!')

    print('Ожидаем начала рассылки..', end='\r')
    while dt.timestamp(dt.now()) < start_time:
        time.sleep(1)

    print('Рассылка началась!       \n----------------\n')
    for i in range(len(IDS)):
        time.sleep(DELAY)
        send(i)
        print(f'сообщение {i + 1} отправлено..')
    input('Сообщения были доставлены!')
