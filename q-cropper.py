import getpass
import json
import os
import tkinter as tk
import webbrowser

import PIL.Image
import pyperclip
import pystray
from pynput.keyboard import KeyCode, Listener
from win10toast import ToastNotifier
from win32com.client import Dispatch

from utils import process_text, process_image

ROOT_PATH = os.path.realpath(os.path.dirname(__file__))
USER_NAME = getpass.getuser()
setting_is_activating = False
toaster = ToastNotifier()


class SettingWindow:
    def __init__(self, master=None):

        self.main_window_padding_size = 0

        self.main_window = tk.Tk() if master is None else tk.Toplevel(master)
        self.main_window.focus_force()
        self.main_window.title("Settings")
        self.main_window.configure(background="#f5f6fa")
        self.main_window.geometry("640x390+500+300")
        self.main_window['padx'] = self.main_window_padding_size
        self.main_window.resizable(True, True)
        self.main_window.iconbitmap(f"{ROOT_PATH}/data/app image/app_icon.ico")

        # main window layout
        self.main_window.rowconfigure(0, weight=3)
        self.main_window.rowconfigure(1, weight=3)
        self.main_window.rowconfigure(2, weight=1)
        self.main_window.columnconfigure(0, weight=1)

        # tk_Var
        self.text_shortcut1 = tk.StringVar()
        self.text_shortcut2 = tk.StringVar()
        self.checkbutton_use_shortcut1 = tk.IntVar()
        self.checkbutton_use_shortcut2 = tk.IntVar()
        self.method1_to_process_shortcut1 = tk.StringVar()
        self.method2_to_process_shortcut1 = tk.StringVar()
        self.method1_to_process_shortcut2 = tk.StringVar()
        self.method2_to_process_shortcut2 = tk.StringVar()
        self.text_button1_mode = tk.StringVar(value="Record")
        self.text_button2_mode = tk.StringVar(value="Record")
        self.in_read_shortcut1_mode = False
        self.in_read_shortcut2_mode = False
        self.checkbutton_start_with_window = tk.IntVar()
        self.checkbutton_show_notification = tk.IntVar()
        self.button_OK_is_clicked = tk.IntVar()
        self.options = sorted(list(process_text.available_options.keys()))

        def key_down(key):
            if self.in_read_shortcut1_mode:
                string_key = convert_vk_tkinter_to_string(key)
                if string_key in self.text_shortcut1.get().split(" + "):
                    return
                elif len(self.text_shortcut1.get()) == 0:
                    self.text_shortcut1.set(convert_vk_tkinter_to_string(key))
                else:
                    self.text_shortcut1.set(self.text_shortcut1.get() + " + " + string_key)
            if self.in_read_shortcut2_mode:
                string_key = convert_vk_tkinter_to_string(key)
                if string_key in self.text_shortcut2.get().split(" + "):
                    return
                elif len(self.text_shortcut2.get()) == 0:
                    self.text_shortcut2.set(convert_vk_tkinter_to_string(key))
                else:
                    self.text_shortcut2.set(self.text_shortcut2.get() + " + " + string_key)

        self.main_window.bind("<KeyPress>", key_down)

        # Define shortcut frame
        self.Shortcut_Frame = tk.LabelFrame(self.main_window)
        self.Shortcut_Frame.configure(borderwidth=2, font="{g} 10 {bold}", text='Shortcuts', background="#f5f6fa")
        self.Shortcut_Frame.grid(column=0, padx=(15, 15), pady=15, row=0, sticky='snew')
        self.Shortcut_Frame.grid_propagate(False)
        self.Shortcut_Frame.columnconfigure(0, weight=1)  # check box
        self.Shortcut_Frame.columnconfigure(1, weight=2)  # shortcut result
        self.Shortcut_Frame.columnconfigure(2, weight=1)  # record
        self.Shortcut_Frame.columnconfigure(3, weight=1)  # choose option
        self.Shortcut_Frame.columnconfigure(4, weight=1)  # choose option
        self.Shortcut_Frame.rowconfigure(0, weight=1)
        self.Shortcut_Frame.rowconfigure(1, weight=1)

        def convert_vk_tkinter_to_string(key):
            map_to_string = {17: "Ctrl", 16: "Shift", 18: "Alt"}
            string_key = map_to_string.get(key.keycode, chr(key.keycode))
            return string_key

        # Record shortcut 1

        # Check button use shortcut1
        def ShortCut_1_Hover_Effect_Come(_):
            self.ShortCut_1.config(selectcolor="#d2dae2")

        def ShortCut_1_Hover_Effect_Leave(_):
            self.ShortCut_1.config(selectcolor="SystemButtonFace")

        self.ShortCut_1 = tk.Checkbutton(self.Shortcut_Frame, variable=self.checkbutton_use_shortcut1, onvalue=1,
                                         offvalue=0)
        self.ShortCut_1.configure(background="#f5f6fa", text='Shortcut 1', font="{g} 11 ", )
        self.ShortCut_1.grid(column=0, row=0, sticky="snew")
        self.ShortCut_1.bind("<Enter>", ShortCut_1_Hover_Effect_Come)
        self.ShortCut_1.bind("<Leave>", ShortCut_1_Hover_Effect_Leave)

        # Label shortcut2
        self.ShortCut_Place_1 = tk.Label(self.Shortcut_Frame, borderwidth=1, relief="solid",
                                         textvariable=self.text_shortcut1)
        self.ShortCut_Place_1.configure(
            background="#ffffff", state="normal", width=26)
        self.ShortCut_Place_1.grid(column=1, padx=2, row=0, sticky="ew")

        # Button Record ShortCut1
        def cmd_Record_ShortCut_1():
            if not self.in_read_shortcut1_mode:
                self.text_shortcut1.set("")
                self.text_button1_mode.set("Done")
                self.in_read_shortcut1_mode = True
            else:
                self.text_button1_mode.set("Record")
                self.in_read_shortcut1_mode = False

        def Record_ShortCut_1_Hover_Effect_Come(_):
            self.Record_ShortCut_1["bg"] = "#bdc3c7"

        def Record_ShortCut_1_Hover_Effect_Leave(_):
            self.Record_ShortCut_1["bg"] = "#ecf0f1"

        self.Record_ShortCut_1 = tk.Button(self.Shortcut_Frame, textvariable=self.text_button1_mode)
        self.Record_ShortCut_1.configure(background="#ecf0f1", default="active", font="{g} 10 ",
                                         command=cmd_Record_ShortCut_1, width=8)
        self.Record_ShortCut_1.grid(column=2, padx=5, pady=5, row=0, sticky="ew")

        self.Record_ShortCut_1.bind("<Enter>", Record_ShortCut_1_Hover_Effect_Come)
        self.Record_ShortCut_1.bind("<Leave>", Record_ShortCut_1_Hover_Effect_Leave)

        # Option1 for shortcut1
        self.Option_Shortcut_1 = tk.OptionMenu(self.Shortcut_Frame, self.method1_to_process_shortcut1, *self.options)
        self.Option_Shortcut_1.config(width=8)
        self.Option_Shortcut_1.grid(column=3, padx=(0, 5), row=0, sticky="ew")

        # Option2 for shortcut1
        self.Option_Shortcut_2 = tk.OptionMenu(self.Shortcut_Frame, self.method2_to_process_shortcut1, *self.options)
        self.Option_Shortcut_2.config(width=8)
        self.Option_Shortcut_2.grid(column=4, padx=(0, 5), row=0, sticky="ew")

        # Record ShortCut 2

        # Check button shortcut 2
        def ShortCut_2_Hover_Effect_Come(_):
            self.ShortCut_2.config(selectcolor="#d2dae2")

        def ShortCut_2_Hover_Effect_Leave(_):
            self.ShortCut_2.config(selectcolor="SystemButtonFace")

        self.ShortCut_2 = tk.Checkbutton(self.Shortcut_Frame, variable=self.checkbutton_use_shortcut2, onvalue=1,
                                         offvalue=0)
        self.ShortCut_2.configure(background="#f5f6fa", text='Shortcut 2', font="{g} 11 ")
        self.ShortCut_2.grid(column=0, row=1, sticky="snew")
        self.ShortCut_2.bind("<Enter>", ShortCut_2_Hover_Effect_Come)
        self.ShortCut_2.bind("<Leave>", ShortCut_2_Hover_Effect_Leave)

        # Label shortcut2
        self.ShortCut_Place_2 = tk.Label(self.Shortcut_Frame, borderwidth=1, relief="solid",
                                         textvariable=self.text_shortcut2)
        self.ShortCut_Place_2.configure(
            background="#ffffff", state="normal", width=26)
        self.ShortCut_Place_2.grid(column=1, row=1, sticky="ew")

        # Button record shortcut2
        def cmd_Record_ShortCut_2():
            if not self.in_read_shortcut2_mode:
                self.text_shortcut2.set("")
                self.text_button2_mode.set("Done")
                self.in_read_shortcut2_mode = True
            else:
                self.text_button2_mode.set("Record")
                self.in_read_shortcut2_mode = False

        def Record_ShortCut_2_Hover_Effect_Come(_):
            self.Record_ShortCut_2["bg"] = "#bdc3c7"

        def Record_ShortCut_2_Hover_Effect_Leave(_):
            self.Record_ShortCut_2["bg"] = "#ecf0f1"

        self.Record_ShortCut_2 = tk.Button(self.Shortcut_Frame, textvariable=self.text_button2_mode)
        self.Record_ShortCut_2.configure(background="#ecf0f1", default="active", font="{g} 10 ",
                                         command=cmd_Record_ShortCut_2, width=8)
        self.Record_ShortCut_2.grid(column=2, padx=5, pady=5, row=1, sticky="ew")
        self.Record_ShortCut_2.bind("<Enter>", Record_ShortCut_2_Hover_Effect_Come)
        self.Record_ShortCut_2.bind("<Leave>", Record_ShortCut_2_Hover_Effect_Leave)

        # Option for shortcut2
        self.Option1_Shortcut_2 = tk.OptionMenu(self.Shortcut_Frame, self.method1_to_process_shortcut2, *self.options)
        self.Option1_Shortcut_2.config(width=8)
        self.Option1_Shortcut_2.grid(column=3, padx=(0, 5), row=1, sticky="ew")

        # Option2 for shortcut1 **
        self.Option2_Shortcut_2 = tk.OptionMenu(self.Shortcut_Frame, self.method2_to_process_shortcut2, *self.options)
        self.Option2_Shortcut_2.config(width=8)
        self.Option2_Shortcut_2.grid(column=4, padx=(0, 5), row=1, sticky="ew")

        # System_Frame
        self.System_Frame = tk.LabelFrame(self.main_window)
        self.System_Frame.configure(borderwidth=2, font="{g} 10 {bold}", text='Systems', background="#f5f6fa",
                                    height=15)
        self.System_Frame.columnconfigure(0, weight=1)
        self.System_Frame.columnconfigure(1, weight=2)
        self.System_Frame.columnconfigure(2, weight=2)
        self.System_Frame.columnconfigure(3, weight=2)
        self.System_Frame.rowconfigure(0, weight=1)
        self.System_Frame.rowconfigure(2, weight=1)

        self.System_Frame.grid(column=0, padx=(15, 15), pady=15, row=1, sticky="ewsn")
        self.System_Frame.grid_propagate(False)

        # Check button Start_At_Window
        def Start_At_Window_Hover_Effect_Come(_):
            self.Start_At_Window.config(selectcolor="#d2dae2")

        def Start_At_Window_Hover_Effect_Leave(_):
            self.Start_At_Window.config(selectcolor="SystemButtonFace")

        self.Start_At_Window = tk.Checkbutton(self.System_Frame, variable=self.checkbutton_start_with_window, onvalue=1,
                                              offvalue=0)
        self.Start_At_Window.configure(
            background="#f5f6fa", text='Start with window', font="{g} 11 ", )
        self.Start_At_Window.grid(column=0, row=0, columnspan=3, padx=(3, 0), sticky="w")
        self.Start_At_Window.bind("<Enter>", Start_At_Window_Hover_Effect_Come)
        self.Start_At_Window.bind("<Leave>", Start_At_Window_Hover_Effect_Leave)

        # Check button Show_Notification
        def Show_Notification_Hover_Effect_Come(_):
            self.Show_Notification.config(selectcolor="#d2dae2")

        def Show_Notification_Hover_Effect_Leave(_):
            self.Show_Notification.config(selectcolor="SystemButtonFace", )

        self.Show_Notification = tk.Checkbutton(self.System_Frame, variable=self.checkbutton_show_notification,
                                                onvalue=1, offvalue=0)
        self.Show_Notification.configure(background="#f5f6fa", text='Show notification after complete a cut',
                                         font="{g} 11 ", )
        self.Show_Notification.grid(column=0, row=1, columnspan=3, padx=(3, 0), sticky="w")
        self.Show_Notification.bind("<Enter>", Show_Notification_Hover_Effect_Come)
        self.Show_Notification.bind("<Leave>", Show_Notification_Hover_Effect_Leave)

        # Button_Frame
        self.Button_Frame = tk.Frame(self.main_window)
        self.Button_Frame.configure(
            background="#f5f6fa", height=120, padx=5, width=200)
        self.Button_Frame.grid(column=0, row=2, sticky="e")

        # Help_Button
        def Help_Button():
            webbrowser.open_new("google.com")

        def Help_Button_Hover_Effect_Come(_):
            self.Help_Button["bg"] = "#d4d4d4"

        def Help_Button_Hover_Effect_Leave(_):
            self.Help_Button["bg"] = "SystemButtonFace"

        self.Help_Button = tk.Button(self.Button_Frame)
        self.Help_Button.configure(default="active", font="{g} 10 {bold}", text='Help', width=10,
                                   command=Help_Button)
        self.Help_Button.grid(column=0, row=0, sticky="w")
        self.Help_Button.bind("<Enter>", Help_Button_Hover_Effect_Come)
        self.Help_Button.bind("<Leave>", Help_Button_Hover_Effect_Leave)

        # Ok_Button
        def Ok_Button():
            self.button_OK_is_clicked.set(1)
            self.main_window.destroy()

        def Ok_Button_Hover_Effect_Come(_):
            self.Ok_Button["bg"] = "#d4d4d4"

        def Ok_Button_Hover_Effect_Leave(_):
            self.Ok_Button["bg"] = "SystemButtonFace"

        self.Ok_Button = tk.Button(self.Button_Frame)
        self.Ok_Button.configure(default="active", font="{OK} 10 {bold}", foreground="#000000",
                                 highlightbackground="#000000", highlightcolor="#000000", text='OK', width=10,
                                 command=Ok_Button)
        self.Ok_Button.grid(column=1, padx=15, pady=10, row=0)
        self.Ok_Button.bind("<Enter>", Ok_Button_Hover_Effect_Come)
        self.Ok_Button.bind("<Leave>", Ok_Button_Hover_Effect_Leave)

        # Button Cancel
        def Cancel_Button():
            self.main_window.destroy()

        def Cancel_Button_Hover_Effect_Come(_):
            self.Cancel["bg"] = "#d4d4d4"

        def Cancel_Button_Hover_Effect_Leave(_):
            self.Cancel["bg"] = "SystemButtonFace"

        self.Cancel = tk.Button(self.Button_Frame)
        self.Cancel.configure(default="active", font="{Cancel} 10 {bold}", foreground="#000000",
                              highlightbackground="#000000", highlightcolor="#000000",
                              text='Cancel', width=10, command=Cancel_Button)
        self.Cancel.grid(column=2, row=0, padx=(0, 20))
        self.Cancel.bind("<Enter>", Cancel_Button_Hover_Effect_Come)
        self.Cancel.bind("<Leave>", Cancel_Button_Hover_Effect_Leave)

    def run(self):
        self.main_window.mainloop()


# Set up config
def read_config():
    # ---- (read option from file) ---
    with open(f'{ROOT_PATH}/data/setup/setup.json', 'r', encoding='utf-8') as file:
        config_ = json.load(file)
    return config_


def config_startup(on):
    shortcut_dir = r'C:\Users\%s\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup' % USER_NAME
    shortcut_path = os.path.join(shortcut_dir, "q-cropper.lnk")  # custom deployed app name
    # C:\Users\LENOVO\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\q-cropper.lnk

    if on:
        # test get file path of output program later as `target`
        target = ROOT_PATH + "//q-cropper.exe"  # custom name of deployed app
        wDir = ROOT_PATH
        _icon = ROOT_PATH + "//q-cropper.exe"
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = target
        shortcut.WorkingDirectory = wDir
        shortcut.IconLocation = _icon
        shortcut.save()
    else:
        if os.path.isfile(shortcut_path):
            os.remove(shortcut_path)


config = read_config()
# config_startup(config["start_at_startup"][0])  # only for deployed app


# stray configuration
def stray_on_clicked(icon_, item):
    if str(item) == "Setting":
        if not setting_is_activating:
            setting_section()
    elif str(item) == "New cut 1":
        crop_section1()
    elif str(item) == "New cut 2":
        crop_section2()
    elif str(item) == "Exit":
        icon_.stop()
        exit()


app_icon_path = f"{ROOT_PATH}/data/app image/app_icon.ico"
app_icon = PIL.Image.open(app_icon_path)
icon = pystray.Icon("Q_snip", app_icon, menu=pystray.Menu(
    pystray.MenuItem("Setting", stray_on_clicked),
    pystray.MenuItem("New cut 1", stray_on_clicked),
    pystray.MenuItem("New cut 2", stray_on_clicked),
    pystray.MenuItem("Exit", stray_on_clicked),
))


def crop_section1():
    raw_text = process_image.crop()
    if raw_text is None:
        if config["display_notification_after_cut"][0]:
            toaster.show_toast("Fail", "Find nothing to read",
                               icon_path=f"{ROOT_PATH}/data/app image/app_icon.ico", duration=5, threaded=True)
        return
    result = process_text.text_process(raw_text, config["options_on_snip1"][0])
    result = process_text.text_process(result, config["options_on_snip1"][1])
    # paste to clipboard
    pyperclip.copy(result)
    pyperclip.paste()

    if config["display_notification_after_cut"][0]:
        toaster.show_toast(f"Cropper 1: {', '.join(config['options_on_snip1'])}", result,
                           icon_path=f"{ROOT_PATH}/data/app image/app_icon.ico", duration=5, threaded=True)


def crop_section2():
    raw_text = process_image.crop()
    if raw_text is None:
        if config["display_notification_after_cut"][0]:
            toaster.show_toast("Fail", "Find nothing to read",
                               icon_path=f"{ROOT_PATH}/data/app image/app_icon.ico", duration=5, threaded=True)
        return
    result = process_text.text_process(raw_text, config["options_on_snip2"][0])
    result = process_text.text_process(result, config["options_on_snip2"][1])
    # paste to clipboard
    pyperclip.copy(result)
    pyperclip.paste()

    if config["display_notification_after_cut"][0]:
        toaster.show_toast(f"Cropper 2: {', '.join(config['options_on_snip2'])}", result,
                           icon_path=f"{ROOT_PATH}/data/app image/app_icon.ico", duration=5, threaded=True)


def read_shortcut_from_config():
    shortcut_to_function_ = dict()
    if config["use_shortcut1"][0]:
        shortcut1 = [KeyCode(vk=int(vk)) for vk in
                     config["shortcut_to_snip1"]]  # list of int value which is virtual key of keyboard
        # check if shortcut is assigned
        if len(shortcut1) > 1:
            shortcut_to_function_[frozenset(shortcut1)] = crop_section1

    if config["use_shortcut2"][0]:
        shortcut2 = [KeyCode(vk=int(vk)) for vk in config["shortcut_to_snip2"]]
        # check if shortcut is assigned
        if len(shortcut2) > 1:
            shortcut_to_function_[frozenset(shortcut2)] = crop_section2
    return shortcut_to_function_


shortcut_to_function = read_shortcut_from_config()


def convert_vk_to_string(shortcut):
    map_to_string = {162: "Ctrl", 160: "Shift", 164: "Alt"}
    string_shortcut = [map_to_string.get(key, chr(key)) for key in shortcut]
    return " + ".join(string_shortcut)


def convert_string_to_vk(string_shortcut):
    map_to_string = {"Ctrl": 162, "Shift": 160, "Alt": 164}
    vks = []
    # TODO : strange error with
    # vks = [map_to_string.get(key, ord(key)) for key in string_shortcut.split(" + ")]
    for key in string_shortcut.split(" + "):
        if key in map_to_string.keys():
            vks.append(map_to_string[key])
        elif key.isalnum():
            vks.append(ord(key))
    return vks


def setting_section():
    global setting_is_activating
    global shortcut_to_function
    setting_is_activating = True

    # disable listener shortcut
    shortcut_to_function.clear()

    app = SettingWindow()
    # read start state
    app.button_OK_is_clicked.set(0)
    app.text_shortcut1.set(convert_vk_to_string([int(vk) for vk in config["shortcut_to_snip1"]]))
    app.text_shortcut2.set(convert_vk_to_string([int(vk) for vk in config["shortcut_to_snip2"]]))
    app.checkbutton_use_shortcut1.set(config["use_shortcut1"][0])
    app.checkbutton_use_shortcut2.set(config["use_shortcut2"][0])
    app.checkbutton_start_with_window.set(config["start_at_startup"][0])
    app.checkbutton_show_notification.set(config["display_notification_after_cut"][0])
    app.method1_to_process_shortcut1.set(config["options_on_snip1"][0])
    app.method2_to_process_shortcut1.set(config["options_on_snip1"][1])
    app.method1_to_process_shortcut2.set(config["options_on_snip2"][0])
    app.method2_to_process_shortcut2.set(config["options_on_snip2"][1])
    app.run()  # init n mainloop

    if app.button_OK_is_clicked.get():
        config["shortcut_to_snip1"] = convert_string_to_vk(app.text_shortcut1.get())
        config["shortcut_to_snip2"] = convert_string_to_vk(app.text_shortcut2.get())
        config["options_on_snip1"] = [app.method1_to_process_shortcut1.get(), app.method2_to_process_shortcut1.get()]
        config["options_on_snip2"] = [app.method1_to_process_shortcut2.get(), app.method2_to_process_shortcut2.get()]
        config["use_shortcut1"] = [app.checkbutton_use_shortcut1.get()]
        config["use_shortcut2"] = [app.checkbutton_use_shortcut2.get()]
        config["start_at_startup"] = [app.checkbutton_start_with_window.get()]
        config["display_notification_after_cut"] = [app.checkbutton_show_notification.get()]

        shortcut_to_function = read_shortcut_from_config()

        with open(f'{ROOT_PATH}/data/setup/setup.json', 'w', encoding='utf-8') as file:
            json.dump(config, file)

    # re-activate listener shortcut
    shortcut_to_function = read_shortcut_from_config()

    # only for deployed app
    # config_startup(on=config["start_at_startup"][0])

    setting_is_activating = False


# The currently pressed keys (initially empty)
pressed_vks = set()


def get_vk(key):
    """
    Get the virtual key code from a key.
    These are used so case/shift modifications are ignored.
    """
    return key.vk if hasattr(key, 'vk') else key.value.vk


def is_combination_pressed(combination):
    """ Check if a combination is satisfied using the keys pressed in pressed_vks """
    return all([get_vk(key) in pressed_vks for key in combination])


def on_press(key):
    """ When a key is pressed """

    # printed pressed key
    # vk2 = key.vk if hasattr(key, 'vk') else key.value.vk
    # print('vk =', vk2)

    vk = get_vk(key)  # Get the key's vk
    pressed_vks.add(vk)  # Add it to the set of currently pressed keys

    for combination in shortcut_to_function:  # Loop through each combination
        if is_combination_pressed(combination):  # Check if all keys in the combination are pressed
            shortcut_to_function[combination]()  # If so, execute the function
            pressed_vks.clear()  # after done remove all captured key

    # if listen_snip_shortcut is False:
    #     return False


def on_release(key):
    """ When a key is released """
    vk = get_vk(key)  # Get the key's vk
    pressed_vks.discard(vk)  # Remove it from the set of currently pressed keys


listener = Listener(on_press=on_press, on_release=on_release)

if __name__ == "__main__":
    listener.start()
    icon.run()
