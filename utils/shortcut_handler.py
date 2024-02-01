from pynput import keyboard
import random

class ShortcutHandler:
    def __init__(self):
        self.shortcuts = {}
        self.pressed_keys = set()
        self.listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)

    def add_shortcut(self, key_combination: list, action):
        self.shortcuts[frozenset(key_combination)] = action

    def remove_shortcut(self, key_combination: list):
        self.shortcuts.pop(frozenset(key_combination), None)

    def get_vk(self, key):
        """
        Get the virtual key code from a key.
        These are used so case/shift modifications are ignored.
        """
        return key.vk if hasattr(key, 'vk') else key.value.vk

    def on_press(self, key):
        """ When a key is pressed """
        vk = self.get_vk(key)
        # print('vk =', vk) # for test
        self.pressed_keys.add(vk)
        self.check_and_execute() 

    def on_release(self, key):
        """ When a key is released """
        vk = self.get_vk(key)
        self.pressed_keys.discard(vk)  # Remove it from the set of currently pressed keys

    def check_and_execute(self):
        """ Check if any shortcut combination is pressed and execute the action. """
        for keys, action in self.shortcuts.items():
            if keys.issubset(self.pressed_keys):
                action()
                self.pressed_keys.clear()  # Clear pressed keys after action
                break

    def start_listen_shortcut(self):
        """ Start the keyboard listener. """
        self.listener.start()

    def stop_listen_shortcut(self):
        """ Stop the keyboard listener. """
        self.listener.stop()
