from core.bgo_inp_res import BGOInpRes
from .base_component import BaseComponent
import json
class Inceptor(BaseComponent):
    def __init__(self):
        super().__init__("inceptor")

    def process_message(self, sender, message):
        super().process_message(sender, message)
        msg = json.loads(message)
        if (msg['message_type'] == "BGO-inp-req"):
            input_type = msg['payload']['gh']
            implementations = self.get_graphs(input_type)
            request = BGOInpRes(implementations)
            self.emit_message(request.to_message(), "choreographer")

    def get_graphs(self, bgo_type):
        # TODO: add URL
        return [{'input_type':'summary-graph'}, {'input_type':'sampled-graph'}, {'input_type':'whole-graph'}]