from typing import Optional
import pygame_widgets
from pygame_widgets.slider import Slider
from pygame_widgets.textbox import TextBox
from pygame_widgets.button import Button
import pygame
import math
import random


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
    
    def getRandomNodes(self, amount):
        outputIds = []
        if amount>len(self.ids):
            return outputIds
        while len(outputIds) < amount:
            id = self.ids[random.randrange(0,len(self.ids))]
            if not id in outputIds:
                outputIds.append(id)
        return outputIds
    
    def getRandomConnection(self, id, exludeIds):
        if id in self.ids:
            connections = list(set(self.graph[id][1]) - set(exludeIds))
            if len(connections) == 0:
                return -1
            
            return connections[random.randrange(0,len(connections))]
        return -1
    
    def display(self):
        for key, value in self.graph.items():
            print(f'{key}: ({value[0].x}, {value[0].y}) -> {value[1]}')

    def clear(self):
        self.graph = {}
        self.ids = []

class Text:

    def __init__(self, text, color, font, x, y, slider=None):

        self.font = font
        self.color = color

        self.text = text
        self.rect = self.font.render(self.text, True, self.color).get_rect()
        self.rect.center = (x, y)
        
        self.slider = slider

    def render(self, window):
        currentText = self.font.render(self.text, True, self.color)
        if self.slider is not None:
            currentText = self.font.render(f'{self.text}{self.slider.getValue()}', True, self.color)
        window.blit(currentText, self.rect)

class WindowInfo:

    def __init__(self, map_width, slider_width, win_height, font, default_density, default_continent_sides, 
                 default_min_distance, default_min_connections, default_num_continents, density_coefficient) -> None:
        
        self.map_width = map_width
        self.slider_width = slider_width
        self.win_width = self.map_width+self.slider_width
        self.win_height = win_height

        self.font = font

        self.density = default_density
        self.continent_sides = default_continent_sides
        self.min_distance = default_min_distance
        self.min_connections = default_min_connections
        self.num_continents = default_num_continents

        self.density_coefficient = density_coefficient

        self.shapes = ['dot', 'square', 'triangle', 'blur', 'water']


        # create palettes
        self.palette = 'default'
        self.palettes = {}

        defaultPalette = ('default', 
                          [pygame.Color('#F0D197'), pygame.Color('#b6ad90'),
                          pygame.Color('#a68a64'), pygame.Color('#656d4a'), 
                          pygame.Color('#333d29'), pygame.Color('#676f54'), 
                          pygame.Color('#7d7d70'), pygame.Color('#858A89'),
                          pygame.Color('#faf3dd'), pygame.Color('#fcfffc'), 
                          pygame.Color('#ffffff')], (0, 50, 100), True)
        
        originalPalette = ('original', 
                           [pygame.Color('#c2c5aa'), pygame.Color('#b6ad90'),
                           pygame.Color('#a68a64'), pygame.Color('#656d4a'), 
                            pygame.Color('#333d29'), pygame.Color('#676f54')], (0, 50, 100), False)
        
        palettesList = [defaultPalette, originalPalette]

        for palette in palettesList:

            if palette[3]:

                polarColorPalette = palette[1].copy()
                polarColorPalette.reverse()
                polarColorPalette.extend(palette[1])

                self.palettes[palette[0]] = {'list': polarColorPalette, 'water': palette[2], 'isPolar': palette[3]}

            else:

                self.palettes[palette[0]] = {
                    'list': palette[1], 'water': palette[2], 'isPolar': palette[3]}

        print(self.getPallete())

        self.textSpacing = 20
        self.textBoxes = []

        self.sliders = {}

        self.buttons = {}

    def createSliders(self, window):

        densitySlider = Slider(
            window, self.map_width+20, 40, self.slider_width-40, 10, min=self.density[0], max=self.density[2], step=1, initial=self.density[1])

        sidesSlider = Slider(window, self.map_width+20, 80, self.slider_width -
                             40, 10, min=self.continent_sides[0], max=self.continent_sides[2], step=1, initial=self.continent_sides[1])

        distanceSlider = Slider(window, self.map_width+20, 120,
                                self.slider_width-40, 10, min=self.min_distance[0], max=self.min_distance[2], step=1, initial=self.min_distance[1])

        connectionsSlider = Slider(window, self.map_width+20, 160, self.slider_width -
                                   40, 10, min=self.min_connections[0], max=self.min_connections[2], step=1, initial=self.min_connections[1])
        
        continentsSlider = Slider(window, self.map_width+20, 280,
                                  self.slider_width-40, 10, min=self.num_continents[0], max=self.num_continents[2], step=1, initial=self.num_continents[1])

        shapeSlider = Slider(window, self.map_width+20, 320,
                             self.slider_width-40, 10, min=0, max=len(self.shapes)-1, step=1)

        colorSlider = Slider(window, self.map_width+20, 360,
                            self.slider_width-40, 10, min=0, max=len(self.palettes.keys())-1, step=1)
        
        self.sliders['density'] = densitySlider
        self.sliders['sides'] = sidesSlider
        self.sliders['distance'] = distanceSlider
        self.sliders['connections'] = connectionsSlider
        self.sliders['continents'] = continentsSlider
        self.sliders['shape'] = shapeSlider
        self.sliders['color'] = colorSlider
        
        return densitySlider, sidesSlider, distanceSlider, connectionsSlider, continentsSlider, shapeSlider, colorSlider
        
        
    def createButtons(self, window, generateNodes, generateContinents, refine, autoGenerate):

        nodeButton = Button(window, self.map_width+20, 200, self.slider_width -
                            40, 30, onClick=generateNodes)
        
        mapButton = Button(window, self.map_width+20, 400, self.slider_width -
                           40, 30, onClick=generateContinents)

        refineButton = Button(window, self.map_width+20, 440, self.slider_width -
                              40, 30, onClick=refine)

        autoButton = Button(window, self.map_width+20, 480, self.slider_width -
                            40, 30, onClick=autoGenerate)
        
        self.buttons['node'] = nodeButton
        self.buttons['map'] = mapButton
        self.buttons['refine'] = refineButton
        self.buttons['auto'] = autoButton
        
        return nodeButton, mapButton, refineButton, autoButton
    
    def createTextBoxes(self):

        black = (0,0,0)

        nodeText = Text('Node Generation', black, self.font,
                        self.win_width - self.slider_width//2, 20)

        mapText = Text('Continent Generation', black, self.font,
                        self.win_width - self.slider_width//2, 260)

        if len(self.sliders) == 0:
            raise Exception('must create sliders before text boxes')
        
        densityText = Text('Density: ', black, self.font,
                       self.win_width - self.slider_width//2, self.sliders['density'].getY()+self.textSpacing, slider=self.sliders['density'])
        
        sidesText = Text('Continent Sides: ', black, self.font,
                         self.win_width - self.slider_width//2, self.sliders['sides'].getY()+self.textSpacing, slider=self.sliders['sides'])
        
        distanceText = Text('Minimum Distance: ', black, self.font,
                            self.win_width - self.slider_width//2, self.sliders['distance'].getY()+self.textSpacing, slider=self.sliders['distance'])
        
        connectionsText = Text('Connections: ', black, self.font,
                               self.win_width - self.slider_width//2, self.sliders['connections'].getY()+self.textSpacing, slider=self.sliders['connections'])
        
        continentsText = Text('Continents: ', black, self.font,
                              self.win_width - self.slider_width//2, self.sliders['continents'].getY()+self.textSpacing, slider=self.sliders['continents'])
        
        shapeText = Text('Refinement: ', black, self.font,
                         self.win_width - self.slider_width//2, self.sliders['shape'].getY()+self.textSpacing, slider=self.sliders['shape'])
        
        colorText = Text('Color: ', black, self.font,
                         self.win_width - self.slider_width//2, self.sliders['color'].getY()+self.textSpacing, slider=self.sliders['color'])
        
        if len(self.buttons) == 0:
            raise Exception('must create buttons before text boxes')
        
        nodeButtonText = Text('Generate Nodes', black, self.font,
                         self.win_width - self.slider_width//2, self.buttons['node'].getY()+self.buttons['node'].getHeight()//2)
        
        mapButtonText = Text('Generate Continents', black, self.font,
                             self.win_width - self.slider_width//2, self.buttons['map'].getY()+self.buttons['map'].getHeight()//2)
        
        refineButtonText = Text('Refine', black, self.font,
                                self.win_width - self.slider_width//2, self.buttons['refine'].getY()+self.buttons['refine'].getHeight()//2)
        
        autoButtonText = Text('Auto Generate', black, self.font,
                              self.win_width - self.slider_width//2, self.buttons['auto'].getY()+self.buttons['auto'].getHeight()//2)
        
        self.textBoxes = [nodeText, mapText, nodeButtonText, mapButtonText, refineButtonText, autoButtonText, densityText, sidesText, distanceText, connectionsText, continentsText, shapeText, colorText]

        return self.textBoxes
    
    def getMinimumContinentSides(self):
        return self.sliders['sides'].getValue()
    
    def getMinimumConnections(self):
        return self.sliders['connections'].getValue()
    
    def getMinimumLength(self):
        return self.sliders['distance'].getValue()
    
    def getNumPoints(self):
        return int(self.sliders['density'].getValue()
                   * self.density_coefficient/self.map_width/self.win_height)
    
    def getPallete(self):
        return self.palettes[self.palette]['list']
    
    def getWater(self):
        return self.palettes[self.palette]['water']

class WorldInfo:

    def __init__(self):

        self.continents = []
        self.continentColors = []

        self.path = []
        self.pathPoints = []

        self.graph = Graph()

    def clearContinents(self):
        self.continents = []
        self.continentColors = []

    def clearPath(self):
        self.path = []
        self.pathPoints = []

def export_window_as_png(window, filename):
    """
    Export Pygame window as a PNG file.

    Args:
    - window: Pygame window object to be exported.
    - filename: Name of the PNG file to be saved.

    Returns:
    - None
    """
    # Get the surface of the window
    surface = pygame.display.get_surface()

    # Create a new surface with the same dimensions as the window
    image = pygame.Surface(surface.get_size())

    # Draw the contents of the window onto the new surface
    image.blit(surface, (0, 0))

    # Save the new surface as a PNG file
    pygame.image.save(image, filename)
