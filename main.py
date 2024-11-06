# main.py

from simulation.lifecycle_manager import LifecycleManager
from commons.terminal import Terminal

def main():
    terminal = Terminal.get_instance()
    terminal.start()
    try:
        lifecycle_manager = LifecycleManager()
        lifecycle_manager.initialize_cluster()
        lifecycle_manager.deploy_components()
        lifecycle_manager.receive_job()
        lifecycle_manager.optimize_job()
        lifecycle_manager.optimize_energy()
        lifecycle_manager.provision_resources()
        lifecycle_manager.initialize_runtime()
        lifecycle_manager.execute_job()
        lifecycle_manager.terminate()
        lifecycle_manager.reset()
    finally:
        terminal.stop()

if __name__ == '__main__':
    main()