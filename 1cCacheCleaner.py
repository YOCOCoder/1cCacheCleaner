import os
import sys
import ctypes
import datetime
import getpass


def main(argv):
    force = False
    safe = False
    all_usr = False
    logging = False
    logfile = ""

    action_msg = "удалены папки с кэшем 1C"
    context_msg = "для текущего пользователя"
    for arg in argv:
        if arg == "-force":
            force = True
        if arg == "-safe":
            safe = True
            action_msg = "переименованы папки с кэшем 1C"
        if arg == "-all_usr":
            all_usr = True
            context_msg = "для всех пользователей"
        if arg == "-log":
            logging = True

    if logging:
        logfile = init_logfile(force, safe, all_usr, logging, logfile)

    if not force:
        result = ctypes.windll.user32.MessageBoxW(0, f"Будут {action_msg} {context_msg}, продолжить?", "Предупреждение!",4)
        if result == 6:
            logfile = clear_cache(safe, all_usr, force, logging, logfile)
        else:
            ctypes.windll.user32.MessageBoxW(0, f"На нет и суда нет", ":)", 0)
            return
    else:
        logfile = clear_cache(safe, all_usr, force, logging, logfile)
    if logging:
        logfile += "Работа скрипта завершена."
        file_log = open("1cCacheCleaner_log.txt", "w")
        file_log.write(logfile)
        file_log.close()


def init_logfile(force, safe, all_usr, logging, logfile):
    if logging:
        now = datetime.datetime.now()
        logfile = f"Выполнение скрипта чистки кэша 1С от {now.day}.{now.month}.{now.year}:\n" \
                  f"Пользователь: {getpass.getuser()}\n\n"
        logfile += "Параметры запуска:\n"
        if force:
            logfile += "Принудительно\t\t= Истина\n"
        else:
            logfile += "Принудительно\t\t= Ложь\n"
        if safe:
            logfile += "Не удалять папки\t= Истина\n"
        else:
            logfile += "Не удалять папки\t= Ложь\n"
        if all_usr:
            logfile += "Все пользователи\t= Истина\n"
        else:
            logfile += "Все пользователи\t= Ложь\n"
        logfile += "\n"
        return logfile


def clear_cache(safe, all_usr, force, logging, logfile):
    if logging:
        logfile += "Запуск процедуры чистки кэша\n"
    if all_usr:
        if logging:
            logfile += "Получение списка пользователей\n"
        users_folder_list = get_users_list()
        for user_folder in users_folder_list:
            if logging:
                logfile += f"\nДиректория пользователя: {user_folder}\n"
            logfile = clear_folder_local(user_folder, safe, force, logging, logfile)
            logfile = clear_folder_roaming(user_folder, safe, force, logging, logfile)
    else:
        user_path = os.environ['HOMEPATH']
        if logging:
            logfile += f"\nДиректория пользователя: {user_path}\n"
        logfile = clear_folder_local(user_path, safe, force, logging, logfile)
        logfile = clear_folder_roaming(user_path, safe, force, logging, logfile)
    return logfile


def clear_folder_local(user_folder="C:/Users/User", safe=True, force=False, logging=False, logfile=None):
    """search if 1C local cache folder exists
    if safe = True - renames it in format 1cv8_DD_MM_YYYY
    else removes it"""
    cache_dir_name = "1cv8"
    path_local_cache_dir = os.path.join(user_folder, "AppData", "Local", "1C")
    cache_dir = os.path.join(path_local_cache_dir, cache_dir_name)
    if os.path.exists(cache_dir):
        if safe:
            if logging:
                logfile += "Переименование Local кэша..."
            now = datetime.datetime.now()
            try:
                os.rename(cache_dir,
                          os.path.join(path_local_cache_dir, f"{cache_dir_name}_{now.day}_{now.month}_{now.year}"))
                if logging:
                    logfile += "Успех!\n"
            except PermissionError:
                if not force:
                    error_msg = f"Не удалось переименовать директорию {cache_dir}\n" \
                                f"Возможно, пользователю, под которым запущен скрипт, не хватает прав" \
                                f"или вы забыли закрыть 1С :)"
                    ctypes.windll.user32.MessageBoxW(0, error_msg, "Ошибка!", 0)
                if logging:
                    logfile += "Ошибка!\n"
                    logfile += f"Не удалось переименовать директорию {cache_dir}. Ошибка доступа.\n"
        else:
            if logging:
                logfile += "Удаление Local кэша..."
            try:
                os.remove(cache_dir)
                if logging:
                    logfile += "Успех!\n"
            except PermissionError:
                if not force:
                    error_msg = f"Не удалось удалить директорию {cache_dir}\n" \
                                f"Возможно, пользователю, под которым запущен скрипт, не хватает прав" \
                                f"или вы забыли закрыть 1С :)"
                    ctypes.windll.user32.MessageBoxW(0, error_msg, "Ошибка!", 0)
                if logging:
                    logfile += "Ошибка!\n"
                    logfile += f"Не удалось удалить директорию {cache_dir}. Ошибка доступа.\n"
    else:
        logfile += "Local кэш не найден\n"
    return logfile


def clear_folder_roaming(user_folder="C:/Users/User", safe=True, force=False, logging=False, logfile=None):
    """search if 1C roaming cache folder exists
    if safe = True - renames it in format 1cv8_DD_MM_YYYY
    else removes it"""
    cache_dir_name = "1cv82"
    path_local_cache_dir = os.path.join(user_folder, "AppData", "Roaming", "1C")
    cache_dir = os.path.join(path_local_cache_dir, cache_dir_name)
    if os.path.exists(cache_dir):
        if safe:
            if logging:
                logfile += "Переименование Roaming кэша..."
            now = datetime.datetime.now()
            try:
                os.rename(cache_dir,
                          os.path.join(path_local_cache_dir, f"{cache_dir_name}_{now.day}_{now.month}_{now.year}"))
                if logging:
                    logfile += "Успех!\n"
            except PermissionError:
                if not force:
                    error_msg = f"Не удалось переименовать директорию {cache_dir}\n" \
                                f"Возможно, пользователю, под которым запущен скрипт, не хватает прав" \
                                f"или вы забыли закрыть 1С :)"
                    ctypes.windll.user32.MessageBoxW(0, error_msg, "Ошибка!", 0)
                if logging:
                    logfile += "Ошибка!\n"
                    logfile += f"Не удалось переименовать директорию {cache_dir}. Ошибка доступа.\n"
        else:
            if logging:
                logfile += "Удаление Roaming кэша..."
            try:
                os.remove(cache_dir)
                if logging:
                    logfile += "Успех!\n"
            except PermissionError:
                if not force:
                    error_msg = f"Не удалось удалить директорию {cache_dir}\n" \
                                f"Возможно, пользователю, под которым запущен скрипт, не хватает прав" \
                                f"или вы забыли закрыть 1С :)"
                    ctypes.windll.user32.MessageBoxW(0, error_msg, "Ошибка!", 0)
                if logging:
                    logfile += "Ошибка!\n"
                    logfile += f"Не удалось удалить директорию {cache_dir}. Ошибка доступа.\n"
    else:
        logfile += "Roaming кэш не найден\n"
    return logfile


def get_users_list():
    """
    Returns list of users homedir paths in users folder
    :return: list
    """
    users_list = []
    path = f"{os.environ['HOMEDRIVE']}/Users"
    for in_dir in os.listdir(path=path):
        user_path = os.path.join(path, in_dir)
        if not os.path.isfile(user_path):
            users_list.append(user_path)
    return users_list


if __name__ == "__main__":
   main(sys.argv[1:])
