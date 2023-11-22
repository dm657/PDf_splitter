import os
import sys
from funcs_for_split_pdf import (split_by_flights, split_by_programs, split_by_programs_nums,
                                 split_by_page_numbers, PDFFiles)

GREETING = ['\nУпс. PDF файлов в папке с программой не найдено',
            '\nНайден 1 PDF файл: {}',
            '\nНайдено несколько PDF файлов:\n{}']
INSTRUCTION = ('Enter - разбить по программам, '
               'номера рейсов - фильтр по рейсам, '
               '-p - фильтр по программам, -m - ручной ввод страниц, -q - выход\n')
HELP = ('Программа для извлечения определенных страниц из PDF документа\n'
        'Enter - для разбиения по программам. результат сохраняется в "results/by_programs" по умолчанию, или в путь, '
        'прописанный в "cfg.json"(в пути следует использовать прямой слэш "/"\n'
        'Номер рейса(или номера через запятую) -  сохранение в файл указанных рейсов\n'
        '  -p - сохранение в файл указанных программ\n'
        '  -m - Сохранение в файл указанных страниц(любого PDF документа)\n'
        'При извлечении программ или страниц "/" служит разделителем на файлы, "-" - для обозначения интервалов\n'
        'К примеру "-p 1-3 10/ 12,15 18-20 создаст 2 файла с указанными программами (для каждого найденного PDF)\n')
dir_name = os.path.dirname(sys.argv[0])

pdf_files = tuple(PDFFiles(dir_name))
greeting = f'{GREETING[bool(pdf_files) + (len(pdf_files) > 1)].format(chr(10).join(pdf_files))}\n{INSTRUCTION}'

first_cycle = True

while (input_data := input(greeting)) != '-q':
    if first_cycle:
        pdf_files = tuple(PDFFiles(dir_name))
        greeting = f'{GREETING[bool(pdf_files) + (len(pdf_files) > 1)].format(chr(10).join(pdf_files))}\n{INSTRUCTION}'
        first_cycle = False
    else:
        pdf_files = tuple(PDFFiles(dir_name))
        greeting = INSTRUCTION
        print(f'{GREETING[bool(pdf_files) + (len(pdf_files) > 1)].format(chr(10).join(pdf_files))}')
    if pdf_files:
        if 'results' not in os.listdir(dir_name) or os.path.isfile(f'{dir_name}/results'):
            os.mkdir('results')

        if input_data.startswith('-p'):
            split_by_programs_nums(pdf_files, input_data[2:])

        elif input_data.startswith('-m'):
            split_by_page_numbers(pdf_files)

        elif input_data.startswith('-h'):
            print(HELP)
            input('Enter, чтобы продолжить')

        elif input_data:
            flights = tuple(s.upper().lstrip() for s in input_data.split(','))
            split_by_flights(pdf_files, flights)
        else:
            split_by_programs(pdf_files)
    else:
        pass
