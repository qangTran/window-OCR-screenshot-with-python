import json
import os
from constants import CONFIG_PATH

class ConfigManager:
    def __init__(self):
        self.config_path = CONFIG_PATH
        self.config = {}

    def load_config(self):
        """ Load the configuration from a setting file """
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as file:
                self.config = json.load(file)
        else:
            self.config = self.default_config()

    def save_config(self):
        """ Save the current configuration to a setting file """
        with open(self.config_path, 'w', encoding='utf-8') as file:
            json.dump(self.config, file, indent=4)

    def default_config(self):
        """ Return the default configuration """
        return {
            "shortcut_to_snip1": [162, 160, 78],
            "shortcut_to_snip2": [162, 81],
            "options_on_snip1": ["raw text", "raw text"],
            "options_on_snip2": ["raw text", "raw text"],
            "use_shortcut1": [True],
            "use_shortcut2": [True],
            "start_at_startup": [False],
            "display_notification_after_cut": [True]
        }

    def get_config(self, key):
        """ Get a specific configuration value """
        return self.config.get(key)

    def set_config(self, key, value):
        """ Set a specific configuration value """
        self.config[key] = value
