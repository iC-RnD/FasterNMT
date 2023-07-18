from .api import hash_session
import time


class SessionS2T(object):

    def __init__(self):
        self.session = dict()

    def insert_session(self, data_input: dict):
        hash_id = hash_session(data_input)
        if hash_id not in self.session:
            self.session[hash_id] = {"status": -1, "created_time": time.time(), "update_time": time.time(),
                                     "result": {}, "data": data_input}
        return hash_id

    def get_info_session(self, hash_id: str):
        if hash_id in self.session:
            return self.session[hash_id]
        return {"status": -2, "result": {}, "meta": {}}

    def update_session(self, hash_id: str, result: dict, status: int):
        if hash_id in self.session:
            self.session[hash_id]["status"] = status
            self.session[hash_id]["result"] = result
            self.session[hash_id]["update_time"] = time.time()
            return True
        return False

    def delete_session(self, hash_id: str):
        if hash_id in self.session:
            del self.session[hash_id]
            return True
        return False
