
```python
MANY2VI = {
    'en': {
        "source_lang": "en",
        "type": "m2m",
        "model_dir": "models/CT2en2vi",
        "max_length": MAX_LENGTH_EN
    },
    'zh': {
        "source_lang": "zh",
        "type": "m2m",
        "model_dir": "models/CT2zh2vi_WMTall",
        "max_length": MAX_LENGTH_ZH
    },
    'other': {
        "source_lang": "other",
        "type": "m2m",
        "model_dir": "models/ct2many2vi",
        "max_length": MAX_LENGTH
    }
}

TOKENIZER = 'tokenizer/m2m100_418M'
```