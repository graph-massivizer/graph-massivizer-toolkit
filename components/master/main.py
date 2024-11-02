# components/master/main.py

from choreographer import Choreographer
from greenifier import Greenifier
from optimizer import Optimizer
from commons.terminal import Terminal

def main():
    terminal = Terminal.get_instance()
    terminal.start()
    try:
        # Initialize components
        choreographer = Choreographer()
        greenifier = Greenifier()
        optimizer = Optimizer()

        # Start components
        choreographer.start()
        greenifier.start()
        optimizer.start()

        # Keep the application running
        choreographer.join()
        greenifier.join()
        optimizer.join()
    except KeyboardInterrupt:
        # Handle graceful shutdown
        choreographer.stop()
        greenifier.stop()
        optimizer.stop()
    finally:
        terminal.stop()

if __name__ == '__main__':
    main()