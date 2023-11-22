import pdfplumber
import PyPDF2
import os
import re
import json

DEFAULTS = {'path': 'results/by_programs'}


class PDFFiles:
    """get folder and return iterator of PDF file names"""

    def __init__(self, dir_name):
        self.dir_name = dir_name

    def __iter__(self):
        return (filename for filename in os.listdir(self.dir_name)
                if os.path.isfile(filename) and filename.endswith('.pdf'))


def _get_path_from_cfg(arg='path'):
    if not os.path.exists('cfg.json'):
        with open('cfg.json', 'w') as json_file:
            json.dump(DEFAULTS, json_file)
            res = DEFAULTS[arg]
    else:
        try:
            with open('cfg.json') as json_file:
                cfg = json.load(json_file)
                res = cfg[arg]
        except json.JSONDecodeError as er:
            res = DEFAULTS[arg]
            print(f'Ошибка в файле cfg.json: {er}')
    return res


def _get_line_from_page(pdf_obj: pdfplumber.PDF, page_index: int, str_index=-1) -> str:
    """Считываем строку текста со страницы PDF документа.
    Строка 4 - дата.
    Строка 5 - номер программы.
    По умолчанию - последняя"""
    try:
        text_from_page = pdf_obj.pages[page_index].extract_text().strip().split('\n')
        return text_from_page[str_index]
    except IndexError:
        return 'не удалось считать данные'


def _get_programs(file: str) -> tuple[dict, str]:
    with (pdfplumber.open(file) as pdf_file):
        programs = {}
        single_page = True
        date_from_first_page = _get_line_from_page(pdf_file, 0, 4)
        le = len(pdf_file.pages)
        print(f'Чтение файла {file:>35}:')
        progress = 0
        for i, page in enumerate(pdf_file.pages):
            if (progress_progress := 49 * (i + 1) // le - progress) > 0:
                # print('\033[33m', end='')
                print('■' * progress_progress, end='')
                progress += progress_progress

            if single_page:
                program = _get_line_from_page(pdf_file, i, 5)

            single_page = 'Total Pax: ' in _get_line_from_page(pdf_file, i)
            programs[program] = programs.get(program, []) + [i]
        print()
    return programs, date_from_first_page


def split_by_flights(pdf_files, flights: list[str] | tuple[str]) -> None:
    print(list(flights))

    for file in pdf_files:
        with pdfplumber.open(file) as pdf_file:
            date_from_first_page = _get_line_from_page(pdf_file, 0, 4)
            pages_by_flights = {}
            flight_for_this_i = None
            single_page = True

            le = len(pdf_file.pages)
            print(f'Чтение файла {file:>35}:' if len(pdf_files) > 1 else 'Чтение файла')
            progress = 0
            for i, page in enumerate(pdf_file.pages):
                if (progress_progress := 49 * (i + 1) // le - progress) > 0:
                    # print('\033[33m', end='')
                    print('■' * progress_progress, end='')
                    progress += progress_progress

                table = page.extract_table()
                if single_page:
                    try:
                        for flight in flights:
                            if table[1][4].lstrip().upper().startswith(flight):
                                pages_by_flights[i] = flight
                                flight_for_this_i = flight
                                break
                    except IndexError:
                        ...
                    except TypeError:
                        ...
                        # print(f'TypeError на странице{i + 1}')
                    if 'Total Pax: ' in _get_line_from_page(pdf_file, i):
                        single_page = True
                    elif i in pages_by_flights:
                        single_page = False
                else:
                    if flight_for_this_i:
                        pages_by_flights[i] = flight_for_this_i
                    if 'Total Pax: ' in _get_line_from_page(pdf_file, i):
                        single_page = True
                # print('\033[0m  ☑️\n', 'добавленные страницы:', *(x + 1 for x in sorted(
                #     pages_by_flights, key=lambda x: flights.index(pages_by_flights[x]))), '\n')
            if pages_by_flights:
                print('\nдобавленные страницы:', *(x + 1 for x in sorted(
                    pages_by_flights, key=lambda x: flights.index(pages_by_flights[x]))))
            else:
                print('\nРейсы не найдены')

        reader = PyPDF2.PdfReader(file)
        writer = PyPDF2.PdfWriter()

        for i in sorted(pages_by_flights, key=lambda x: flights.index(pages_by_flights[x])):
            writer.add_page(reader.pages[i])

        if writer.pages:
            with open(f'results/{date_from_first_page} [' + ']['.join(map(str.upper, flights)) + '].pdf',
                      'wb') as split_motive:
                writer.write(split_motive)


def split_by_programs(pdf_files: tuple[str] | list[str]) -> None:
    for file in pdf_files:
        # with (pdfplumber.open(file) as pdf_file):
            # programs = {}
            # single_page = True
            # date_from_first_page = _get_line_from_page(pdf_file, 0, 4)
            # le = len(pdf_file.pages)
            # print(f'Чтение файла {file:>35}:' if len(pdf_files) > 1 else 'Чтение файла')
            # progress = 0
            # for i, page in enumerate(pdf_file.pages):
            #     if (progress_progress := 49 * (i + 1) // le - progress) > 0:
            #         # print('\033[33m', end='')
            #         print('■' * progress_progress, end='')
            #         progress += progress_progress
            #
            #     if single_page:
            #         program = _get_line_from_page(pdf_file, i, 5)
            #
            #     single_page = 'Total Pax: ' in _get_line_from_page(pdf_file, i)
            #     programs[program] = programs.get(program, []) + [i]
            # print()
        programs, date_from_first_page = _get_programs(file)
        if programs:
            result_folder = f'{_get_path_from_cfg()}/{date_from_first_page}'
            try:
                os.makedirs(result_folder)
            except FileExistsError:
                pass

            reader = PyPDF2.PdfReader(file)
            for program, pages in programs.items():
                writer = PyPDF2.PdfWriter()
                for i in pages:
                    writer.add_page(reader.pages[i])
                split_motive = open(f'{result_folder}/ARR {program} {date_from_first_page}.pdf', 'wb')
                writer.write(split_motive)
                split_motive.close()


def _extract_numbers(input_string):
    results = {}
    for s in input_string.split('/'):
        pattern = r'(\d+)-(\d+)|(\d+)'
        matches = re.findall(pattern, input_string)
        result = []
        for match in matches:
            if match[0] and match[1]:
                # Интервал чисел
                result.extend(range(int(match[0]), int(match[1]) + 1))
            elif match[2]:
                # Отдельное число
                result.append(int(match[2]))
        results[re.sub('[^0-9-]', ' ', s).replace('  ', ' ').strip()] = result
    return results


def split_by_programs_nums(pdf_files, input_str=''):
    if not input_str:
        input_str = input('Введите номера программ: ')
    programs_dict = _extract_numbers(input_str)
    for pdf_file in pdf_files:
        all_programs, date = _get_programs(pdf_file)
        if all_programs:
            try:
                os.makedirs('results')
            except FileExistsError:
                pass

            for programs_str, programs_list in programs_dict.items():
                reader = PyPDF2.PdfReader(pdf_file)
                writer = PyPDF2.PdfWriter()

                if set(programs_list).intersection({int(x) for x in all_programs}):
                    for program, pages in ((k, v) for k, v in all_programs.items() if int(k) in programs_list):

                        for i in pages:
                            writer.add_page(reader.pages[i])
                    with open(f'results/{date} [{programs_str[:180]}].pdf', 'wb') as split_motive:
                        writer.write(split_motive)
                else:
                    print('Указанные программы не найдены')


def split_by_page_numbers(pdf_files):
    print('Укажите необходимые страницы и/или интервалы(через дефис)\n'
          'Enter - пропустить текущий файл, -q - выход')
    for pdf_file in pdf_files:
        reader = PyPDF2.PdfReader(pdf_file)
        writer = PyPDF2.PdfWriter()
        print(f'Текущий файл {pdf_file:<35} Всего страниц: {len(reader.pages)}')

        str_pages = input('Введите нужные страницы: ')
        if str_pages == '-q':
            break

        for pages_str, pages_list in _extract_numbers(str_pages).items():
            reader = PyPDF2.PdfReader(pdf_file)
            writer = PyPDF2.PdfWriter()

            for page in pages_list:
                if page <= len(reader.pages):
                    writer.add_page(reader.pages[page - 1])
            if writer.pages:
                with open(f'results/{pdf_file[:-4]} Pages[{pages_str}].pdf', 'wb') as split_motive:
                    writer.write(split_motive)
