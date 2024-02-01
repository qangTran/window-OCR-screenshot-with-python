import tkinter as tk
import webbrowser
from .config_manager import ConfigManager
from .text_processor import TextProcessor
from constants import APP_ICON_PATH


class SettingWindow:
    def __init__(self, master=None):
        self.config_manager = ConfigManager()
        self.config_manager.load_config()
        self.text_processor = TextProcessor()
        self.listener = None
        self.recording_shortcut = None

        # window ui
        self.root = tk.Tk() if master is None else tk.Toplevel(master)
        self.root.focus_force()
        self.root.title("OCR-S")
        self.root.configure(background="#f5f6fa")
        self.root.geometry("640x390+500+300")
        self.root['padx'] = 0
        self.root.resizable(True, True)
        self.root.iconbitmap(APP_ICON_PATH)

        # tk variables first setup
        self.label_combination_shortcut1 = tk.StringVar(value=self.convert_vk_pynput_to_string(
            [int(vk) for vk in self.config_manager.get_config("shortcut_to_snip1")]))
        self.label_combination_shortcut2 = tk.StringVar(value=self.convert_vk_pynput_to_string(
            [int(vk) for vk in self.config_manager.get_config("shortcut_to_snip2")]))
        self.method1_to_process_shortcut1 = tk.StringVar(
            value=self.config_manager.get_config("options_on_snip1")[0])
        self.method2_to_process_shortcut1 = tk.StringVar(
            value=self.config_manager.get_config("options_on_snip1")[1])
        self.method1_to_process_shortcut2 = tk.StringVar(
            value=self.config_manager.get_config("options_on_snip2")[0])
        self.method2_to_process_shortcut2 = tk.StringVar(
            value=self.config_manager.get_config("options_on_snip2")[1])
        self.label_button_record_shortcut1 = tk.StringVar(value="Record")
        self.label_button_record_shortcut2 = tk.StringVar(value="Record")
        self.in_read_shortcut1_mode = False
        self.in_read_shortcut2_mode = False
        self.checkbutton_use_shortcut1 = tk.IntVar(
            value=self.config_manager.get_config("use_shortcut1")[0])
        self.checkbutton_use_shortcut2 = tk.IntVar(
            value=self.config_manager.get_config("use_shortcut2")[0])
        self.checkbutton_start_with_window = tk.IntVar(
            value=self.config_manager.get_config("start_at_startup")[0])
        self.checkbutton_show_notification = tk.IntVar(
            value=self.config_manager.get_config("display_notification_after_cut")[0])
        self.options = sorted(
            list(self.text_processor.available_options.keys()))

        # listen to pressed case
        self.root.bind("<KeyPress>", self.key_down)

        # more ui setup
        self.setup_ui()

    def key_down(self, key):
        if self.in_read_shortcut1_mode:
            string_key = self.convert_vk_tkinter_to_string(key)
            if string_key in self.label_combination_shortcut1.get().split(" + "):
                return
            elif len(self.label_combination_shortcut1.get()) == 0:
                self.label_combination_shortcut1.set(
                    self.convert_vk_tkinter_to_string(key))
            else:
                self.label_combination_shortcut1.set(
                    self.label_combination_shortcut1.get() + " + " + string_key)
        elif self.in_read_shortcut2_mode:
            string_key = self.convert_vk_tkinter_to_string(key)
            if string_key in self.label_combination_shortcut2.get().split(" + "):
                return
            elif len(self.label_combination_shortcut2.get()) == 0:
                self.label_combination_shortcut2.set(
                    self.convert_vk_tkinter_to_string(key))
            else:
                self.label_combination_shortcut2.set(
                    self.label_combination_shortcut2.get() + " + " + string_key)

    def setup_ui(self):

        # main window layout ------------------------------------------
        self.root.rowconfigure(0, weight=3)  # Shortcut frame
        self.root.rowconfigure(1, weight=3)  # Systems frame
        self.root.rowconfigure(2, weight=1)  # Buttons
        self.root.columnconfigure(0, weight=1)

        # Define shortcut frame  ---------------------------------------
        self.Shortcut_Frame = tk.LabelFrame(self.root)
        self.Shortcut_Frame.configure(
            borderwidth=2, font="{g} 10 {bold}", text='Shortcuts', background="#f5f6fa")
        self.Shortcut_Frame.grid(column=0, padx=(
            15, 15), pady=15, row=0, sticky='snew')
        self.Shortcut_Frame.grid_propagate(False)
        self.Shortcut_Frame.columnconfigure(0, weight=1)  # check box
        self.Shortcut_Frame.columnconfigure(1, weight=2)  # shortcut result
        self.Shortcut_Frame.columnconfigure(2, weight=1)  # record button
        self.Shortcut_Frame.columnconfigure(3, weight=1)  # choose option
        self.Shortcut_Frame.columnconfigure(4, weight=1)  # choose option
        self.Shortcut_Frame.rowconfigure(0, weight=1)
        self.Shortcut_Frame.rowconfigure(1, weight=1)

        # Shortcut 1  --------------------------------------------------

        # Check button use shortcut1

        def checkbutton_use_shortcut_1_hover_effect_come(_):
            self.ShortCut_1.config(selectcolor="#d2dae2")

        def checkbutton_use_shortcut_1_hover_effect_leave(_):
            self.ShortCut_1.config(selectcolor="SystemButtonFace")

        self.ShortCut_1 = tk.Checkbutton(self.Shortcut_Frame, variable=self.checkbutton_use_shortcut1, onvalue=1,
                                         offvalue=0, )
        self.ShortCut_1.configure(
            background="#f5f6fa", text='Shortcut 1', font="{g} 11 ", )
        self.ShortCut_1.grid(column=0, row=0, sticky="snew", ipadx=10)
        self.ShortCut_1.bind(
            "<Enter>", checkbutton_use_shortcut_1_hover_effect_come)
        self.ShortCut_1.bind(
            "<Leave>", checkbutton_use_shortcut_1_hover_effect_leave)

        # Label shortcut2
        self.ShortCut_Place_1 = tk.Label(self.Shortcut_Frame, borderwidth=1, relief="solid",
                                         textvariable=self.label_combination_shortcut1)
        self.ShortCut_Place_1.configure(
            background="#ffffff", state="normal", width=26)
        self.ShortCut_Place_1.grid(column=1, padx=2, row=0, sticky="ew")

        # Button Record ShortCut1
        def cmd_record_shortcut_1():
            if not self.in_read_shortcut1_mode:
                self.label_combination_shortcut1.set("")
                self.label_button_record_shortcut1.set("Done")
                self.in_read_shortcut1_mode = True
            else:
                self.label_button_record_shortcut1.set("Record")
                self.in_read_shortcut1_mode = False

        def record_shortcut_1_hover_effect_come(_):
            self.Record_ShortCut_1["bg"] = "#bdc3c7"

        def record_shortcut_1_hover_effect_leave(_):
            self.Record_ShortCut_1["bg"] = "#ecf0f1"

        self.Record_ShortCut_1 = tk.Button(
            self.Shortcut_Frame, textvariable=self.label_button_record_shortcut1)
        self.Record_ShortCut_1.configure(background="#ecf0f1", default="active", font="{g} 10 ",
                                         command=cmd_record_shortcut_1, width=8)
        self.Record_ShortCut_1.grid(
            column=2, padx=5, pady=5, row=0, sticky="ew")
        self.Record_ShortCut_1.bind(
            "<Enter>", record_shortcut_1_hover_effect_come)
        self.Record_ShortCut_1.bind(
            "<Leave>", record_shortcut_1_hover_effect_leave)

        # Option1 for shortcut1
        self.Option_Shortcut_1 = tk.OptionMenu(
            self.Shortcut_Frame, self.method1_to_process_shortcut1, *self.options)
        self.Option_Shortcut_1.config(width=8)
        self.Option_Shortcut_1.grid(column=3, padx=(0, 5), row=0, sticky="ew")

        # Option2 for shortcut1
        self.Option_Shortcut_2 = tk.OptionMenu(
            self.Shortcut_Frame, self.method2_to_process_shortcut1, *self.options)
        self.Option_Shortcut_2.config(width=8)
        self.Option_Shortcut_2.grid(column=4, padx=(0, 5), row=0, sticky="ew")

        # Shortcut 2  ----------------------------------------------------

        # Check button shortcut 2

        def checkbutton_use_shortcut_2_hover_effect_come(_):
            self.ShortCut_2.config(selectcolor="#d2dae2")

        def checkbutton_use_shortcut_2_hover_effect_leave(_):
            self.ShortCut_2.config(selectcolor="SystemButtonFace")

        self.ShortCut_2 = tk.Checkbutton(self.Shortcut_Frame, variable=self.checkbutton_use_shortcut2, onvalue=1,
                                         offvalue=0)
        self.ShortCut_2.configure(
            background="#f5f6fa", text='Shortcut 2', font="{g} 11 ")
        self.ShortCut_2.grid(column=0, row=1, sticky="snew", ipadx=10)
        self.ShortCut_2.bind(
            "<Enter>", checkbutton_use_shortcut_2_hover_effect_come)
        self.ShortCut_2.bind(
            "<Leave>", checkbutton_use_shortcut_2_hover_effect_leave)

        # Label shortcut2
        self.ShortCut_Place_2 = tk.Label(self.Shortcut_Frame, borderwidth=1, relief="solid",
                                         textvariable=self.label_combination_shortcut2)
        self.ShortCut_Place_2.configure(
            background="#ffffff", state="normal", width=26)
        self.ShortCut_Place_2.grid(column=1, row=1, sticky="ew")

        # Button record shortcut2
        def cmd_record_shortcut_2():
            if not self.in_read_shortcut2_mode:
                self.label_combination_shortcut2.set("")
                self.label_button_record_shortcut2.set("Done")
                self.in_read_shortcut2_mode = True
            else:
                self.label_button_record_shortcut2.set("Record")
                self.in_read_shortcut2_mode = False

        def record_shortcut_2_hover_effect_come(_):
            self.Record_ShortCut_2["bg"] = "#bdc3c7"

        def record_shortcut_2_hover_effect_leave(_):
            self.Record_ShortCut_2["bg"] = "#ecf0f1"

        self.Record_ShortCut_2 = tk.Button(
            self.Shortcut_Frame, textvariable=self.label_button_record_shortcut2)
        self.Record_ShortCut_2.configure(background="#ecf0f1", default="active", font="{g} 10 ",
                                         command=cmd_record_shortcut_2, width=8)
        self.Record_ShortCut_2.grid(
            column=2, padx=5, pady=5, row=1, sticky="ew")
        self.Record_ShortCut_2.bind(
            "<Enter>", record_shortcut_2_hover_effect_come)
        self.Record_ShortCut_2.bind(
            "<Leave>", record_shortcut_2_hover_effect_leave)

        # Option for shortcut2
        self.Option1_Shortcut_2 = tk.OptionMenu(
            self.Shortcut_Frame, self.method1_to_process_shortcut2, *self.options)
        self.Option1_Shortcut_2.config(width=8)
        self.Option1_Shortcut_2.grid(column=3, padx=(0, 5), row=1, sticky="ew")

        # Option2 for shortcut1
        self.Option2_Shortcut_2 = tk.OptionMenu(
            self.Shortcut_Frame, self.method2_to_process_shortcut2, *self.options)
        self.Option2_Shortcut_2.config(width=8)
        self.Option2_Shortcut_2.grid(column=4, padx=(0, 5), row=1, sticky="ew")

        # System_Frame  ----------------------------------------------------

        self.System_Frame = tk.LabelFrame(self.root)
        self.System_Frame.configure(borderwidth=2, font="{g} 10 {bold}", text='Systems', background="#f5f6fa",
                                    height=15)
        self.System_Frame.columnconfigure(0, weight=1)
        self.System_Frame.columnconfigure(1, weight=2)
        self.System_Frame.columnconfigure(2, weight=2)
        self.System_Frame.columnconfigure(3, weight=2)
        self.System_Frame.rowconfigure(0, weight=1)
        self.System_Frame.rowconfigure(2, weight=1)

        self.System_Frame.grid(column=0, padx=(
            15, 15), pady=15, row=1, sticky="ewsn")
        self.System_Frame.grid_propagate(False)

        # Check button Start_At_Window
        def start_at_window_hover_effect_come(_):
            self.Start_At_Window.config(selectcolor="#d2dae2")

        def start_at_window_hover_effect_leave(_):
            self.Start_At_Window.config(selectcolor="SystemButtonFace")

        self.Start_At_Window = tk.Checkbutton(self.System_Frame, variable=self.checkbutton_start_with_window, onvalue=1,
                                              offvalue=0)
        self.Start_At_Window.configure(
            background="#f5f6fa", text='Start with window', font="{g} 11 ", )
        self.Start_At_Window.grid(
            column=0, row=0, columnspan=3, padx=(3, 0), sticky="w")
        self.Start_At_Window.bind("<Enter>", start_at_window_hover_effect_come)
        self.Start_At_Window.bind(
            "<Leave>", start_at_window_hover_effect_leave)

        # Check button Show_Notification
        def show_notification_hover_effect_come(_):
            self.Show_Notification.config(selectcolor="#d2dae2")

        def show_notification_hover_effect_leave(_):
            self.Show_Notification.config(selectcolor="SystemButtonFace", )

        self.Show_Notification = tk.Checkbutton(self.System_Frame, variable=self.checkbutton_show_notification,
                                                onvalue=1, offvalue=0)
        self.Show_Notification.configure(background="#f5f6fa", text='Show notification after complete a cut',
                                         font="{g} 11 ", )
        self.Show_Notification.grid(
            column=0, row=1, columnspan=3, padx=(3, 0), sticky="w")
        self.Show_Notification.bind(
            "<Enter>", show_notification_hover_effect_come)
        self.Show_Notification.bind(
            "<Leave>", show_notification_hover_effect_leave)

        # Button_Frame   ----------------------------------------------------
        self.Button_Frame = tk.Frame(self.root)
        self.Button_Frame.configure(
            background="#f5f6fa", height=120, padx=5, width=200)
        self.Button_Frame.grid(column=0, row=2, sticky="e")

        # Help_Button
        def help_button():
            webbrowser.open_new("https://www.facebook.com/Qangtran2002/")

        def help_button_hover_effect_come(_):
            self.Help_Button["bg"] = "#d4d4d4"

        def help_button_hover_effect_leave(_):
            self.Help_Button["bg"] = "SystemButtonFace"

        self.Help_Button = tk.Button(self.Button_Frame)
        self.Help_Button.configure(default="active", font="{g} 10 {bold}", text='Help', width=10,
                                   command=help_button)
        self.Help_Button.grid(column=0, row=0, sticky="w")
        self.Help_Button.bind("<Enter>", help_button_hover_effect_come)
        self.Help_Button.bind("<Leave>", help_button_hover_effect_leave)

        # Ok_Button
        def ok_button():
            self.config_manager.set_config("shortcut_to_snip1", self.convert_string_to_vk_pynput(
                self.label_combination_shortcut1.get()))
            self.config_manager.set_config("shortcut_to_snip2", self.convert_string_to_vk_pynput(
                self.label_combination_shortcut2.get()))
            self.config_manager.set_config("options_on_snip1", [
                                           self.method1_to_process_shortcut1.get(), self.method2_to_process_shortcut1.get()])
            self.config_manager.set_config("options_on_snip2", [
                                           self.method1_to_process_shortcut2.get(), self.method2_to_process_shortcut2.get()])
            self.config_manager.set_config(
                "use_shortcut1", [self.checkbutton_use_shortcut1.get()])
            self.config_manager.set_config(
                "use_shortcut2", [self.checkbutton_use_shortcut2.get()])
            self.config_manager.set_config(
                "start_at_startup", [self.checkbutton_start_with_window.get()])
            self.config_manager.set_config("display_notification_after_cut", [
                                           self.checkbutton_show_notification.get()])
            self.config_manager.save_config()
            self.root.destroy()

        def ok_button_hover_effect_come(_):
            self.Ok_Button["bg"] = "#d4d4d4"

        def ok_button_hover_effect_leave(_):
            self.Ok_Button["bg"] = "SystemButtonFace"

        self.Ok_Button = tk.Button(self.Button_Frame)
        self.Ok_Button.configure(default="active", font="{OK} 10 {bold}", foreground="#000000",
                                 highlightbackground="#000000", highlightcolor="#000000", text='OK', width=10,
                                 command=ok_button)
        self.Ok_Button.grid(column=1, padx=15, pady=10, row=0)
        self.Ok_Button.bind("<Enter>", ok_button_hover_effect_come)
        self.Ok_Button.bind("<Leave>", ok_button_hover_effect_leave)

        # Button Cancel
        def cancel_button():
            self.root.destroy()

        def cancel_button_hover_effect_come(_):
            self.Cancel["bg"] = "#d4d4d4"

        def cancel_button_hover_effect_leave(_):
            self.Cancel["bg"] = "SystemButtonFace"

        self.Cancel = tk.Button(self.Button_Frame)
        self.Cancel.configure(default="active", font="{Cancel} 10 {bold}", foreground="#000000",
                              highlightbackground="#000000", highlightcolor="#000000",
                              text='Cancel', width=10, command=cancel_button)
        self.Cancel.grid(column=2, row=0, padx=(0, 20))
        self.Cancel.bind("<Enter>", cancel_button_hover_effect_come)
        self.Cancel.bind("<Leave>", cancel_button_hover_effect_leave)

    def convert_vk_pynput_to_string(self, shortcut):
        map_vk_pynput_to_string = {162: "Ctrl", 160: "Shift", 164: "Alt"}
        return " + ".join([map_vk_pynput_to_string.get(key, chr(key)) for key in shortcut])

    def convert_vk_tkinter_to_string(self, key):
        map_vk_tkinter_to_string = {17: "Ctrl", 16: "Shift", 18: "Alt"}
        return map_vk_tkinter_to_string.get(key.keycode, chr(key.keycode))

    def convert_string_to_vk_pynput(self, string_shortcut):
        map_string_to_vk_pynput = {"Ctrl": 162, "Shift": 160, "Alt": 164}
        vks = []
        # vks = [map_string_to_vk_pynput.get(key, ord(key)) for key in string_shortcut.split(" + ")] # ! Note: strange error when using this
        for key in string_shortcut.split(" + "):
            if key in map_string_to_vk_pynput.keys():
                vks.append(map_string_to_vk_pynput[key])
            elif key.isalnum():
                vks.append(ord(key))
        return vks

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    SettingWindow().run()
