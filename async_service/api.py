from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from entity import Response, Input, Output
from function import api
from config import get_config
from iclib import ICRabbitMQ

app = FastAPI(title="Translate")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

cfg = get_config()
QUEUE_NAME_ZH = cfg["ConfigManager"]["QueueConfigs"]["queue_translate_zh"]["Queue"]
QUEUE_NAME_EN = cfg["ConfigManager"]["QueueConfigs"]["queue_translate_en"]["Queue"]
QUEUE_NAME_OTHER = cfg["ConfigManager"]["QueueConfigs"]["queue_translate_other"]["Queue"]
QUEUE_EXCHANGE = ""
QUEUE_HOST = cfg["ConfigManager"]["QueueConfigs"]["queue_translate"]["HostName"]
QUEUE_PASSWORD = cfg["ConfigManager"]["QueueConfigs"]["queue_translate"]["Password"]
QUEUE_USERNAME = cfg["ConfigManager"]["QueueConfigs"]["queue_translate"]["UserName"]
QUEUE_VIRTUAL_HOST = cfg["ConfigManager"]["QueueConfigs"]["queue_translate"]["VirtualHost"]


@app.post("/api/translate/send")
def send_requests(item: Input):
    hash_id = item.hash_id
    if hash_id == "":
        hash_id = api.hash_session(item.__dict__)
    if item.src_lang == "en":
        QUEUE_NAME = QUEUE_NAME_EN
    elif item.src_lang == "zh":
        QUEUE_NAME = QUEUE_NAME_ZH
    else:
        QUEUE_NAME = QUEUE_NAME_OTHER
    rab = ICRabbitMQ(QUEUE_HOST, QUEUE_VIRTUAL_HOST, QUEUE_USERNAME, QUEUE_PASSWORD)
    print(QUEUE_HOST, QUEUE_VIRTUAL_HOST, QUEUE_USERNAME, QUEUE_PASSWORD)
    print(QUEUE_EXCHANGE, QUEUE_NAME)
    channel = rab.init_queue(QUEUE_NAME, exchange=QUEUE_EXCHANGE, max_priority=10)
    body_data = item.__dict__.copy()
    body_data["hash_id"] = hash_id
    ICRabbitMQ.publish_message(channel, QUEUE_NAME, body_data, exchange=QUEUE_EXCHANGE)
    return Response(status=1, msg="", res={"hash_id": hash_id})


@app.get("/api/translate/check")
def health_check():
    res = {}
    return Response(status=1, msg="", res=res)


@app.post("/api/translate/result")
def get_requests(item: Output):
    out = {"query": item.query, "response": item.response}
    print(item.response)
    return Response(status=1, msg="", res=out)
