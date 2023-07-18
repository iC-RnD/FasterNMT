LIST_LANGUAGES = ['zh', 'en']
LIST_TARGETS = ['vi']
LIST_TYPE=['marian', 'm2m', 'mbart']

MAX_LENGTH_EN=128
MAX_LENGTH_ZH=128

MANY2VI = {
    'en': {
        "source_lang": "en",
        "type": "m2m",
        "model": "./models/en-vi",
        "max_length": MAX_LENGTH_EN
    },
    'zh': {
        "source_lang": "zh",
        "type": "m2m",
        "model": "./models/zh-vi",
        "max_length": MAX_LENGTH_ZH
    }
}

TOKENIZER = 'facebook/m2m100_418M'

