import requests
import json
import os


def translate_gg(text, src_lang='zh', tgt_lang='vi', proxy: str = None):
    proxies = {
        "http": proxy
    }
    tran = ''
    try:
        r = requests.get(
            'https://translate.googleapis.com/translate_a/single?client=gtx&sl=' + src_lang + '&tl=' + tgt_lang +
            '&dt=t&dt=bd&dj=1&q=' + text, proxies=proxies)
        if r.status_code == 200:
            resp = r.json()
            for j in resp['sentences']:
                tran += j['trans']
    except Exception as ve:
        print(ve)
    return tran.strip()

