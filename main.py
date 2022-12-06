import os
import time
from modules.menu import UI as menu
from modules.menu import GUI as graphical_menu
from modules.parser import parser
from modules.analyzer import analyzer


def main():
    graphical_menu.init(parser, analyzer)
    # status = menu.init()
    # if status == "create_snapshot":
    #     status = parser.init()
    #     print(f"> Создание снимка профиля компетенеций...")
    #     if len(status['errors']) > 0:
    #         print(f"Ошибки: {status['errors']}")
    #     else:
    #         print(f"id: {status['id']}")
            # analyzer.init(status['id'])


if __name__ == "__main__":
    main()
