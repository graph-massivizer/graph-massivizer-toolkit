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

def choreographer_coordinator():
    # user-BGO->choreographer
    # choreographer-(what implementations do we have for that particular function?)->scrutinizer/BGO repository
    # choreographer -I(what versions do we have to load?)->Inceptor
    # choreographer -O(what is the cost of execution and target hardware for the available graphs and function implementations? Use types to determine compatibility between the function and the whole/sampled/summarized graph)->
    # (assumptions regarding the possible inputs and the range of output we get from Optimizer: we expect the optimizer to answer with a list of possible scrutinizer implementations and associated inceptor particular handles
    # choreographer-(what is the hardware holistically that should be considered)->Greenifier
    # choreographer executes the physical execution graph
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
    user.emit_message(bgo_request.to_message(), "choreographer")


    # choreographer.emit_message(Message("x", "what implementations do we have for shortest-path"), "scrutinizer")
    #
    #
    # choreographer.emit_message(Message("x", "what graph versions do we have to load?"), "inceptor")
    # choreographer.emit_message(Message("x", "what is the cost of execution and target hardware for the available graphs and function implementations?"), "optimizer")
    # choreographer.emit_message(Message("x",
    #                                    "what is the hardware holistically that should be considered?"), "greenifier")

    time.sleep(2)  # Allow time for messages to be processed


def main():
    choreographer_coordinator()

if __name__ == "__main__":
    main()
