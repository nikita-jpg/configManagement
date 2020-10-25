import json
import random
import hashlib
import os


from collections import deque

GRAY, BLACK = 0, 1
BD_NAME = "bd.json"
TEST_EXPANSION = ".file"
DEP = "dep"
COM = "com"
HASH = "hash"
MAKE_FILE = "Makefile"
MAKE_FILE_LOCAL = "Makefile_Local"

# Добавляет к обычному json поле для команды
def refactor_json_to_myJson():
    with open(MAKE_FILE + TEST_EXPANSION,'r') as f:
        data = json.load(f)
        str = "{"+\
              "\"com\":[], "+\
              "\"dep\":"

        for name in data:
            #Достаём элементы
            s = "["
            for dep in data[name]:
                s += "'" + dep + "'" + ","
            if s!= "[":
                s = s[:-1]
            s+="]"
            data[name] = str + s + "}"
            i = 4

    with open(MAKE_FILE_LOCAL+TEST_EXPANSION, 'w') as write_file:
        json.dump(data, write_file)

    file = ""
    with open(MAKE_FILE + "_LOCAL" + TEST_EXPANSION, 'r') as f:
        file = f.read()
    file = file.replace("\"{","{")
    file = file.replace("}\"", "}")
    file = file.replace("'","\"")
    file = file.replace("\\","")
    with open(MAKE_FILE + "_LOCAL" + TEST_EXPANSION, 'w') as f:
        f.write(file)

    return

# Код для топологической сортировки взят с https://gist.github.com/kachayev/5910538;
def init_bd(graph):
    order, enter, state = deque(), set(graph), {}

    def dfs(node):
        state[node] = GRAY
        q = graph.get(node, ())

        # Топологическая сортировка
        for k in q.get(DEP):
            sk = state.get(k, None)
            if sk == GRAY: raise ValueError("cycle")
            if sk == BLACK: continue
            enter.discard(k)
            dfs(k)

        order.appendleft(node)
        state[node] = BLACK

    def infile():
        bd = "{\n"
        jsdoc = json.loads(json.dumps(graph))

        # Пересобираем json с учётом топол. сорт.
        for key_json in order:
            dict_json = jsdoc.get(key_json)
            dep = str(dict_json.get(DEP))
            dep = dep.replace("'", "\"")
            bd += "    \"" + \
                  key_json + \
                  "\"" + \
                  ": {\n" + \
                  "        \""+HASH+"\": "+\
                  "\"\"" \
                  ",\n        "+ \
                  "\""+DEP+"\": "+ \
                  dep + \
                  "\n    },\n"

        bd = bd[0:-2]
        bd += "\n}"

        # Пишем в файл
        f = open(BD_NAME, "w")
        for char in bd:
            f.write(char)
        return bd

    while enter: dfs(enter.pop())
    order.reverse()
    return infile()

def download_package(package_name,need):

    # Выполняем консольные команды
    with open(MAKE_FILE + TEST_EXPANSION,'r') as f:
        data = json.load(f)
        for com in data[package_name][COM]:
            os.system(com)

    with open(BD_NAME) as f:
        data = json.load(f)

    deps = data[package_name][DEP]
    hash = data[package_name][HASH]

    def add_hash(inf):

        with open(BD_NAME, 'r') as f:
            data = json.load(f)
        with open(BD_NAME, 'w') as f:
            hash_object = hashlib.md5(inf.encode())
            data[package_name][HASH] = hash_object.hexdigest()
            json.dump(data, f, indent=4)

    if os.path.exists(package_name + TEST_EXPANSION):
        with open(package_name + TEST_EXPANSION, "r") as f:
            inf = f.read()
            hash_object = hashlib.md5(inf.encode())
            file_hash = hash_object.hexdigest()
        if file_hash != hash :
            add_hash(inf)
            need.append(package_name)
        for dep_name in deps:
             download_package(dep_name,need)

        return
    else:
        need.append(package_name)
        if len(deps) != 0:
            for dep_name in deps:
                download_package(dep_name,need)

        #Пишем в файл рандомное число
        with open(package_name + TEST_EXPANSION, "w") as f:
            inf = str(random.random())
            for char in inf:
                f.write(char)

        add_hash(inf)
        # Добавляем хэш
        return

def show():
    with open(BD_NAME,'r') as f:
        data = json.load(f)
    for key in data:
        print(key)


if __name__ == '__main__':

    #refactor_json_to_myJson()
    with open(MAKE_FILE+TEST_EXPANSION,'r') as f:
        data = json.load(f)
    init_bd(data)
    need = []
    inp = input().split(' ')

    while inp[0]!= "0":
        if inp[0] == "show":
            show()

        if inp[0] == "make":
            pack_name = inp[1]
            download_package(pack_name, need)

            if len(need) == 0:
                print(pack_name + " is already updated")
            else:
                if need[0] == pack_name:
                    need = need[1:]
                    for i in need:
                        print(i)

        if inp[0] == "del":
            os.remove(inp[1]+TEST_EXPANSION)
        if inp[0] == "clear":
            with open(BD_NAME,'r') as f:
                data = json.load(f)

            for name in data:
                os.remove(name+TEST_EXPANSION)

        need = []
        inp = input().split(' ')

