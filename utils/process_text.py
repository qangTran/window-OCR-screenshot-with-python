from autocorrect import Speller


def to_lower(text):
    return text.lower()


def to_upper(text):
    return text.upper()


def raw_text(text):
    return text


def no_space(text):
    return text.replace(" ", "")


def autocorrect(text):
    spell = Speller(only_replacements=True)
    return spell(text)


def no_endline(text: str):
    return text.replace("\n", " ")


available_options = {"to lower": to_lower,
                     "to upper": to_upper,
                     "autocorrect": autocorrect,
                     "raw text": raw_text,
                     "no endline": no_endline,
                     "no space": no_space,
                     }


def text_process(text: str, option: str) -> str:
    """receive `text` and `option` to process and return the processed string"""
    return available_options[option](text)
