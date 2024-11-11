from core.bgo_impl_res import BGOImplRes
from core.hardware import Hardware
from .base_component import BaseComponent
import json

class Scrutinizer(BaseComponent):
    def __init__(self):
        super().__init__("scrutinizer")

    def process_message(self, sender, message):
        print("Scrutinizer received"+message)
        msg = json.loads(message)
        payload = msg["payload"]
        if(msg['message_type'] == "BGO"):
            super().process_message(sender, message)
            bgo_type = payload['gf']
            implementations = self.get_implementations(bgo_type)
            request = BGOImplRes(payload['uuid'], bgo_type, implementations)
            self.emit_message(request.to_message(), "*")

    def get_implementations(self, bgo_type):
        return [{'bgo_type':'shortest_path', 'implementation': 'dijkstra', 'hardware': Hardware(hardware_type="GPU", architecture="NVIDIA A100").to_dict()}]