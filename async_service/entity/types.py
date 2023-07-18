from pydantic import BaseModel


class Input(BaseModel):
    hash_id: str = ""
    text: str = ""
    src_lang: str = ""
    tgt_lang: str = ""
    api_callback: str = ""


class Response(BaseModel):
    status: int = 1
    msg: str = ""
    res: dict = {"hash_id": "",
                 "src_lang": "",
                 "tgt_lang": "",
                 "text": "",
                 "text_tran": ""}


class InputSession(BaseModel):
    hash_id: str

class Output(BaseModel):
    query: dict = {}
    response: dict = {}