import numpy as np
from mapclasses import Graph

Point = tuple[int, int]

graph = Graph(4)
graph.addNode((4,5))
graph.addNode((3,5))
graph.addConnection(0,1)
print(graph.matrix)
print(graph.nodes)
print(type(graph.getNode(1)))
print(graph.getConnections(1))

array = np.arange(1,5)
print(array)
print(array[3:3])

print(range(3,3))
