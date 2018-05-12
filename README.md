# 01_advanced_basics
домашнее задание к лекции Advanced basics

## Install
Получение репозитория

```cmd
git clone https://github.com/shpawel/01_advanced_basics.git
```

## Зависимости
- python2.7

## Запуск

### Анализатор логов
Основым исполняемым модулем является **log_analyze.py**
```cmd
python log_analyze.py
```

### Параметры запуска
|Параметр|Описание|Значение по умолчанию|
|--------|--------|:-------------------|
|-h|Вывод посказки о параметрах запуска скрипта|
|-c, --config|Путь к файлу с параметрами| ./config.json |

### Тестирование
```cmd
python -m unittest discover -v
```