# builderpy

## Требуется:
Python >=3.5.2  
PostgreSQL >= 9.5.6  
git

## Установка:
Для установки потребуется [pip](https://pip.pypa.io/en/stable/installing/) для Python 3

`git clone https://github.com/rtmy/builderpy`  
`cd proveryalka && pip3 install -r requirements.txt`

## Как использовать:
Запущенный сервер ожидает на порту 8000 HTTP POST запрос вида:
`{  
"type-action": действие,  
"repository": URL вида "https://github.com/username/reponame"  
}`

Доступные действия: собрать содержимое репозитория 'build', получить лог 'retrieve'

## Что может случиться:
git запросит логин и пароль

## Что планируется:
* ~~страничка "введите адрес на github"~~
* параллельное исполнение
* полное соответствие спецификации билд-файла
