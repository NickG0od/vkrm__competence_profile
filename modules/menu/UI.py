import os
import json
from pynput import keyboard


C_POINT = 0
MENU_FIELDS = []
with open('modules/menu/menu.json', mode='r', encoding='utf-8') as file:
    MENU_FIELDS = json.load(file)
MENU_ON = False
RETURNED_MENU = ""


def init():
    global MENU_ON
    MENU_ON = True
    if len(MENU_FIELDS) > 0:
        menu_cycle()
        input()
    else:
        print('> ERR: Cannot load menu...')
    return RETURNED_MENU


def render_menu():
    os.system('cls') if os.name == "nt" else os.system('clear')
    for i in range(len(MENU_FIELDS)):
        tmp_str = "> " if i == C_POINT else ""
        print(f"{tmp_str}{MENU_FIELDS[i]['title']}")


def menu_cycle():
    listener = keyboard.Listener(on_release=on_release)
    listener.start()
    tmp_point = -1
    while MENU_ON:
        if tmp_point != C_POINT:
            render_menu()
            tmp_point = C_POINT
    listener.stop()


def on_release(key):
    global MENU_ON
    global C_POINT
    if key == keyboard.Key.up:
        C_POINT -= 1
        if C_POINT < 0:
            C_POINT = len(MENU_FIELDS) - 1
    if key == keyboard.Key.down:
        C_POINT += 1
        if C_POINT > len(MENU_FIELDS) - 1:
            C_POINT = 0
    if key == keyboard.Key.enter:
        menu_opener()
    if key == keyboard.Key.esc:
        MENU_ON = False
        return False


def menu_opener():
    global MENU_ON
    global RETURNED_MENU
    current_menu = MENU_FIELDS[C_POINT]
    RETURNED_MENU =  current_menu['id']
    MENU_ON = False
    return
