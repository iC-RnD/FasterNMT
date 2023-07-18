import hashlib
import json


def hash_session(query: dict):
    return hashlib.sha224(json.dumps(query).encode("utf-8")).hexdigest()
