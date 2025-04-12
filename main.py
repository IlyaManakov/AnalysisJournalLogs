import argparse
import os.path


#список столбцов
rows = {'HANDLER': 7, 'DEBUG': 5, 'INFO': 4, 'WARNING': 7, 'ERROR': 5, 'CRITICAL': 8}

#инициализация парсера (команды cli)
def create_parser():
    # список отчетов
    list_report = ['handlers', 'handlers-split']

    parser = argparse.ArgumentParser(description='Log-files reading')
    parser.add_argument('files', type=str, nargs='*', help='names of files')
    parser.add_argument('--report', required=True,
                        choices=list_report,
                        help=f'choice a report type: {", ".join(list_report)}')
    return parser


#функция объединения словарей
def merge_dict(main:dict, slave:dict)->dict:
    global rows
    for k,v in slave.items():
        main[k] = main.get(k, dict.fromkeys(list(rows.keys())[1:], 0))
        try:
            for k2, v2 in v.items():
                main[k][k2] = main[k].get(k2, 0) + v2
        except Exception as e:
            raise TypeError('Ошибка: нет подсловаря у объединяемого элемента')
    return main


#поиск пути до файла
def find_path(lst:list)->str:
    if not isinstance(lst, list):
        raise TypeError('Передан неверный тип данных')
    for i in lst:
        if '/' in str(i):
            return i
    return ''


#чтение файла и сохранение в виде словаря данных
def read_log(path:str)->dict:
    d = {}
    cache = ''

    #обработка пустого пути
    if not os.path.exists(str(path)):
        return d

    with open(path, 'r', encoding='utf-8') as file:
        for s in file:
            mas = s.strip().split()
            status = mas[2]
            if status in ('INFO', 'ERROR'):
                cache = find_path(mas)
            d[cache] = d.get(cache, dict.fromkeys(list(rows.keys())[1:], 0))
            d[cache][status] = d[cache].get(status, 0) + 1
    return d


#вывод результата
def result_out(d_out: dict):
    res = [sum([v[k] for v in d_out.values()]) for k in list(rows.keys())[1:]]

    # табуляция
    rows['HANDLER'] = len(max(list(d_out.keys()) + ['HANDLER'], key=len))
    for i1, i2 in zip(list(rows.items())[1:], res):
        if i1[1] < len(str(i2)):
            rows[i1[0]] = i2

    print(f'Total requests: {sum(res)}')
    [print(k.ljust(v), end='\t') for k, v in rows.items()]
    print()
    [print(*map(lambda x: str(x[1]).ljust(x[0]), zip(list(rows.values()), [k, *v.values()])), sep='\t')
     for k, v in sorted(d_out.items())]
    [print(str(k).ljust(v), end='\t') for v, k in zip(list(rows.values()), ['ИТОГ']+res)]
    print()


#логика обработки отчетов
def process_args(args):
    #раздельные отчеты
    if args.report == 'handlers-split':
        for arg in args.files:
            d = read_log(arg)
            result_out(d)
            total = 0
    #общий отчет
    elif args.report == 'handlers':
        d = {}
        for arg in args.files:
            d = merge_dict(d, read_log(arg))
        result_out(d)


if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()
    process_args(args)

