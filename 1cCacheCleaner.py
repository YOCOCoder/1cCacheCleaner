import os           # Working with operation system environment
import shutil       # Directories processing
import sys          # Pass launch arguments
import ctypes       # Dialogue messages
import datetime
from getpass import getuser
import re           # Regular expressions (folder name mask)


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
            action_msg = "удалены папки с кэшем 1C и создан backup, "
        if arg == "-all_usr":
            all_usr = True
            context_msg = "для всех пользователей"
        if arg == "-log":
            logging = True

    if logging:
        logfile = init_logfile(force, safe, all_usr, logging)

    if not force:
        result = ctypes.windll.user32.MessageBoxW(0,
                                                  f"Будут {action_msg} {context_msg}, продолжить?",
                                                  "Предупреждение!",
                                                  4)
        if result == 6:
            logfile = start_clear_cache(safe, all_usr, force, logging, logfile)
        else:
            ctypes.windll.user32.MessageBoxW(0, f"На нет и суда нет", ":)", 0)
            return
    else:
        logfile = start_clear_cache(safe, all_usr, force, logging, logfile)

    if logging:
        logfile += "Работа скрипта завершена."
        file_log = open("1cCacheCleaner_log.txt", "w")
        file_log.write(logfile)
        file_log.close()

    if not force:
        ctypes.windll.user32.MessageBoxW(0, f"Работа скрипта завершена.", "Готово!", 0)


def init_logfile(force, safe, all_usr, logging):
    """fills the header of log-file with init data
    """
    if logging:
        now = datetime.datetime.now()
        logfile = f"Выполнение скрипта чистки кэша 1С от {now.day}.{now.month}.{now.year}:\n" \
                  f"Пользователь: {getuser()}\n\n"
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


def start_clear_cache(safe, all_usr, force, logging, logfile):
    """initializing cache cleaning"""
    if logging:
        logfile += "Запуск процедуры чистки кэша\n"
    if all_usr:
        if logging:
            logfile += "Получение списка пользователей\n"
        users_folder_list = get_users_list()
        for user_folder in users_folder_list:
            if logging:
                logfile += f"\nДиректория пользователя: {user_folder}\n"
            # For all users
            logfile = clear_cache_folder(user_folder, "Local", "1cv8", safe, force, logging, logfile)
            logfile = clear_cache_folder(user_folder, "Roaming", "1cv82", safe, force, logging, logfile)
            # If cache folder name changed - you can adjust it here, or add new line
    else:
        user_path = os.environ['HOMEPATH']
        if logging:
            logfile += f"\nДиректория пользователя: {user_path}\n"
        # For current user
        logfile = clear_cache_folder(user_path, "Local", "1cv8", safe, force, logging, logfile)
        logfile = clear_cache_folder(user_path, "Roaming", "1cv82", safe, force, logging, logfile)
        # Also here
    return logfile


def clear_cache_folder(user_folder="C:/Users/User", cache_type="Local", cache_dir_name="1cv8",
                       safe=True, force=False, logging=False, logfile=None):
    """search if 1C cache_type (local/roaming) cache in cache_dir_name folder exists
    if safe = True - renames it in format 1cv8_DD_MM_YYYY
    else removes it"""
    path_cache_dir = os.path.join(user_folder, "AppData", cache_type, "1C")
    cache_dir = os.path.join(path_cache_dir, cache_dir_name)
    now = datetime.datetime.now()
    backup_dir = os.path.join(path_cache_dir, f"{cache_dir_name}_{now.day}_{now.month}_{now.year}")

    if os.path.exists(cache_dir):
        if safe:    # With backup
            if logging:
                logfile += f"Создание копии {cache_type} и удаление кэша...\t"
            try:
                remove_cache(cache_dir, backup_dir)
                if logging:
                    logfile += "Успех!\n"
            except PermissionError:
                if not force:
                    show_error_message(cache_dir)
                if logging:
                    logfile += f"Ошибка доступа.\n"
        else:   # Without backup
            if logging:
                logfile += f"Удаление {cache_type} кэша..."
            try:
                remove_cache(cache_dir)
                if logging:
                    logfile += "Успех!\n"
            except PermissionError:
                if not force:
                    show_error_message(cache_dir)
                if logging:
                    logfile += f"Ошибка доступа.\n"
    else:
        logfile += f"{cache_type} кэш не найден\n"
    return logfile


def remove_cache(cache_dir, backup_dir=""):
    """compares folders in cache dir with name mask and removes if it applied
       if backup path is filled - creates copy of folder before remove
    """
    if len(backup_dir) > 0:
        shutil.copytree(cache_dir, backup_dir)
    cache_fol_pattern = re.compile('........-....-....-....-............')
    in_dirs = os.listdir(cache_dir)
    for fol_elm in in_dirs:
        cache_folder = cache_fol_pattern.fullmatch(fol_elm)
        if cache_folder:
            shutil.rmtree(os.path.join(cache_dir, fol_elm))


def show_error_message(cache_dir):
    error_msg = f"Возникли проблемы при удалении кэша в директории:\n" \
                f"{cache_dir}\n" \
                f"Возможно, пользователю, под которым запущен скрипт, не хватает прав\n" \
                f"или вы забыли закрыть 1С :)"
    ctypes.windll.user32.MessageBoxW(0, error_msg, "Ошибка!", 0)


def get_users_list():
    """
    Returns list of users home dir paths in users folder
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
