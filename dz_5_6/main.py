import json
import random
import hashlib
import os.path

"'"
{
    "b": {
        "com":["@echo \"Putting on socks."],
        "dep":[]
    },
    "b": {
        "com": ["@echo \"Putting on socks."],
        "dep": []
    },
    "b": {
        "com": ["@echo \"Putting on socks."],
        "dep": []
    },
    "f": [],
    "d": [],
    "g": [],
    "q": [],
    "c": ["d"],
    "e": ["g", "f", "q"],
    "a": ["b", "c", "d"]
}
"'"

# 2 components
graph2 = {
    "a": {
        "com":["@echo \"Putting on socks.\""],
        "dep":["b", "c", "d"]
    },
    "b": {
        "com": ["@echo \"Putting on socks.\""],
        "dep": []
    },
    "c": {
        "com": ["@echo \"Putting on socks.\""],
        "dep": ["d"]
    },
    "d": {
        "com": ["@echo \"Putting on socks.\""],
        "dep": []
    },
    "e": {
        "com": ["@echo \"Putting on socks.\""],
        "dep": ["g", "f", "q"]
    },
    "g": {
        "com": ["@echo \"Putting on socks.\""],
        "dep": []
    },
    "f": {
        "com": ["@echo \"Putting on socks.\""],
        "dep": []
    },
    "q": {
        "com": ["@echo \"Putting on socks.\""],
        "dep": []
    },
}

from collections import deque

GRAY, BLACK = 0, 1
BD_NAME = "bd.json"
TEST_EXPANSION = ".file"
DEP = "dep"
HASH = "hash"


# Код для топологической сортировки взят с https://gist.github.com/kachayev/5910538;
def init_bd(graph):
    order, enter, state = deque(), set(graph), {}

    def dfs(node):
        state[node] = GRAY
        for k in graph.get(node, ()):
            sk = state.get(k, None)
            if sk == GRAY: raise ValueError("cycle")
            if sk == BLACK: continue
            enter.discard(k)
            dfs(k)
        order.appendleft(node)
        state[node] = BLACK

    def infile():
        bd = "{\n"
        jsdoc = json.loads(json.dumps(graph2))

        # Пересобираем json с учётом топол. сорт.
        for key_json in order:
            dict_json = jsdoc.get(key_json)
            dep = str(dict_json)
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
    with open(BD_NAME) as f:
        data = json.load(f)

    deps = data[package_name][DEP]
    hash = data[package_name][HASH]

    def add_hash(inf):
        # Добавляем хэш
        with open(BD_NAME, 'r') as f:
            data = json.load(f)
        with open(BD_NAME, 'w') as write_file:
            hash_object = hashlib.md5(inf.encode())
            data[package_name][HASH] = hash_object.hexdigest()
            json.dump(data, write_file, indent=4)

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
    init_bd(graph2)
    need = []
    inp = input().split(' ')

    while inp[0]!= "0":
        if inp[0] == "show":
            show()

        if inp[0] == "make":
            pack_name = inp[1]
            download_package(pack_name, need)
            if need[0] == pack_name:
                need = need[1:]

                if len(need) == 0:
                    print(pack_name + "is already updated")
                else:
                    for i in need:
                        print(i)

        inp = input().split(' ')

