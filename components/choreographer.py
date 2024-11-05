import json

from core.bgo_cost_req import BGOCostReq
from core.bgo_impl_req import BGOImplReq
from core.bgo_inp_req import BGOInpReq
from .base_component import BaseComponent

class Choreographer(BaseComponent):
    def __init__(self):
        super().__init__("choreographer")

    def process_message(self, sender, message):
        super().process_message(sender, message)
        msg = json.loads(message)
        if(msg['message_type'] == "BGO"):
            request = BGOImplReq(msg['payload']['gf'])
            self.emit_message(request.to_message(), "scrutinizer")

            request = BGOInpReq(msg['payload']['input'])
            self.emit_message(request.to_message(), "inceptor")

        
            # request = BGOCostReq(msg['payload']['input'])
            # self.emit_message(request.to_message(), "inceptor")

