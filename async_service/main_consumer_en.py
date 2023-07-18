from config import get_config
from iclib import ICRabbitMQ
import requests
from translate_inference import inference
from fastapi import HTTPException
import translate_inference.config as config
import nltk
import time
import sys
import logging
from logging.handlers import RotatingFileHandler

nltk.download('punkt')
log_formatter = logging.Formatter('[%(asctime)s]-[%(levelname)s]-[%(funcName)s]-[(%(lineno)d)] %(message)s')
log_file = 'logs/main_en.log'
log_handler = RotatingFileHandler(log_file, mode='a', maxBytes=5 * 1024 * 1024, backupCount=2, encoding=None,
                                  delay=False)
log_handler.setFormatter(log_formatter)
main_log = logging.getLogger("main_en")
main_log.setLevel(logging.DEBUG)
main_log.addHandler(log_handler)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(log_formatter)
main_log.addHandler(console_handler)


EN_translator = inference.many2vi('en')


def callback_func(body, properties):
    """
    function callback người dùng định nghĩa
    :param properties:
    :param body: message từ queue
    :return:
    """
    res_tran = dict()
    print(properties)
    src_lang = body["src_lang"]
    tgt_lang = body["tgt_lang"]
    res_tran["hash_id"] = body["hash_id"]
    try:
        doc = body["text"]
        if src_lang == 'en':
            st_time = time.time()
            main_log.info("{0}: len(message): {1}".format(body["hash_id"], len(body["text"])))
            if src_lang.lower() not in config.LIST_LANGUAGES or tgt_lang.lower() not in config.LIST_TARGETS:
                data_return = {"query": body,
                               "response": {"context": "", "message": "language not support", "code": 0}}
                url_calback = body.get("api_callback", "path callback result")
                if url_calback:
                    res = requests.post(url_calback, json=data_return)
                    print(res.text)
                    if res.status_code != 200:
                        main_log.error("{0}: error call back - error status code: {1}".format(body["hash_id"],
                                                                                              res.status_code))
                main_log.info("{0}: message language not support".format(body["hash_id"]))
                main_log.info("{0}: time analysis and call back: {1}".format(body["hash_id"], time.time() - st_time))
            else:
                res_tran["context"] = EN_translator.infer(doc)
                main_log.info("{0}: time analysis: {1}".format(body["hash_id"], time.time() - st_time))
                res_tran["messege"] = "success"
                res_tran["code"] = 1
                data_return = {"query": body, "response": res_tran}
                url_calback = body.get("api_callback", "path callback result")
                if url_calback:
                    res = requests.post(url_calback, json=data_return, timeout=10)
                    print(res.text)
                    if res.status_code != 200:
                        main_log.error("{0}: error call back - error status code: {1}".format(body["hash_id"],
                                                                                              res.status_code))
                main_log.info("{0}: time analysis and callback: {1}".format(body["hash_id"], time.time() - st_time))

    except Exception as vee:
        print(vee)
        main_log.error("{0}: {1}".format(body["hash_id"], str(vee)))


if __name__ == '__main__':
    cfg = get_config()
    QUEUE_NAME = cfg["ConfigManager"]["QueueConfigs"]["queue_translate_en"]["Queue"]
    QUEUE_HOST = cfg["ConfigManager"]["QueueConfigs"]["queue_translate_en"]["HostName"]
    QUEUE_PASSWORD = cfg["ConfigManager"]["QueueConfigs"]["queue_translate_en"]["Password"]
    QUEUE_USERNAME = cfg["ConfigManager"]["QueueConfigs"]["queue_translate_en"]["UserName"]
    QUEUE_VIRTUAL_HOST = cfg["ConfigManager"]["QueueConfigs"]["queue_translate_en"]["VirtualHost"]
    rab = None
    while True:
        try:
            try:
                rab = ICRabbitMQ(QUEUE_HOST, QUEUE_VIRTUAL_HOST, QUEUE_USERNAME, QUEUE_PASSWORD)
                channel = rab.init_queue(QUEUE_NAME, max_priority=10)
                ICRabbitMQ.run_consummer(channel, QUEUE_NAME, callback_func, is_ack_type=2)
            except Exception as ve:
                print(ve)
                if rab is not None and rab.connection_status():
                    rab.connection_close()
        except Exception as ve:
            print(ve)
