# from autocorrect import Speller
from googletrans import Translator
import time


class TextProcessor:
    def __init__(self):
        # Due to conflict between autocorrect and auto-py-to-exe, I turn off this feature,
        #   but if you run it with batch file to start the app, spell checker feature will be fine

        # self.spell_checker = Speller(only_replacements=True)
        self.translator = Translator()

        self.available_options = {
            "to lower": self.to_lower,
            "to upper": self.to_upper,
            # "autocorrect": self.autocorrect,
            "raw text": self.raw_text,
            "no endline": self.no_endline,
            "no space": self.no_space,
            "translate": self.translate,
            "capitalize": self.capitalize
        }

    def to_lower(self, text):
        return text.lower()

    def to_upper(self, text):
        return text.upper()

    def raw_text(self, text):
        return text

    def no_space(self, text):
        return text.replace(" ", "")

    # def autocorrect(self, text):
    #     return self.spell_checker(text)

    def no_endline(self, text):
        return text.replace("\n", " ")

    def capitalize(self, text):
        return text.title()

    def translate(self, text, src='en', dest='vi', max_retries=3):
        for _ in range(max_retries):
            try:
                response = self.translator.translate(text, src=src, dest=dest)
                if response.text:
                    return response.text
            except Exception as e:
                print(f"Translation error: {e}")
                time.sleep(0.5)  # Wait for a moment before retrying
        print("Translation failed after multiple attempts.")
        return text  # Return the original text if translation fails

    def process_text(self, text, options):
        """ Process the text based on the given options. """
        for option in options:
            text = self.available_options[option](text)
        return text
