from core.bgo_inp_res import BGOInpRes
from .base_component import BaseComponent
import json
class Inceptor(BaseComponent):
    def __init__(self):
        super().__init__("inceptor")

    def process_message(self, sender, message):
        print("Inceptor"+message)
        msg = json.loads(message)
        payload = msg["payload"]
        if(msg['message_type'] == "BGO"):
            super().process_message(sender, message)
            graph_id = payload['input']
            implementations = self.get_graphs(graph_id)
            request = BGOInpRes(payload['uuid'], implementations)
            self.emit_message(request.to_message(), "*")

    def get_graphs(self, graph_id):
        # TODO: add URL
        return [{'input_type':'summary-graph'}, {'input_type':'sampled-graph'}, {'input_type':'whole-graph'}]