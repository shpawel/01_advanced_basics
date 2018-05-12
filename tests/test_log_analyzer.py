#!/usr/bin/env python2
#  -*- coding: utf-8 -*-
import datetime
import os
import unittest
import log_analyzer


class LogAnalyzerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.log_dir = os.path.abspath(os.path.join(os.path.curdir, 'log'))
        cls.report_dir = os.path.abspath(os.path.join(os.path.curdir, 'report'))

    def test_load_config(self):
        """
        Загрузка файла конфигурации
        :return:
        """
        file_config = log_analyzer.load_config(os.path.join(os.path.curdir, 'config.json'))
        self.assertEqual(file_config, dict(
            TS_FILENAME="log_analyzer.ts",
            REPORT_DIR="./report",
            LOG_DIR="./log",
            LOGGING_FILENAME=None,
            ERROR_PERC=10.0
        ))

    def test_get_latest_logfile_info(self):
        """
        Получение последнего лог-файла
        :return:
        """
        logfile_info = log_analyzer.get_latest_logfile_info(self.log_dir)
        self.assertEqual(logfile_info.path_to_file, os.path.join(self.log_dir, 'nginx-access-ui.log-20170630.gz'))
        self.assertEqual(logfile_info.date_file.strftime('%Y.%m.%d'), '2017.06.30')
        self.assertEqual(logfile_info.format_file, 'gz')

    def test_exit_report(self):
        """
        Существование отчёта
        :return:
        """
        logfile_info = log_analyzer.LogFileInfo(
            os.path.join(self.log_dir, 'nginx-access-ui.log-20170630.gz'),
            datetime.datetime(2017, 6, 29),
            'gz'
        )
        self.assertTrue(log_analyzer.search_report(logfile_info, self.report_dir))

    def test_not_exit_report(self):
        """Отсутствие отчёта"""
        logfile_info = log_analyzer.LogFileInfo(
            os.path.join(self.log_dir, 'nginx-access-ui.log-20170628.gz'),
            datetime.datetime(2017, 6, 28),
            'gz'
        )
        self.assertFalse(log_analyzer.search_report(logfile_info, self.report_dir))


if __name__ == '__main__':
    unittest.main()
