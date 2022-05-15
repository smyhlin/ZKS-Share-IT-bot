import json as jsonb
import os


def _(word: str, language='en') -> str:
    """
    We select user's language and adapted bot interface to it
    """
    try:
        try:  # it take lang telegram took to user
            with open(f'locales/{language}.json', encoding='utf-8') as json:
                w_dict = jsonb.load(json)
        except Exception:  # If error it choose english
            with open(f'locales/en.json', encoding='utf-8') as json:
                w_dict = jsonb.load(json)

        return w_dict[word]
    except Exception as error:  # if NONE such word / sentences
        print('word {} : lang {} missmatch\n\n{}'.format(word, language, error))
        return word
