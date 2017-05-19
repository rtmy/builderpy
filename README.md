# builderpy

## Requirements:
Python >=3.5.2
PostgreSQL >= 9.5.6
git

## Setup:
Make sure that pip for Python 3 installed.
If not, refer to https://pip.pypa.io/en/stable/installing/

`git clone https://github.com/rtmy/builderpy
cd builderpy && pip3 install -r requrements.txt`

Before first usage (run once):
`./preparedb`

`./builder`

## Как использовать:
Запущенный сервер ожидает на порту 8000 HTTP POST запрос вида:
`{
"type-action": действие,
"repository": URL вида "https://github.com/username/"
}`

Доступные действия: собрать содержимое репозитория 'build', получить лог 'retrieve'

## TODO:
* ~~страничка "введите адрес на github"~~
* параллельное исполнение
* полное соответствие спецификации билд-файла
