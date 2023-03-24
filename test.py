from mapclasses import Point, Line, Graph

graph = Graph()

id1 = graph.addNode(Point(1,1))
id2 = graph.addNode(Point(3,4))
graph.addConnection(id1, id2)
id3 = graph.addNodeWithConnections(Point(2,2), [id1,id2])
id4 = graph.addNodeWithConnections(Point(1, 2), [id1, id3])

graph.display()

