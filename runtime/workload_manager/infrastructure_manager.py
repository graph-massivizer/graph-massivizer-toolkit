# - Manages the infrastructure, including Task Manager discovery and resource allocation.
# - Uses ZooKeeper to track available Task Managers and their resources.
# - Implements the getMachine method, which selects a suitable Task Manager for execution nodes based on resource availability and location preferences.
# - Reclaims execution units when tasks are finished or datasets are erased.