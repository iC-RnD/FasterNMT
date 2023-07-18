LIST_LANGUAGES = ['zh', 'en', 'lo', 'km', 'id', 'ms', 'th', 'tl', 'ru', 'de', 'ja', 'ko']
LIST_TARGETS = ['vi']
LIST_TYPE = ['marian', 'm2m', 'mbart']

MAX_LENGTH = 128
MAX_LENGTH_EN = 128
MAX_LENGTH_ZH = 100

MANY2VI = {
    'en': {
        "source_lang": "en",
        "type": "m2m",
        "model_dir": "model/en-vi",
        "max_length": MAX_LENGTH_EN
    },
    'zh': {
        "source_lang": "zh",
        "type": "m2m",
        "model_dir": "model/zh-vi",
        "max_length": MAX_LENGTH_ZH
    },
    'other': {
        "source_lang": "other",
        "type": "m2m",
        "model_dir": "model/many-vi",
        "max_length": MAX_LENGTH
    }
}

TOKENIZER = 'model/m2m100_418M'
