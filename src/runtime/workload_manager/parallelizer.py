# Parallelizes the logical dataflow by creating execution nodes for each logical node in the dataflow graph.
# - Determines the degree of parallelism for each node.
# - Creates execution nodes and assigns them to logical nodes.
# - Connects execution nodes based on the defined edges and transfer types (all-to-all or point-to-point).
# ATTENTION: There is no need for this in use case 0.


class Parallelizer:
    
    def parallelize(DAG):
    
        # TODO Ana, Duncan, Dante
        # THIS CAN BE STATIC 
        
        return DAG
