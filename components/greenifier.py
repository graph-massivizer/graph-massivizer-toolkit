from core.bgo_green_res import BGOGreenResponse
from .base_component import BaseComponent
import json
class Greenifier(BaseComponent):
    def __init__(self):
        super().__init__("greenifier")
        self.bgo_status = {}


    def process_message(self, sender, message):
        msg = json.loads(message)
        payload = msg["payload"]
        uuid = payload["uuid"]
        if (msg['message_type'] == "BGO-hardware-res"):
            super().process_message(sender, message)
            if uuid not in self.bgo_status.keys():
                self.bgo_status[uuid]={}
            self.bgo_status[uuid]['hardware']=payload['hardware']
        if (msg['message_type'] == "BGO-opt-res"):
            super().process_message(sender, message)
            if uuid not in self.bgo_status.keys():
                self.bgo_status[uuid]={}
            self.bgo_status[uuid]['cost_estimates'] = payload['cost_estimates']

        if (msg['message_type'] in set(["BGO-hardware-res", "BGO-opt-res"])):
            keys = self.bgo_status[uuid].keys()
            if(len(set(keys).intersection(set(['hardware', 'cost_estimates'])))==2):
                hardware = self.bgo_status[uuid]['hardware']
                cost_estimates = self.bgo_status[uuid]['cost_estimates']
                response = BGOGreenResponse(payload['uuid'], self.get_physical_plans(hardware, cost_estimates))
                self.emit_message(response.to_message(), "*")

    def get_physical_plans(self, available_hardware, cost_estimates):
        # TODO: add ids and some content
        return [{'physical_execution_plan':{}}, {'physical_execution_plan':{}}, {'physical_execution_plan':{}}]