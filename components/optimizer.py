from core.bgo_opt_res import BGOOptRes
from .base_component import BaseComponent
import json

class Optimizer(BaseComponent):
    def __init__(self):
        super().__init__("optimizer")
        self.bgo_status = {}

    def process_message(self, sender, message):
        msg = json.loads(message)
        payload = msg["payload"]
        uuid = payload["uuid"]
        if(msg['message_type'] == "BGO-inp-res"):
            super().process_message(sender, message)
            if uuid not in self.bgo_status.keys():
                self.bgo_status[uuid]={}
            self.bgo_status[uuid]['gh'] = payload['gh']
        if (msg['message_type'] == "BGO-impl-res"):
            super().process_message(sender, message)
            if uuid not in self.bgo_status.keys():
                self.bgo_status[uuid]={}
            self.bgo_status[uuid]['gf'] = payload['gf']

        if (msg['message_type'] in set(["BGO-inp-res", "BGO-impl-res"])):
            keys = self.bgo_status[uuid].keys()
            if(len(set(keys).intersection(set(['gh', 'gf'])))==2):
                response = BGOOptRes(payload['uuid'], self.get_cost_estimates())
                self.emit_message(response.to_message(), "*")


    def get_cost_estimates(self):
        # TODO load some static info regarding the hardware
        # TODO: do something with the graph handle and BGO implementations
        # TODO: add higher level of detail
        return [{'cost_estimate': 5}, {'cost_estimate': 6}, {'cost_estimate': 7}]