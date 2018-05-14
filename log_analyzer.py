#!/usr/bin/env python2
#  -*- coding: utf-8 -*-
from __future__ import print_function, division
import argparse
import datetime
import gzip
import json
import logging
import os
import settings
import tempfile
from collections import namedtuple, defaultdict
from shutil import copy2
from time import time
# log_format ui_short '$remote_addr $remote_user $http_x_real_ip [$time_local] "$request" '
#                     '$status $body_bytes_sent "$http_referer" '
#                     '"$http_user_agent" "$http_x_forwarded_for" "$http_X_REQUEST_ID" "$http_X_RB_USER" '
#                     '$request_time';

config = {
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log"
}

logger = logging.getLogger(__name__)


LogFileFormat = namedtuple(typename='LogFileFormat',
                           field_names=[
                               'remote_addr',
                               'remote_user',
                               'http_x_real_ip',
                               'time_local',
                               'url',
                               'status',
                               'body_bytes_sent',
                               'http_referer',
                               'user_agent',
                               'http_x_forwarded_for',
                               'http_X_REQUEST_ID',
                               'http_X_RD_USER',
                               'request_time'
                           ])

LogFileInfo = namedtuple(typename='LogFileInfo',
                         field_names=[
                             'path_to_file',
                             'date_file',
                             'format_file'
                         ])


def load_config(path_to_config_file):
    """
    Загрузка параметров конфигурации из файла

    :param str path_to_config_file: путь к файлу конфигурации
    """
    
    if not os.path.exists(path_to_config_file) or not os.path.isfile(path_to_config_file):
        raise Exception('Недействительный путь к файлу конфигурации: {}'.format(path_to_config_file))

    with open(path_to_config_file) as _f:
        try:
            result = json.loads(_f.read())
        except Exception as e:
            logger.exception(e.message)
            raise Exception('Ошибка считывания параметров из конфигурационного файла')
        else:
            return result


def setup_logging(**param):
    """
    Инициализация параметров логирования

    :param dict param: параметры конфигурации
    """
    log_file = param.get('LOGGING_FILENAME', None)
    if log_file:
        log_file = os.path.abspath(log_file)
        if os.path.isdir(log_file):
            log_file = os.path.join(log_file, 'report-{}.log'.format(datetime.datetime.today().strftime('%Y.%m.%d %H:%M:%S')))
        os.makedirs(log_file)
    logging.basicConfig(filename=log_file,
                        format='[%(asctime)s] %(levelname).1s %(message)s',
                        level=logging.INFO,
                        datefmt='%Y.%m.%d %H:%M:%S')


def get_latest_logfile_info(log_dir):
    """
    Получение актуального(последнего по дате) файла лога

    :param str|unicode log_dir: путь к директории с лог-файлами
    :return: информация о последнем лог-файле
    :rtype: LogFileInfo
    """
    _latest_log = None
    for _filename in os.listdir(log_dir):
        match = settings.LOG_FILE_RE_PATTERN.match(_filename)
        if not match:
            continue
        _log_date_string = match.groupdict()['log_date']
        _log_date_date = datetime.datetime.strptime(_log_date_string, "%Y%m%d")
        if not _latest_log or _log_date_date > _latest_log.date_file:
            _latest_log = LogFileInfo(**dict(
                path_to_file=os.path.abspath(os.path.join(log_dir, _filename)),
                date_file=_log_date_date,
                format_file=match.groupdict()['log_format']
            ))
    return _latest_log


def search_report(latest_log_info, report_dir):
    """
    Поиск файла-отчёта для лог-файла

    :param latest_log_info: информация о лог-файле
    :param str|unicode report_dir: путь к директории с отчётами
    :return: наличие файла-отчёта для лог-файла
    :rtype: bool
    """
    _report_file = 'report-{}.html'.format(latest_log_info.date_file.strftime('%Y.%m.%d'))
    _path_to_report_file = os.path.join(report_dir, _report_file)
    return os.path.exists(_path_to_report_file)


def next_line_iterator(latest_log_info):
    """
    Открытие файла логов и итерирование по строкам

    :param latest_log_info: информация о лог-файле
    :return: интератор строк
    :rtype: collections.Iterator[str]
    """
    open_fn = gzip.open if latest_log_info.format_file == 'gz' else open

    with open_fn(latest_log_info.path_to_file) as f_logfile:
        for _line in f_logfile:
            yield _line.decode('utf-8')


def get_next_line_info(line):
    """
    Обработка очередной строки

    :param str|bytes line: очередная строка лога
    :return: информация о следующей записи
    :rtype: LogFileInfo
    """
    logger.info(line)
    math = settings.LOG_RECORD_RE_PATTERN.match(line)
    result = None
    if math:
        result = LogFileFormat(**math.groupdict())
    return result


def save_report(latest_logfile_info, report_dir, parse_data):
    """
    Сохранение отчёта

    :param LogFileInfo latest_logfile_info: информация о лог-файле
    :param str|unicode report_dir: путь к директории сохранения отчётов
    :param list[dict] parse_data: данные для отчёта
    :return:
    """
    _table_json = json.dumps(parse_data)
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)
    _path_to_template = os.path.normpath(os.path.join(os.path.dirname(__file__), 'report.html'))
    with open(_path_to_template, mode='r') as _report_template_file:
        _report_template_data = _report_template_file.read().replace('$table_json', _table_json)
        _temp_path_to_report = os.path.join(tempfile.gettempdir(),
                                            'report-{}.html'.format(latest_logfile_info.date_file.strftime('%Y.%m.%d'))
                                            )
        _path_to_report = os.path.join(report_dir,
                                       'report-{}.html'.format(latest_logfile_info.date_file.strftime('%Y.%m.%d'))
                                       )

        with open(_temp_path_to_report, mode='w') as _report_file:
            _report_file.write(_report_template_data)
        copy2(_temp_path_to_report, _path_to_report)


def write_ts(ts_file):
    with open(ts_file, mode='a') as _ts:
        _ts.write(str(time()) + '\n')


def median(times_list):
    times_list = sorted(times_list)
    if len(times_list) % 2 == 1:
        return times_list[len(times_list) // 2]
    else:
        return 0.5 * (times_list[len(times_list) // 2 - 1] + times_list[len(times_list) // 2])


def main(**param):
    """
    Оснавная процедура

    :param str param: параметры конфигурации
    :return:
    """
    setup_logging(**param)

    log_dir = param.get('LOG_DIR', None)
    report_dir = param.get('REPORT_DIR', None)
    report_size = param.get('REPORT_SIZE', 100)
    ts_filename = param.get('TS_FILENAME', None)
    if not log_dir or not os.path.isdir(os.path.abspath(log_dir)):
        raise Exception('Не найдена директория с обрабатываемыми файлами!')

    if not report_dir or not os.path.isdir(os.path.abspath(report_dir)):
        raise Exception('Не найдена директория для хранения отчётов!')

    latest_logfile_info = get_latest_logfile_info(log_dir)

    if search_report(latest_logfile_info, report_dir):
        logging.info('Лог-файл "{}" обработан'.format(os.path.basename(latest_logfile_info.path_to_file)))
        return

    line_count = 0
    line_error = 0
    url_times = defaultdict(list)       # Подсчёт времени для каждого url

    for next_line in next_line_iterator(latest_logfile_info):
        line_count += 1
        next_line_info = get_next_line_info(next_line)
        if not next_line_info:
            line_error += 1
            continue

        url = next_line_info.url
        request_time = float(next_line_info.request_time)
        url_times[url].append(request_time)

        if line_count >= 100:
            break

    error_perc = param.get('ERROR_PERC', 10.0)
    calc_error_perc = round(line_error/line_count * 100, 1)
    if calc_error_perc > error_perc:
        raise Exception('Количество ошибочных url адресов превысило допустимое значение.')

    report_data = []
    count = 0
    time_count = 0

    for url, times in url_times.items():
        report_data.append(dict(
            url=url,
            count=len(times),
            time_sum=sum(times),
            time_max=max(times),
            time_avg=round(sum(times) / len(times), 3),
            time_med=median(times)
        ))

        count += len(times)
        time_count += sum(times)

    for report_line in report_data:
        report_line.update(**dict(
            count_perc=round(report_line['count'] / count * 100, 3),
            time_perc=round(report_line['time_sum'] / time_count * 100, 3),
        ))

    report_data = sorted(report_data, key=lambda line: line['time_sum'])[-report_size:]

    save_report(latest_logfile_info, report_dir, report_data)
    _dir, _file = os.path.split(ts_filename)
    if not _dir:
        ts_filename = os.path.join(os.path.curdir, ts_filename)
    write_ts(ts_filename)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-c',
                        '--config',
                        help='Имя конфигурационного файла',
                        default=settings.DEFAULT_CONFIG_FILE,
                        nargs='?'
                        )
    args = parser.parse_args()
    config_main = config.copy()
    if args.config:
        file_config = os.path.abspath(args.config)
        config_from_file = load_config(file_config)
        config_main.update(config_from_file)
    try:
        main(**config_main)
    except Exception as e:
        logger.exception(e)
