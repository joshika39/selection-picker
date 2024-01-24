import os
from abc import abstractmethod
from pynput import keyboard
from .colors import *

Key = keyboard.Key

KEYS_ENTER = (Key.enter, b'\r', b'\n')
KEYS_UP = (Key.up, b'k')
KEYS_DOWN = (Key.down, b'j')
KEYS_SELECT = (Key.space, b'x', 'x')
KEYS_ESC = (Key.esc)
KEYS_SEARCH = (b's', b'f', 's', 'f')
KEYS_ALL = (b'a', 'a')


def clear():
    if os.name == 'nt':
        os.system('cls')
    elif os.name == 'posix':
        os.system('clear')


class KeyboardHandler:
    selected_key = None  # type: Key | None
    
    def __init__(self):
        pass

    def collect_key(self):
        with keyboard.Listener(on_press=self.on_press) as listener:
            listener.join()

    def on_press(self, key):
        self.selected_key = key
        return False  # stop listener


class Menu:
    def __init__(self, title: str, options: list, callback, search_engine, indicator: str, selected: int,
                 shown_content: int):
        self.title = title
        self.indicator = indicator
        self.indicator_space = ' ' * len(indicator)
        self.options = options
        self.selected = selected
        self.page = 0
        self.shown_content = shown_content
        self.callback = callback
        self.search_engine = search_engine
        self.all_options = options
        self.keyboard_handler = KeyboardHandler()

    def __str__(self):
        return self.title

    def action_check(self):
        self.keyboard_handler.collect_key()
        key = self.keyboard_handler.selected_key
        if key in KEYS_DOWN and self.selected + 1 < len(self.options):
            self.selected += 1
        if key in KEYS_UP and self.selected - 1 >= 0:
            self.selected -= 1
        if key in KEYS_SEARCH:
            clear()
            search_string = input("Search: ")
            if search_string == "":
                self.options = self.all_options
            elif self.search_engine is not None:
                self.options = self.search_engine(search_string, self.all_options)
            else:
                temp_list = []
                for elem in self.options:
                    if search_string.lower() in str(elem).lower():
                        temp_list.append(elem)
                self.options = temp_list
            if self.selected > len(self.options) - 1 and len(self.options) > 0:
                self.selected = len(self.options) - 1

        if self.selected >= self.page * self.shown_content + self.shown_content:
            self.page += 1
        elif self.selected <= (self.page * self.shown_content) - 1:
            self.page -= 1
        return key

    @abstractmethod
    def show(self, parent=''):
        pass


class FunctionItem:
    def __init__(self, title: str, callable):
        self.title = title
        self.callable = callable

    def __str__(self):
        return self.title


class SingleMenu(Menu):
    def __init__(self, title: str, options: list, callback=None, search_engine=None, indicator='->', selected=0,
                 shown_content=15):
        super().__init__(title, options, callback, search_engine, indicator, selected, shown_content)

    def show(self, parent=''):
        if parent != '':
            title = f'{parent} -> {self.title}'
        else:
            title = self.title
        move = None
        while move not in KEYS_ENTER or len(self.options) <= 0:
            clear()
            print(f'{title}')
            for index in range(self.page * self.shown_content, self.shown_content + self.page * self.shown_content):
                if index < len(self.options):
                    option = self.options[index]
                    if index == self.selected:
                        print(colorize(f'{self.indicator} {option}'))
                    else:
                        print(colorize(f'{self.indicator_space} {option}'))
            move = self.action_check()
            if move == Key.esc:
                return None
        if self.callback is not None:
            self.callback(self.options[self.selected])
        else:
            return self.options[self.selected]


class MultiMenu(Menu):
    def __init__(self, title: str, options: list, callback=None, search_engine=None, indicator='->', selected=0,
                 shown_content=15, select_open='[', select_close=']', select_mark='*', unselect_mark=' '):
        super().__init__(title, options, callback, search_engine, indicator, selected, shown_content)

        self.unselected = f'{select_open}{unselect_mark}{select_close}'
        self.selected_in = f'{select_open}{select_mark}{select_close}'

    def show(self, parent=''):
        if parent != '':
            title = f'{parent} -> {self.title}'
        else:
            title = self.title
        move = None
        selection = []
        while move not in KEYS_ENTER:
            clear()
            print(f'{title}')
            for index in range(self.page * self.shown_content, self.shown_content + self.page * self.shown_content):
                if index < len(self.options):
                    option = self.options[index]
                    if index == self.selected:
                        if option in selection:
                            print(colorize(f'{self.indicator} {self.selected_in} {option}'))
                        else:
                            print(colorize(f'{self.indicator} {self.unselected} {option}'))
                    else:
                        if option in selection:
                            print(colorize(f'{self.indicator_space} {self.selected_in} {option}'))
                        else:
                            print(colorize(f'{self.indicator_space} {self.unselected} {option}'))
            move = self.action_check()
            if move in KEYS_SELECT:
                if self.options[self.selected] in selection:
                    selection.remove(self.options[self.selected])
                else:
                    selection.append(self.options[self.selected])
            if move == Key.esc:
                return None
            if move == KEYS_ALL:
                if len(selection) < len(self.options):
                    selection = self.options
                elif len(selection) == len(self.options):
                    selection = []
        if self.callback is not None:
            self.callback(selection)
        else:
            return selection


class MenuWrapper(Menu):
    def __init__(self, title: str, options: list, indicator='->', selected=0, shown_content=15):
        super().__init__(title, options, None, None, indicator, selected, shown_content)

    def show(self, parent=''):
        if parent != '':
            title = f'{parent} -> {self.title}'
        else:
            title = self.title
        move = KEYS_ENTER[0]  # type: Key | None
        while move != Key.esc:
            clear()
            print(f'{title}')
            for index in range(self.page * self.shown_content, self.shown_content + self.page * self.shown_content):
                if index < len(self.options):
                    option = self.options[index]
                    if index == self.selected:
                        print(colorize(f'{self.indicator} {option}'))
                    else:
                        print(f'{self.indicator_space} {option}')
            move = self.action_check()
            if move in KEYS_ENTER:
                if type(self.options[self.selected]) == FunctionItem:
                    func = self.options[self.selected]  # type: FunctionItem
                    func.callable()

                if isinstance(self.options[self.selected], Menu):
                    menu = self.options[self.selected]  # type: Menu
                    menu.show(self.title)
