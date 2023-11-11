
import sys
import os
import hashlib
from pprint import pprint

SLASH = "|"

# -------- Расчёт контрольной суммы для файла --------
def get_file_hash(filename, block_size = 2**20):
    Result = ""
    if not os.path.isfile(filename):
        return Result
    md5 = hashlib.md5()
    try:
        f = open(filename, "rb")
        while True:
            data = f.read(block_size)
            if not data:
                break
            md5.update(data)
        Result = md5.hexdigest()
    except:
        Result = "Cannot read file"
        while len(Result) < 32:
            Result += "_"
    return Result

def help():
    print("compare_by_hash.py [-r|--recursive] [-u|--ignore-unexisted] [-d|--ignore-different] <dir1> <dir2>")
    print("    Print difference for two directories comparing files by its content.")
    print("    -r|--recursive           recursive scan directories")
    print("    -u|--ignore-unexisted    do not print unexisted items")
    print("    -d|--ignore-different    do not print different items")
    print("")


def parse_params(argv):
    params = {}
    params["recursive"] = False
    params["ignore_unexisted"] = False
    params["ignore_different"] = False
    params["sequential"] = []
    for i in range(1, len(argv)):
        a = argv[i]
        if a == "-r":
            params["recursive"] = True
            continue
        if a == "-u" or a == "--ignore-unexisted":
            params["ignore_unexisted"] = True
            continue
        if a == "-d" or a == "--ignore-different":
            params["ignore_different"] = True
            continue
        params["sequential"].append(a)
    return params


# -------- Составить список файлов и каталогов, для файлов вычислить контрольные суммы --------
def build_items_list(root_dir:str, items_list, recursive:bool, do_not_calc_hash:bool, depth:int = 0) -> None:
    raw_items_list = os.listdir(root_dir)
    for item in raw_items_list:
        path = root_dir + SLASH + item
        if os.path.isfile(path):
            hash = ""
            if not do_not_calc_hash:
                hash = get_file_hash(path)
            items_list[path] = hash
        elif os.path.isdir(path):
            items_list[path + SLASH] = ""
            if recursive:
                build_items_list(path, items_list, recursive, depth+1)
    if depth == 0:
        # удалить корневой каталог из всех путей
        pass

# -------- Сравнение двух списков файлов и каталогов --------
def compare_items_list(dir1:str, items1, dir2:str, items2, ignore_different:bool, ignore_unexisted:bool) -> None:
    names1 = list(set(items1))
    names2 = list(set(items2))
    names1.sort()
    names2.sort()
    dir1_length = len(dir1)
    dir2_length = len(dir2)
    #print(dir1_length, names1)
    #print(dir2_length, names2)

    # ----- проход по items1[] -----
    for s1 in names1:
        s1_short = s1[dir1_length+1:]
        s2 = dir2 + SLASH + s1_short
        #print(s1, s1_short, s2)
        if s2 in items2:
            # существует в обоих списках
            if not ignore_different and items1[s1] != items2[s2]:
                print("{}\t<>\t{}" . format(s1, s2))
        else:
            # существует только в первом списке
            if not ignore_unexisted:
                print(s2 + "\t" + "not exists")

    # ----- проход по items2[] -----
    for s2 in names2:
        s2_short = s2[dir2_length+1:]
        s1 = dir1 + SLASH + s2_short
        #print(s1, s1_short, s2)
        if s1 in items1:
            # существует в обоих списках
            # не выводить сообщение о различии, т.к. такое сообщение уже выводилось при сканировании первого списка
            pass
        else:
            # существует только во втором списке
            if not ignore_unexisted:
                print(s1 + "\t" + "not exists")


def do_compare(dir1:str, dir2:str, params) -> bool:
    print("----- compare [{}] and [{}] -----" . format(dir1, dir2))
    if not os.path.isdir(dir1):
        print("Directory [{}] does not exist." . format(dir1))
        return False
    if not os.path.isdir(dir2):
        print("Directory [{}] does not exist." . format(dir2))
        return False
    items1 = {}; build_items_list(dir1, items1, params["recursive"], params["ignore_different"])
    items2 = {}; build_items_list(dir2, items2, params["recursive"], params["ignore_different"])
    pprint(items1)
    #pprint(items2)
    compare_items_list(dir1, items1, dir2, items2, params["ignore_different"], params["ignore_unexisted"])
    return True


if __name__ == "__main__":
    if len(sys.argv) == 1:
        help()
        exit(0)
    params = parse_params(sys.argv)
    #pprint(params)
    if os.path.exists("/etc/passwd"):
        SLASH = "/"
    else:
        SLASH = "\\"
    for i in range(1, len(params["sequential"])):
        do_compare(params["sequential"][i-1], params["sequential"][i], params)