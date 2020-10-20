import json
import random
import hashlib
import os.path

"'"
{
    "b": [],
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
    "a": ["b", "c", "d"],
    "b": [],
    "c": ["d"],
    "d": [],
    "e": ["g", "f", "q"],
    "g": [],
    "f": [],
    "q": []
}

from collections import deque

GRAY, BLACK = 0, 1
BD_NAME = "bd.txt"
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


def download_package(package_name):
    f = open(BD_NAME, "wr")
    js_doc = json.loads(f.read())
    dep = js_doc.get(package_name)
    deps = dep.get(DEP)
    hash = dep.get(HASH);

    if os.path.exists(package_name + TEST_EXPANSION):
        print("Существует")
        return
    else:
        if len(deps) != 0:
            for dep_name in deps:
                download_package(dep_name)
        file = open(package_name + TEST_EXPANSION, "w")
        inf = str(random.random())
        for char in inf:
            file.write(char)


if __name__ == '__main__':
    print(init_bd(graph2))
    download_package("a")
