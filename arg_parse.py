
global_ARGUMENTS_STARTS_SINCE = 1 # 0=имя скрипта, 1,2,3,...=аргументы командной строки
global_YES_VALUES   = ["1", "yes", "true"]
global_FALSE_VALUES = ["0", "no",  "false"]


# -------- разделить короткие объединённые параметры вида -la на -l -a --------
# -------- вернуть список разделённых аргументов --------
def split_short_arguments(argv, since = global_ARGUMENTS_STARTS_SINCE):
    argv_splited = []
    for i in range(since, len(argv)):
        a = argv[i]
        if len(a) >= 3 and a[0] == "-" and a[1] != "-" and a.find("=") == -1:
            # сначала "-", потом одна или больше букв, символа равенства нет - выделить каждую букву в отдельный параметр
            for j in range(1, len(a)):
                argv_splited.append("-" + a[j])
            continue
        argv_splited.append(a)
    return argv_splited

# -------- Установить значение параметра (если массив - добавить в список, если скаляр - перезаписать) --------
def set_param(params, param_name, param_value):
    if type(params[param_name]) == type([]):
        # массив
        params[param_name].append(param_value)
    else:
        # скаляр
        params[param_name] = param_value

# -------- Проверка наличия аргумента командной строки (argv - список разделённых аргументов) --------
def check_arg(
        argv, 
        params, 
        param_name, 
        names_list, 
        logical:bool = False, # логический флаг, если просто указан - True
        multiple:bool = False,  # параметр может содержать несколько значений
        default:any = "", # значение по умолчанию, если не указан в аргументах командной строки
        mandatory:bool = False, # обязательный параметр, генерировать исключение, если не указан
        scan_since = 0 # сканировать аргументы начиная с указанной позиции
):
    if type(names_list) == type("stroka"):
        names_list = [names_list]

    #if multiple and param_name not in params:
    #    # это множественный параметр и он ещё не был определён - создать пустой масси
    #    params[param_name] = []

    if param_name not in params:
        # этот параметр ещё не был определён
        if multiple:
            params[param_name] = []
        else:
            if logical and default == "":
                default = False
            params[param_name] = default
    
    found_count = 0
    found = True
    while found:
        found = False
        value = None
        for i in range(scan_since, len(argv)):
            a = argv[i]
            for name in names_list:
                if a == name:
                    found = True
                    # текущий пользовательский параметр совпадает с именем проверяемого параметра
                    if logical:
                        # это логический флаг - значит включение этого флага
                        value = True
                        #set_param(params, param_name, True)
                        argv.pop(i)
                        #return True
                        break
                    else:
                        # это не логический флаг - значит значение в следующем пользовательском параметре (если есть)
                        if i < len(argv)-1:
                            # есть ещё последующие элементы
                            value = argv[i+1]
                            #set_param(params, param_name, argv[i+1])
                            argv.pop(i)
                            argv.pop(i) # тот элемент, который был i+1 после удаления i стал тоже i
                            #return True
                            break
                        else:
                            # нет следующего аргумента командной строки
                            raise Exception("value for argument [{}] not specified" . format(a))
                if len(a) > len(name)+1 and a[0:len(name)+1] == name+"=":
                    # после имени параметра есть знак равенства, получить значение после знака равенства
                    found = True
                    value = a[len(name)+1:len(a)]
                    if logical:
                        # если это логический флаг, то может быть указано значение TRUE: 1, yes, true;  FALSE: 0, no, false
                        if value.lower() in global_YES_VALUES:
                            value = True
                        elif value.lower() in global_FALSE_VALUES:
                            value = False
                        else:
                            raise Exception("invalid value [{}] for logical option [{}]" . format(value, param_name))
                    #set_param(params, param_name, value)
                    argv.pop(i)
                    #return True
                    break
            if value != None:
                found = True
                break
        if found:
            # найдено совпадение
            found_count += 1
            set_param(params, param_name, value)
    if mandatory and found_count == 0:
        # указанный параметр не был задан в аргументах командной строки
        raise Exception("Mandatory argument: [{}] not specified." . format(",".join(names_list)))
    return found_count > 0

