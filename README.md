# 1С Cache cleaner

> Утилита для чистки кеша 1С с параметрами запуска

## Описание
Выполняет установленные действия с папками кеша 1С (удаление/переименование).
Возможна работа утилиты как в режиме диалоговых окон, так и без.
```
%Путь к пользователю%/AppData/Local/1cv8/
%Путь к пользователю%/AppData/Roaming/1cv82/
```

## Параметры запуска
Без параметров: -safe

- -force	 :	применение скрипта без отображения диалоговых окон
- -safe	   :	вместо удаления папки кеша - переименование в формат папка_ДД_ММ_ГГГГ
- -all_usr :	чистка для всех пользователей системы (понадобятся права администратора)
- -log		 :	при выполнении скрипта создается лог-файл

## Примечание

- Удаляются только папки с кешем, имеющие вид '????????-????-????-????-????????????'
- Скрипт работает под правами пользователя, под которым запущен.
- Перед работой скрипта стоит закрыть запущенную 1С у пользователя, для которого чистится кэш.
- Для чистки кэша всех пользователей, нужны права администратора.