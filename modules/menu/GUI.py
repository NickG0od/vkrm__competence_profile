import PySimpleGUI as sg


main_menu_column = [
    [sg.Button("Сделать снимок профиля компетенций", key="_create_snapshot")],
    [sg.Button("Просмотреть список снимков профилей компетенций", key="_snapshots_list")],
    [sg.Button("Выход", key="_exit")]
]
create_snapshot_column = [
    [
        sg.Text("Профессия, должность или компания *", key="_proffesion_text", size=(30, 1)), 
        sg.InputText(key="_proffesion_value", size=(40, 1))
    ],
    [
        sg.Text("Уровень дохода (руб.)", key="_salary_text", size=(30, 1)),
        sg.InputText(key="_salary_value", size=(10, 1))
    ],
    [
        sg.Text("Регион", key="_region_text", size=(30, 1)),
        sg.InputText(key="_region_value", size=(30, 1))
    ],
    [
        sg.Text("Количество обрабатываемых страниц", key="_pages_count_text", size=(30, 1)),
        sg.Combo(list(range(1, 51)), default_value=1, key="_pages_count_value", size=(10, 1))
    ],
    [
        sg.Text("Сбор полной информации \n(может занять больше времени)", key="_full_block_text", size=(30, 2)),
        sg.Checkbox('', default=False, key="_full_block_value")
    ],
    [sg.Button("<- Назад", key="_back_to_menu"), sg.Button("Продолжить", key="_enter_creating_snapshot")]
]
snapshots_list_column = [
    [sg.Text("Привет")],
    [sg.Button("<- Назад", key="_back_to_menu")]
]
status_handler_column = [
    [sg.Text("", key="_status_text")],
    [sg.Button("OK!", key="_status_ok")]
]
analyzer_column = [
    [sg.Text("-- Все слова --")],
    [
        sg.InputText(key="_analyzer_all_words_search", size=(20, 1), tooltip="Поиск", enable_events=True),
        sg.Button("+", key="_analyzer_all_words_from_add", size=(2, 1), tooltip="Добавить слово в словарь")
    ],
    [sg.Listbox([], key="_analyzer_all_words", size=(150, 6))],
    [sg.Text("-- Обнаруженные словосочетания --")],
    [
        sg.InputText(key="_analyzer_words_combinations_search", size=(20, 1), tooltip="Поиск", enable_events=True),
        sg.Button("+", key="_analyzer_words_combinations_from_add", size=(2, 1), tooltip="Добавить слово в словарь")
    ],
    [sg.Listbox([], key="_analyzer_words_combinations", size=(150, 4))],
    [sg.Text("-- Ваш словарь (для редактирования) --")],
    [
        sg.InputText(key="_analyzer_words_dict_search", size=(20, 1), tooltip="Поиск", enable_events=True),
        sg.Button("-", key="_analyzer_dict_word_delete", size=(2, 1), tooltip="Удалить слово из словаря"),
        sg.Text(" | Добавление своего слова или словосочетания:"),
        sg.InputText(key="_analyzer_words_dict_word_adding_value", size=(25, 1)),
        sg.Button("+", key="_analyzer_dict_word_add", size=(2, 1), tooltip="Добавить слово")
    ],
    [sg.Listbox([], key="_analyzer_user_dict", size=(150, 6))],
    [
        sg.Button("Продолжить", key="_analyzer_final_analysis"),
        sg.Text("* Словарь не должен быть пустым!"),
    ]
]
layout = [
    [
        sg.Column(main_menu_column, key="_main_menu", visible=True),
        sg.Column(create_snapshot_column, key="_create_snapshot_menu", visible=False),
        sg.Column(snapshots_list_column, key="_snapshots_list_menu", visible=False),
        sg.Column(status_handler_column, key="_status_handler_menu", visible=False),
        sg.Column(analyzer_column, key="_analyzer_column_menu", visible=False)
    ]
]

status_mode = None
folder_id = None


def init(parser=None, analyzer=None):
    global status_mode
    global folder_id

    analyzer_words = []
    analyzer_combinations = []
    analyzer_user_dict = []

    window = sg.Window("Program", layout, size=(800, 600))
    while True:
        event, values = window.read()

        if event == "_create_snapshot":
            window['_main_menu'].update(visible = False)
            window['_create_snapshot_menu'].update(visible = True)
        if event == "_snapshots_list":
            window['_main_menu'].update(visible = False)
            window['_snapshots_list_menu'].update(visible = True)

        if event == "_enter_creating_snapshot":
            window['_create_snapshot_menu'].update(visible = False)
            proffesion = values['_proffesion_value']
            salary = values['_salary_value']
            region = values['_region_value']
            pages_count = values['_pages_count_value']
            search_full = values['_full_block_value']
            result = parser.start(proffesion, salary, region, pages_count, search_full)
            status_text = ""
            if len(result['errors']) > 0:
                status_text += f"Ошибки: {result['errors']}\n\n"
                status_mode = None
                folder_id = None
            else:
                status_text += f"id: {result['id']}\nПереход к обработке полученной информации.\n\n"
                status_mode = "analyzing_data"
                folder_id = result['id']
            window['_status_text'].update(f"{status_text}")
            window['_status_handler_menu'].update(visible = True)

        if event == "_status_ok":
            if status_mode == "analyzing_data":
                window['_status_handler_menu'].update(visible = False)
                result = analyzer.init(folder_id)
                if result:
                    analyzer_words = result['words']
                    analyzer_combinations = result['combinations']
                    window['_analyzer_all_words'].update(result['words'])
                    window['_analyzer_words_combinations'].update(result['combinations'])
                    window['_analyzer_column_menu'].update(visible = True)
                else:
                    analyzer_words = []
                    analyzer_combinations = []
                    analyzer_user_dict = []
                    window['_status_text'].update(f"Ошибка. Текст пуст.")
                    window['_status_handler_menu'].update(visible = True)
                    status_mode = None
            else:
                window['_status_handler_menu'].update(visible = False)
                window['_main_menu'].update(visible = True)

        if event == "_analyzer_all_words_search":
            val = values['_analyzer_all_words_search']
            tmp_arr = []
            for word in analyzer_words:
                if val in word:
                    tmp_arr.append(word)
            window['_analyzer_all_words'].update(tmp_arr)
        if event == "_analyzer_words_combinations_search":
            val = values['_analyzer_words_combinations_search']
            tmp_arr = []
            for word in analyzer_combinations:
                if val in word:
                    tmp_arr.append(word)
            window['_analyzer_words_combinations'].update(tmp_arr)
        if event == "_analyzer_words_dict_search":
            val = values['_analyzer_words_dict_search']
            tmp_arr = []
            for word in analyzer_user_dict:
                if val in word:
                    tmp_arr.append(word)
            window['_analyzer_user_dict'].update(tmp_arr)
        if event == "_analyzer_all_words_from_add":
            val = values['_analyzer_all_words']
            if len(val) > 0:
                if not val[0] in analyzer_user_dict:
                    analyzer_user_dict.append(val[0])
                    window['_analyzer_user_dict'].update(analyzer_user_dict)
        if event == "_analyzer_words_combinations_from_add":
            val = values['_analyzer_words_combinations']
            if len(val) > 0:
                if not val[0] in analyzer_user_dict:
                    analyzer_user_dict.append(val[0])
                    window['_analyzer_user_dict'].update(analyzer_user_dict)
        if event == "_analyzer_dict_word_add":
            val = values['_analyzer_words_dict_word_adding_value']
            if val != "" and val != " " and not val in analyzer_user_dict:
                analyzer_user_dict.append(val)
                window['_analyzer_user_dict'].update(analyzer_user_dict)
            window['_analyzer_words_dict_word_adding_value'].update('')
        if event == "_analyzer_dict_word_delete":
            val = values['_analyzer_user_dict']
            if len(val) > 0:
                analyzer_user_dict.remove(val[0])
                window['_analyzer_user_dict'].update(analyzer_user_dict)
        if event == "_analyzer_final_analysis":
            if len(analyzer_user_dict) > 0:
                result = analyzer.text_analysis(folder_id, analyzer_user_dict)

        if event != sg.WIN_CLOSED and "_back_to_menu" in event:
            window['_create_snapshot_menu'].update(visible = False)
            window['_snapshots_list_menu'].update(visible = False)
            window['_main_menu'].update(visible = True)
            pass
        if event == "_exit" or event == sg.WIN_CLOSED:
            break
    window.close()
    return True
