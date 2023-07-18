import requests
import json
import os
from yaml import load
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

URL_CFG = ""

AccessToken = ""
Environment = "Production"


def get_config(is_off=False, path_save_cfg: str = "config/cfg.yaml"):
    cfg = None
    try:
        if not is_off:
            payload = json.dumps({
                "AccessToken": AccessToken,
                "Environment": Environment
            })
            headers = {
                'accept': 'text/plain',
                'Content-Type': 'application/json-patch+json'
            }

            response = requests.request("POST", URL_CFG, headers=headers, data=payload)
            if response.status_code == 200:
                with open(path_save_cfg, "w+") as f:
                    f.write(response.text)
    except Exception as ve:
        print(ve)
    if os.path.exists(path_save_cfg):
        with open(path_save_cfg) as f:
            cfg = load(f, Loader)
    return cfg


def parse_connection_string(str_cnn):
    res = dict()
    split_dt = str_cnn.split(";")
    for c_sp in split_dt:
        k, v = c_sp.split("=")
        res[k.strip()] = v.replace("'", "").replace('"', '')
    return res


if __name__ == '__main__':
    cf = get_config()
    print(cf)
    print(parse_connection_string(cf["ConfigManager"]["ConnectionStrings"]["facebook_info"]["Value"]))
