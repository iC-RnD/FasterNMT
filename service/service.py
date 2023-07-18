import inference
from fastapi import FastAPI, Response, status, BackgroundTasks, HTTPException
from pydantic import BaseModel
import config as cfg
import time

EN_translator = inference.many2vi('en')
ZH_translator = inference.many2vi('zh')

description = """
    ## code languages
        en: English/
        zh: Chinese
"""

app = FastAPI(
    title="Translator enzh2vi",
    description=description,
    version="0.0.1"
)

class Content(BaseModel):
    doc: str = "Hello World!"
    src_lang: str = "en"
    tgt_lang: str = "vi"

@app.post("/translate_enzh2vi")
async def translate_enzh2vi(response: Response, doc: str, src_lang: str):
    if src_lang.lower() not in cfg.LIST_LANGUAGES:
        raise HTTPException(status_code=400, detail="language not support")
    try:
        stime = time.time()
        doc_translated = ""
        if src_lang == 'en':
            doc_translated = EN_translator.infer(doc)
        elif src_lang == 'zh':
            doc_translated = ZH_translator.infer(doc)

        return {"result": doc_translated, 'language_dict': [src_lang, 'vi'],
                'time_run': time.time() - stime, "code": 1, "message": "success"}
    except Exception as ve:
        print(ve)
        results = {'message': str(ve), 'code': -1}
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

        return results

@app.post("/translate_enzh2vi_content")
async def translate_enzh2vi_content(response: Response, item: Content):
    src_lang = item.src_lang
    if src_lang.lower() not in cfg.LIST_LANGUAGES:
        raise HTTPException(status_code=400, detail="language not support")

    stime = time.time()
    doc_translated = ""
    doc = item.doc
    if src_lang == 'en':
            doc_translated = EN_translator.infer(doc)
    elif src_lang == 'zh':
            doc_translated = ZH_translator.infer(doc)

    return {"result": doc_translated, 'language_dict': [item.src_lang, item.tgt_lang],
                'time_run': time.time() - stime, "code": 1, "message": "success"}
