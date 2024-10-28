from components.user import User
from components.inceptor import Inceptor
from components.scrutinizer import Scrutinizer
from components.choreographer import Choreographer
from components.optimizer import Optimizer
from components.greenifier import Greenifier
from core.bgo import BGO
from core.message import Message
from core.hardware import Hardware
from core.graph_handle import GraphHandle

import time

def main():
    user = User()
    inceptor = Inceptor()
    scrutinizer = Scrutinizer()
    choreographer = Choreographer()
    optimizer = Optimizer()
    greenifier = Greenifier()

    user.start_listening()
    inceptor.start_listening()
    scrutinizer.start_listening()
    choreographer.start_listening()
    optimizer.start_listening()
    greenifier.start_listening()

    time.sleep(1)  # Allow listeners to initialize

    bgo_request = BGO(GraphHandle("input"), "shortest-path", Hardware(hardware_type="GPU", architecture="NVIDIA A100"), GraphHandle("output"))
    user.emit_message(bgo_request.to_message(), "*")

    time.sleep(2)  # Allow time for messages to be processed

if __name__ == "__main__":
    main()
