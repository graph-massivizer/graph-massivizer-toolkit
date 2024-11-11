import json
from core.bgo_hardware_res import BGOHardwareResponse
from core.hardware import Hardware
from .base_component import BaseComponent

class Choreographer(BaseComponent):
    def __init__(self):
        super().__init__("choreographer")

    def process_message(self, sender, message):
        msg = json.loads(message)
        payload = msg["payload"]
        if(msg['message_type'] == "BGO"):
            super().process_message(sender, message)
            response = BGOHardwareResponse(payload["uuid"], [x.to_dict() for x in self.get_available_hardware()])
            self.emit_message(response.to_message(), "*")
        if (msg['message_type'] == "BGO-green-res"):
            super().process_message(sender, message)
            self.choose_and_schedule(payload["physical_execution_plans"])


    def get_available_hardware(self):
        return [Hardware(hardware_type="GPU", architecture="NVIDIA A100"), Hardware(hardware_type="CPU", architecture="Intel Core i9-14900K"), Hardware(hardware_type="CPU", architecture="AMD Zen 4 Ryzen 7000")]

    def choose_and_schedule(self, physical_execution_plans):
        print("Choreographer is scheduling execution")