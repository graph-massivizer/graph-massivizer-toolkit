# components/runtime/main.py

from inceptor import Inceptor
from scrutinizer import Scrutinizer
from commons.terminal import Terminal

def main():
    terminal = Terminal.get_instance()
    terminal.start()
    try:
        # Initialize components
        inceptor = Inceptor()
        scrutinizer = Scrutinizer()

        # Start components
        inceptor.start()
        scrutinizer.start()

        # Keep the application running
        inceptor.join()
        scrutinizer.join()
    except KeyboardInterrupt:
        inceptor.stop()
        scrutinizer.stop()
    finally:
        terminal.stop()

if __name__ == '__main__':
    main()