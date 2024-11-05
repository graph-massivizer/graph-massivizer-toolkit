from core.bgo_impl_res import BGOImplRes
from core.hardware import Hardware
from .base_component import BaseComponent
import json

class Scrutinizer(BaseComponent):
    def __init__(self):
        super().__init__("scrutinizer")

    def process_message(self, sender, message):
        super().process_message(sender, message)
        msg = json.loads(message)
        if (msg['message_type'] == "BGO-impl-req"):
            bgo_type = msg['payload']['gf']
            implementations = self.get_implementations(bgo_type)
            request = BGOImplRes(bgo_type, implementations)
            self.emit_message(request.to_message(), "choreographer")

    def get_implementations(self, bgo_type):
        return [{'bgo_type':'shortest_path', 'implementation': 'dijkstra', 'hardware': Hardware(hardware_type="GPU", architecture="NVIDIA A100").to_dict()}]