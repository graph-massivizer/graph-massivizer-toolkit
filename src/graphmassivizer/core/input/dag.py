class DAG:

 def __init__(self,init={"directed": False, "multigraph": False, "graph":None, "nodes":{}, "edges":{}}):
  self.dag = init

 def add(self,key,value=None):
  if key != None and key not in self.dag:
   self.dag[key] = value

 def update(self,key,value):
  if key != None and key in self.dag:
   self.dag[key] = value

 def updateFn(self,key,fun):
  if key != None and key in self.dag:
   self.dag[key] = fun(self.dag[key])

 def remove(self,key):
  self.dag.pop(key,None)
