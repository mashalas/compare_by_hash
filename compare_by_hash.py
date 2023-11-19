
import sys
import os
import hashlib
from pprint import pprint
import arg_parse as ap

global_SLASH = "|"

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

# -------- help --------
def help():
    print("compare_by_hash.py [options] <dir1> <dir2>")
    print("    Print difference for two directories comparing files by its content.")
    print("    options:")
    print("    -h|--help                  print this help")
    print("    -r|--recursive             recursive scan directories")
    print("    -u|--ignore-unexisted      do not print unexisted items")
    print("    -d|--ignore-different      do not print different items")
    print("    -s|--skip-once=<item>      do not enter to the directory or not compare the file")
    print("    -S|--skip-from=<filename>  read skiping items (directories and files) from the file")

# -------- Разбор аргументов командной строки --------
def arg_parse(argv):
    #argv = argv.copy() # создать новый массив, поэтому наружу не пойдёт удаление элементов
    #argv = argv[1:len(argv)] # создать новый массив, поэтому наружу не пойдёт удаление элементов; имя скрипта не учитывать как аргумен командной строки
    argv = ap.split_short_arguments(argv)
    params = {}
    if len(argv) == 0:
        # не указаны аргументы командной строки
        params["help"] = True
        return params
    if ap.check_arg(argv, params, "help", ["-h", "--help"], logical=True):
        # если запрошена справка, дальнейший разбор не производить, т.к. будет выводиться только справка по программе
        return params
    #print("ARGV:", argv)
    ap.check_arg(argv, params, "recursive",         ["-r", "--recursive"],          logical=True)
    ap.check_arg(argv, params, "ignore-unexisted",  ["-u", "--ignore-unexisted"],   logical=True)
    ap.check_arg(argv, params, "ignore-different",  ["-d", "--ignore-different"],   logical=True)
    ap.check_arg(argv, params, "skip-once",         ["-s", "--skip-once"],          multiple=True)
    ap.check_arg(argv, params, "skip-from",         ["-S", "--skip-from"],          multiple=True)
    #print(argv)
    params["sequential"] = argv.copy() # последовательные (не именованные параметры)
    return params

# -------- Составить список файлов и каталогов, для файлов вычислить контрольные суммы --------
def build_items_list(root_dir:str, items_list, skips, recursive:bool, do_not_calc_hash:bool, depth:int = 0) -> None:
    raw_items_list = os.listdir(root_dir)
    for item in raw_items_list:
        if item in skips:
            continue
        path = root_dir + global_SLASH + item
        if os.path.isfile(path):
            hash = ""
            if not do_not_calc_hash:
                hash = get_file_hash(path)
            items_list[path] = hash
        elif os.path.isdir(path):
            items_list[path + global_SLASH] = ""
            if recursive:
                build_items_list(path, items_list, skips, recursive, do_not_calc_hash, depth+1)

# -------- Сравнение двух списков файлов и каталогов --------
def compare_items_list(dir1:str, items1, dir2:str, items2, ignore_different:bool, ignore_unexisted:bool) -> None:
    #names1 = list(set(items1))
    #names2 = list(set(items2))
    names1 = list(items1.keys())
    names2 = list(items2.keys())
    names1.sort()
    names2.sort()
    dir1_length = len(dir1)
    dir2_length = len(dir2)
    #print(dir1_length, names1)
    #print(dir2_length, names2)

    # ----- проход по items1[] -----
    for s1 in names1:
        s1_short = s1[dir1_length+1:]
        s2 = dir2 + global_SLASH + s1_short
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
        s1 = dir1 + global_SLASH + s2_short
        #print(s1, s1_short, s2)
        if s1 in items1:
            # существует в обоих списках
            # не выводить сообщение о различии, т.к. такое сообщение уже выводилось при сканировании первого списка
            pass
        else:
            # существует только во втором списке
            if not ignore_unexisted:
                print(s1 + "\t" + "not exists")

# -------- Выполнить сравнение двух каталогов --------
def do_compare(dir1:str, dir2:str, params) -> bool:
    print("----- compare [{}] and [{}] -----" . format(dir1, dir2))
    if not os.path.isdir(dir1):
        print("Directory [{}] does not exist." . format(dir1))
        return False
    if not os.path.isdir(dir2):
        print("Directory [{}] does not exist." . format(dir2))
        return False
    items1 = {}; build_items_list(dir1, items1, params["skips"], params["recursive"], params["ignore-different"])
    items2 = {}; build_items_list(dir2, items2, params["skips"], params["recursive"], params["ignore-different"])
    #pprint(items1)
    #pprint(items2)
    compare_items_list(dir1, items1, dir2, items2, params["ignore-different"], params["ignore-unexisted"])
    return True

# -------- Удалить комментарий начнающийся с символа comment_symbol --------
def remove_comment(s:str, comment_symbol:str = "#") -> str:
    p = s.find(comment_symbol)
    if p >= 0:
        s = s[0:p]
    return s

# -------- Строки файла (кроме комментариев) добавить к уже переданным в ExistedItems --------
def append_file_contents_to_array(filename, existed_items, comment_symbol = "#") -> None:
    f = open(filename, "rt")
    for s in f:
        s = s.strip()
        s = remove_comment(s, comment_symbol)
        if len(s) == 0:
            continue
        existed_items.append(s)
    f.close()

# -------- Если указаны исключаемые параметры (одиночный файл/каталог и файл со списком исключаемых), то заполнить параметр params["skips"] --------
def fill_skips(params) -> None:
    params["skips"] = []
    if len(params["skip-once"]) > 0:
        # указаны файлы или каталоги, которые игнорировать
        params["skips"] = params["skip-once"].copy()
    if len(params["skip-from"]) > 0:
        # указаны файлы, из которых прочитать список игнорируемые файлов и каталогов
        for sk in params["skip-from"]:
            if os.path.isfile(sk):
                append_file_contents_to_array(sk, params["skips"])
            else:
                print("WARNING! File [{}] not found." . format(sk))
    params["skips"] = list(set(params["skips"])) # оставить только уникальные значения
    params["skips"].sort() # сортировать


# -------- Какой слеш "/" или "\" на данной платформе --------
def detect_slash() -> str:
    if os.path.exists("/etc/passwd"):
        return "/"
    return "\\"

# --------------------------------- main -------------------------------------
if __name__ == "__main__":
    if len(sys.argv) == 1:
        # не указаны аргументы командной строки - вывести справку
        help()
        exit(0)
    
    global_SLASH = detect_slash()
    params = arg_parse(sys.argv)
    #print(sys.argv)
    if params["help"]:
        # явно запрошена справка
        help()
        exit(0)
    fill_skips(params)
    #pprint(params); exit(0)
    for i in range(1, len(params["sequential"])):
        do_compare(params["sequential"][i-1], params["sequential"][i], params)