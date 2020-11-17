import codecs
import sys
import os

COMMANDS = ['rep - показывает текущий репозитория',
            'user - показывает имя и почту пользователя',
            'dirs - показывает все файлы в папке .git',
            'file "filename" - показывает содержимое файла',
            'patch "filename" - показывает абсолютный путь к файлу',
            'change "filename" - изменяет текущий репозитория',
            'info - показывает список доступных команд',
            'exit - выход из программы']

SEPARATOR = '\t' + '-' * 50

ERROR_COMMAND_NOT_EXIST = "Вы указали несуществующую команду"
QUANTITY_ARGS = "Вы указали неверное количество аргументов"

REPOS = " "
TAB = '  '


def get_user_inf():
    if not os.path.exists(REPOS + '\\.git'):
        print("Это не git-репозиторий")
        return

    way = REPOS + '\\.git' + '\\config'

    with open(way, 'r') as data:
        data_list = data.read().split('\n')

    for i in range(len(data_list)):

        if data_list[i][0:1] == '\t':
            data_list[i] = data_list[i][1:]
        else:
            data_list[i] = data_list[i]

    inf = {}
    for p in data_list:
        if len(p.split(' = ')) == 1:
            key = p
        else:
            key = p.split(' = ')[0]

        if len(p.split(' = ')) == 1:
            value = None
        else:
            value = p.split(' = ')[1]

        inf[key] = value

    user_name = "Username = "
    if 'name' in inf:
        user_name += inf['name']
    else:
        user_name += "no name"

    user_email = "User email = "
    if 'name' in inf:
        user_email += inf['email']
    else:
        user_email += "no email"

    print(user_name, user_email, sep='\n')


def dirs():
    if not os.path.exists(REPOS + '\\.git'):
        print("Это не git-репозиторий")
        return
    print(REPOS)
    print_dirs(REPOS, 0)


def print_dirs(dir_path, depth):
    for dir_name in os.listdir(dir_path):
        current_path = dir_path + '\\' + dir_name
        print(TAB * depth + ('- ' + dir_name if os.path.isfile(current_path) else dir_name + ":"))
        if os.path.isdir(current_path):
            print_dirs(current_path, depth + 1)


def file(file_name):
    file_path_list = find(REPOS, file_name)
    if len(file_path_list) == 0:
        print("Такого файла нет!")
        return
    print_file_list(file_path_list)


def print_file_list(file_path_list):
    for file_path in file_path_list:
        if type(file_path) is list:
            print_file_list(file_path)
        else:
            print('\t' + file_path)
            if os.path.isdir(file_path):
                print("Это директория!")
            else:
                print(SEPARATOR)
                contents = None
                with open(file_path) as f:
                    for line in f:
                        print(line)


def find(dir_path, file_name):
    result = list()
    for dir_name in os.listdir(dir_path):
        current_path = dir_path + '\\' + dir_name
        if dir_name.split('.')[0] == file_name or dir_name == file_name:
            result.append(current_path)
        if os.path.isdir(current_path):
            t = find(current_path, file_name)
            if len(t) != 0:
                result.append(t)
    return result


def path(name):
    path_list = find(REPOS, name)
    print(SEPARATOR)
    print_path(path_list)


def print_path(path_list):
    for current_path in path_list:
        if type(current_path) is list:
            print_path(current_path)
        else:
            print('\t' + current_path)


def change(path):
    return path


def cur_rep():
    print(REPOS)


def info():
    for com in COMMANDS:
        print(com)


if __name__ == '__main__':
    REPOS = input("Введите путь к папке, содержащей папку .git: ")
    s = ""

    while s != 'exit':
        s = input("Введите команду: ")
        arr = s.split(" ")

        if arr[0] == 'rep':
            cur_rep()
            continue

        if arr[0] == 'user':
            get_user_inf()
            continue

        if arr[0] == 'dirs':
            dirs()
            continue

        if arr[0] == 'file':
            if len(arr) != 2:
                print(QUANTITY_ARGS)
                continue
            file(arr[1])
            continue

        if arr[0] == 'patch':
            if len(arr) != 2:
                print(QUANTITY_ARGS)
                continue
            path(arr[1])
            continue

        if arr[0] == 'change':
            REPOS = change(arr[1])
            continue

        if arr[0] == 'info':
            info()
            continue

        if arr[0] == 'exit':
            sys.exit()
        else:
            print(ERROR_COMMAND_NOT_EXIST)
            continue
