import pytest
from contextlib import nullcontext
from main import find_path, merge_dict, read_log, result_out, create_parser
from unittest.mock import patch, call

#тесты для cli-report приложения
class Test_cli_report:
    #тесты функции merge_dict
    @pytest.mark.parametrize(
        'osn, slave, expected, err',
        [
            #если оба словаря заполнены
            ( {'/admin/dashboard/':  {'DEBUG': 5, 'INFO': 4, 'WARNING': 7, 'ERROR': 5, 'CRITICAL':8}},
              {'/api/v1/reviews/':  {'DEBUG': 5, 'INFO': 4, 'WARNING': 7, 'ERROR': 5, 'CRITICAL':8}},
              {'/admin/dashboard/':  {'DEBUG': 5, 'INFO': 4, 'WARNING': 7, 'ERROR': 5, 'CRITICAL':8},
               '/api/v1/reviews/':  {'DEBUG': 5, 'INFO': 4, 'WARNING': 7, 'ERROR': 5, 'CRITICAL':8}},
              nullcontext()
            ),
            #если лишь ведомый словарь заполнен
            ({},
            {'/api/v1/reviews/': {'DEBUG': 5, 'INFO': 4, 'WARNING': 7, 'ERROR': 5, 'CRITICAL': 8}},
            {'/api/v1/reviews/': {'DEBUG': 5, 'INFO': 4, 'WARNING': 7, 'ERROR': 5, 'CRITICAL': 8}},
             nullcontext()
            ),
            #если лишь основной словарь заполнен
            ({'/api/v1/reviews/': {'DEBUG': 5, 'INFO': 4, 'WARNING': 7, 'ERROR': 5, 'CRITICAL': 8}},
             {},
             {'/api/v1/reviews/': {'DEBUG': 5, 'INFO': 4, 'WARNING': 7, 'ERROR': 5, 'CRITICAL': 8}},
             nullcontext()
             ),
            #если два словаря пустые
            ({}, {}, {}, nullcontext()),
            #если два одинаковых
            ( {'/admin/dashboard/':  {'DEBUG': 5, 'INFO': 4, 'WARNING': 7, 'ERROR': 5, 'CRITICAL':8}},
              {'/admin/dashboard/': {'DEBUG': 5, 'INFO': 4, 'WARNING': 7, 'ERROR': 5, 'CRITICAL': 8}},
              {'/admin/dashboard/':  {'DEBUG': 5*2, 'INFO': 4*2, 'WARNING': 7*2, 'ERROR': 5*2, 'CRITICAL':8*2}},
              nullcontext()
              ),
            #если внутри пустой подсловарь
            ({'/admin/dashboard/': {}},
             {'/admin/dashboard/': {'DEBUG': 5, 'INFO': 4, 'WARNING': 7, 'ERROR': 5, 'CRITICAL': 8}},
             {'/admin/dashboard/': {'DEBUG': 5, 'INFO': 4, 'WARNING': 7, 'ERROR': 5, 'CRITICAL': 8}},
             nullcontext()),
            #если внутри два пустых подсловаря
            ({'/admin/dashboard/': {}},
                {'/admin/dashboard/': {}},
                {'/admin/dashboard/': {}},
             nullcontext()
            ),
            #если вместо ключа None
            ({None: {'DEBUG': 5, 'INFO': 4, 'WARNING': 7, 'ERROR': 5, 'CRITICAL': 8}},
             {None: {'DEBUG': 5, 'INFO': 4, 'WARNING': 7, 'ERROR': 5, 'CRITICAL': 8}},
             {None: {'DEBUG': 5*2, 'INFO': 4*2, 'WARNING': 7*2, 'ERROR': 5*2, 'CRITICAL': 8*2}},
             nullcontext()
             ),
            #если вместо ключа None, и вместо значения пустой словарь
            ({None: {}},
             {None: {}},
             {None: {}},
             nullcontext()
             ),
            #если вместо ключа None, и вместо значения None
            ({None: None},
             {None: None},
             {None: None},
             pytest.raises(TypeError)
             ),
        ]
    )
    def test_merge_dict(self, osn, slave, expected, err):
        with err:
            assert merge_dict(osn, slave) == expected


    #тесты функции find_path
    @pytest.mark.parametrize(
        'mas, res, err',
        [
            #в списке нет нужного пути
            (['no_path', 'no_path', 'no_path'], '', nullcontext()),
            #в списке один нужный путь
            (['no_path', '/var/log', 'no_path'], '/var/log', nullcontext()),
            #в списке два возможных пути (предполагается, что первый найденный - основной)
            (['no_path', '/var/log', "/usr/bin"], '/var/log', nullcontext()),
            #список пустой
            ([], '', nullcontext()),
            #в списке есть элементы другого типа данных
            ([9, True, 0.2, [], (), {}, '/var/log'], '/var/log',nullcontext()),
            #список не является списком
            ('/var/log', None, pytest.raises(TypeError)),
            ({}, None, pytest.raises(TypeError)),
            (None, None, pytest.raises(TypeError))
        ]
    )
    def test_find_path(self, mas, res, err):
        with err:
            assert find_path(mas) is res


    #тесты функции read_log
    @pytest.mark.parametrize(
        'path, res, err',
        [
            #нормальная работа программы
            ('./logs/app1.log',
            {'/api/v1/reviews/': {'DEBUG': 1, 'INFO': 5, 'WARNING': 2, 'ERROR': 0, 'CRITICAL': 0},
              '/admin/dashboard/': {'DEBUG': 6, 'INFO': 6, 'WARNING': 1, 'ERROR': 2, 'CRITICAL': 1},
              '/api/v1/users/': {'DEBUG': 2, 'INFO': 4, 'WARNING': 1
                  , 'ERROR': 0, 'CRITICAL': 0},
              '/api/v1/cart/': {'DEBUG': 2, 'INFO': 3, 'WARNING': 1, 'ERROR': 0, 'CRITICAL': 2},
              '/api/v1/products/': {'DEBUG': 0, 'INFO': 3, 'WARNING': 0, 'ERROR': 0, 'CRITICAL': 0},
              '/api/v1/support/': {'DEBUG'
                                   : 1, 'INFO': 1, 'WARNING': 1, 'ERROR': 3, 'CRITICAL': 1},
              '/api/v1/auth/login/': {'DEBUG': 1, 'INFO': 4, 'WARNING': 3, 'ERROR': 1, 'CRITICAL': 1},
              '/admin/login/': {'DEBUG': 0, 'INFO': 5, 'WARNING': 1, 'ERROR': 1, 'CRITICAL': 0}
                 , '/api/v1/checkout/': {'DEBUG': 3, 'INFO': 6, 'WARNING': 0, 'ERROR': 1, 'CRITICAL': 1},
              '/api/v1/payments/': {'DEBUG': 2, 'INFO': 7, 'WARNING': 2, 'ERROR': 1, 'CRITICAL': 0},
              '/api/v1/orders/': {'DEBUG': 2, 'INFO': 2, 'WARNING': 1, 'ERROR': 2, 'CRITICAL': 0},
              '/api/v1/shipping/': {'DEBUG': 1, 'INFO': 2, 'WARNING': 0, 'ERROR': 1, 'CRITICAL': 0}}
             , nullcontext()),
            # если путь неправильный
            ('wrong_path', {}, nullcontext()),
            # если тип данных у пути неправильный
            ([], {}, nullcontext())
        ]
    )
    def test_read_log(self, path, res, err):
        with err:
            assert read_log(path) == res


    #тесты функции result_out
    @patch('builtins.print')
    @pytest.mark.parametrize(
        'd, res',
        [
            #стандартный вывод
            (
                    {
                        '/api/v1/reviews/': {'DEBUG': 1, 'INFO': 5, 'WARNING': 2, 'ERROR': 0, 'CRITICAL': 0},
                        '/admin/dashboard/': {'DEBUG': 6, 'INFO': 6, 'WARNING': 1, 'ERROR': 2, 'CRITICAL': 1}
                    },
                    [
                     call('Total requests: 24'),
                     call('HANDLER          ', end='\t'),
                     call('DEBUG', end='\t'),
                     call('INFO', end='\t'),
                     call('WARNING', end='\t'),
                     call('ERROR', end='\t'),
                     call('CRITICAL', end='\t'),
                     call(),
                     call('/admin/dashboard/', '6    ', '6   ', '1      ', '2    ', '1       ', sep='\t'),
                     call('/api/v1/reviews/ ', '1    ', '5   ', '2      ', '0    ', '0       ', sep='\t'),
                     call('ИТОГ             ', end='\t'),
                     call('7    ', end='\t'),
                     call('11  ', end='\t'),
                     call('3      ', end='\t'),
                     call('2    ', end='\t'),
                     call('1       ', end='\t'),
                     call()
                    ]
            ),
            #пустой словарь
            ({},
                 [
                 call('Total requests: 0'),
                 call('HANDLER', end='\t'),
                 call('DEBUG', end='\t'),
                 call('INFO', end='\t'),
                 call('WARNING', end='\t'),
                 call('ERROR', end='\t'),
                 call('CRITICAL', end='\t'),
                 call(),
                 call('ИТОГ   ', end='\t'),
                 call('0    ', end='\t'),
                 call('0   ', end='\t'),
                 call('0      ', end='\t'),
                 call('0    ', end='\t'),
                 call('0       ', end='\t'),
                 call()]
             )
        ]
    )
    def test_result_out(self, mocked_print, d, res):
        result_out(d)
        # Проверяем основные вызовы print
        assert mocked_print.mock_calls == res


    # Тесты для аргументов командной строки
    class TestArgParser:
        @pytest.fixture
        def parser(self):
            return create_parser()

        #проверка, что парсер создается
        def test_creating_parser(self, parser):
            return parser is not None


        @pytest.mark.parametrize(
            'elems, res, err',
             [
                 #передаем файлы
                 (['--report', 'handlers', 'file1.log', 'file2.log', 'file3.log'], ['file1.log', 'file2.log', 'file3.log'], nullcontext()),
                 (['--report', 'handlers', 'file1.log', 'file2.log'], ['file1.log', 'file2.log'], nullcontext()),
                 (['--report', 'handlers', 'file1.log'], ['file1.log'], nullcontext()),
                 (['--report', 'handlers'], [], nullcontext()),
                 # проверка, что --report и его название обязательны
                 (['--report'], [], pytest.raises(SystemExit)),
                 (['file1.log'],[], pytest.raises(SystemExit))
             ])
        #проверка передачи файлов
        def test_files_argument(self, parser, elems, res, err):
            with err:
                args = parser.parse_args(elems)
                assert args.files == res




