from typing import Optional
import pygame
import math


def ccw(A, B, C):
    return (C.y-A.y)*(B.x-A.x) > (B.y-A.y)*(C.x-A.x)

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def display(self):
        print(f'Point:\nX: {self.x}\nY: {self.y}')

    def asCoordinate(self):
        return (self.x, self.y)


class Line:
    def __init__(self, start, end):
        self.start = start
        self.startPos = (start.x, start.y)
        self.end = end
        self.endPos = (end.x, end.y)
        self.slope = (end.y-start.y)/(end.x-start.x+0.00000001)

    def display(self):
        print(f'Line:\nStart: {self.startPos}\nEnd: {self.endPos}')

    def isParellel(self, otherLine) -> bool:
        return self.slope == otherLine.slope
    
    def findIntersection(self, otherLine) -> Optional[Point]:

        if self.isParellel(otherLine):
            return None

        x = ( otherLine.start.y - self.start.y + self.slope*self.start.x - otherLine.slope*otherLine.start.x ) / (self.slope - otherLine.slope)
        y = self.start.y + self.slope * (x - self.start.x)

        withinOwnX = (x < self.end.x and self.start.x < x) or (
            x > self.end.x and self.start.x > x)
        withinOtherX = (x < otherLine.end.x and otherLine.start.x < x) or (
            x > otherLine.end.x and otherLine.start.x > x)
        withinOwnY = (y < self.end.y and self.start.y < y) or (
            y > self.end.y and self.start.y > y)
        withinOtherY = (y < otherLine.end.y and otherLine.start.y < y) or (
            y > otherLine.end.y and otherLine.start.y > y)

        if withinOwnX and withinOtherX and withinOwnY and withinOtherY:
            return Point(x,y)

        return None
    
    def isIntersecting(self, otherLine):

        A = self.start
        B = self.end
        C = otherLine.start
        D = otherLine.end

        if A.asCoordinate() == C.asCoordinate() or A.asCoordinate() == D.asCoordinate() or B.asCoordinate() == C.asCoordinate() or B.asCoordinate() == D.asCoordinate():
            return False

        return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)
    
    def drawLine(self, window, color):
        pygame.draw.line(window, color, self.startPos, self.endPos)

    def calculateLength(self):
        return math.sqrt((self.start.x-self.end.x)**2 + (self.start.y-self.end.y)**2)
    
class ConnectedPoint(Point):

    def __init__(self, point: Point):
        self.x = point.x
        self.y = point.y
        self.connections = []
        self.lines = []
    
    def addConnection(self, point: Point):
        self.connections.append(point)

    def removeConnection(self, point: Point):
        self.connections.remove(point)

    def addLine(self, line: Line):
        self.lines.append(line)

    def display(self):
        print(f'ConnectedPoint:\nX: {self.x}\nY: {self.y}')
        for point in self.connections:
            print(f'   Point:\nX: {self.x}\nY: {self.y}')

class Graph:

    def __init__(self):
        self.graph = {}
        self.ids = []

    def getIds(self):
        return self.ids

    def getGraph(self):
        return self.graph

    def generateNewId(self):
        newId = len(self.ids)
        self.ids.append(newId)
        return newId
    
    def addNode(self, point: Point):
        id = self.generateNewId()
        self.graph[id] = (point, [])
        return id
    
    def addConnection(self, id1: int, id2: int):
        self.graph[id1][1].append(id2)
        self.graph[id2][1].append(id1)

    def addNodeWithConnections(self, point:Point, connections):
        id = self.generateNewId()
        self.graph[id] = (point, [])
        for connectionId in connections:
            self.addConnection(id, connectionId)


    def getNodeId(self, point:Point):
        for id,node in self.graph.items():
            if node[0]==point:
                return id
        return -1
    
    def display(self):
        for key, value in self.graph.items():
            print(f'{key}: ({value[0].x}, {value[0].y}) -> {value[1]}')
