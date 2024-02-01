import os
from pystray import Icon, Menu, MenuItem
import PIL.Image
import pyperclip
from win10toast import ToastNotifier
from win32com.client import Dispatch
from utils.settings_window import SettingWindow
from utils.config_manager import ConfigManager
from utils.image_processor import ImageProcessor
from utils.text_processor import TextProcessor
from utils.shortcut_handler import ShortcutHandler
from constants import APP_ICON_PATH, ROOT_PATH, USER_NAME


class MainApp:
    def __init__(self):
        self.config_manager = ConfigManager()
        self.image_processor = ImageProcessor()
        self.text_processor = TextProcessor()
        self.shortcut_handler = ShortcutHandler()
        self.toaster = ToastNotifier()
        self.tray_icon = PIL.Image.open(APP_ICON_PATH)
        self.tray_menu = Menu(
            MenuItem('Settings', self.open_settings),
            MenuItem('New Snip 1', self.crop_and_process_section1),
            MenuItem('New Snip 2', self.crop_and_process_section2),
            MenuItem('Exit', self.exit_app))
        self.tray = Icon("OCR-S", self.tray_icon, menu=self.tray_menu)
        self.config_manager.load_config()
        self.load_and_start_shortcut()

    def load_and_start_shortcut(self):
        config = self.config_manager
        if int(config.get_config("use_shortcut1")[0]) and config.get_config('shortcut_to_snip1'):
            self.shortcut_handler.add_shortcut(config.get_config(
                'shortcut_to_snip1'), self.crop_and_process_section1)
        if int(config.get_config("use_shortcut2")[0]) and config.get_config('shortcut_to_snip2'):
            self.shortcut_handler.add_shortcut(config.get_config(
                'shortcut_to_snip2'), self.crop_and_process_section2)
        self.shortcut_handler.start_listen_shortcut()

    def crop_and_process_section1(self):
        self._crop_and_process("snip1")

    def crop_and_process_section2(self):
        self._crop_and_process("snip2")

    def _crop_and_process(self, snip):
        raw_text = self.image_processor.capture_and_process_image()
        if raw_text is not None:
            options = self.config_manager.get_config(f'options_on_{snip}')
            processed_text = self.text_processor.process_text(
                raw_text, options)
            pyperclip.copy(processed_text)
            pyperclip.paste()
            if self.config_manager.get_config("display_notification_after_cut")[0]:
                self.toaster.show_toast(f"Cropper {snip[-1]}: {', '.join(options)}", processed_text,
                                        icon_path=APP_ICON_PATH, duration=5, threaded=True)
        else:
            if self.config_manager.get_config("display_notification_after_cut")[0]:
                self.toaster.show_toast("Fail", "Find nothing to read",
                                        icon_path=APP_ICON_PATH, duration=2, threaded=True)

    def config_startup_using_shortcut(self, on):
        shortcut_dir = r'C:\Users\%s\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup' % USER_NAME
        # C:\Users\LENOVO\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\q-cropper.lnk
        shortcut_path = os.path.join(shortcut_dir, "OCR-S.lnk")
        if on:
            adjusted_root_path = ROOT_PATH[:-10]
            target = adjusted_root_path + "//OCR-S.exe"  # custom name of deployed app
            wDir = adjusted_root_path
            _icon = adjusted_root_path + "//OCR-S.exe"
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = target
            shortcut.WorkingDirectory = wDir
            shortcut.IconLocation = _icon
            shortcut.save()
        else:
            if os.path.isfile(shortcut_path):
                os.remove(shortcut_path)


    def open_settings(self):
        self.shortcut_handler.stop_listen_shortcut()
        SettingWindow().run() # This will block until the settings window is closed

        # Once the settings window is closed, reload config and shortcut listener
        self.config_manager.load_config()
        self.config_startup_using_shortcut(
            on=self.config_manager.get_config("start_at_startup")[0])
        self.shortcut_handler = ShortcutHandler()
        self.load_and_start_shortcut()

    def exit_app(self):
        self.tray.stop()
        os._exit(0)


if __name__ == "__main__":
    MainApp().tray.run()
