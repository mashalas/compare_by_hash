# compare_by_hash
Сравнить содержимое двух каталогов. Вывести файлы, которые различаются по содержимому или файлы/подкаталоги существующие в одном каталоге, но отсутствующие в другом.

Формат запуска:
~~~
compare_by_hash.py [options] <dir1> <dir2>
    -h|--help                  print this help
    -r|--recursive             recursive scan directories
    -u|--ignore-unexisted      do not print unexisted items
    -d|--ignore-different      do not print different items
    -s|--skip-once=<item>      do not enter to the directory or not compare the file
    -S|--skip-from=<filename>  read skiping items (directories and files) from the file
~~~
