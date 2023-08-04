from typing import Optional, Tuple, List
import pygame_widgets
from pygame_widgets.slider import Slider
from pygame_widgets.textbox import TextBox
from pygame_widgets.button import Button
import pygame
import math
import random
import time
import numpy as np


def ccw(A, B, C):
    return (C[1]-A[1])*(B[0]-A[0]) > (B[1]-A[1])*(C[0]-A[0])

Point = tuple[int, int]

class Line:
    def __init__(self, start:Point, end:Point):
        self.start = start
        self.end = end

    def display(self):
        print(f'Line:\nStart: {self.start}\nEnd: {self.end}')
    
    def isIntersecting(self, otherLine):

        A = self.start
        B = self.end
        C = otherLine.start
        D = otherLine.end

        if A == C or A == D or B == C or B == D:
            return False

        return ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D)
    
    def drawLine(self, window, color):
        pygame.draw.line(window, color, self.start, self.end)

    def calculateLength(self):
        return math.sqrt((self.start[0]-self.end[0])**2 + (self.start[1]-self.end[1])**2)

class Graph:

    def __init__(self, size=200):

        self.size = size
        self.matrix = np.zeros((size, size), dtype=bool)
        self.nodes = np.zeros(size, dtype=object)
        self.nextIndex = 0
        self.emptyIds = []
        self.partitions = {"width":-1, "height":-1, "numX":0, "numY":0, "array":None}

    def getMatrix(self):
        return self.matrix

    def getAllNodes(self):
        return self.nodes
    
    def getNode(self, id:int):
        return self.nodes[id]
    
    def getNodes(self, ids:List[int]):
        return self.nodes[ids]

    def addNode(self, point:Point):

        if len(self.emptyIds) >0 :
            self.nodes[self.emptyIds.pop()] = point
        else:
            self.nodes[self.nextIndex] = point
            self.nextIndex += 1
    
    def addNodes(self, positions: List[Point]):

        while len(self.emptyIds) > 0 and len(positions) > 0:
            self.nodes[self.emptyIds.pop()] = positions.pop()

        if self.nextIndex+len(positions) > self.size:
            raise IndexError("Attempting to add too many nodes")
        self.nodes[self.nextIndex:self.nextIndex + len(positions)] = positions

    def removeNode(self, id:int):

        self.nodes[id] = 0
        self.matrix[id, :] = np.zeros(self.size)
        self.matrix[:, id] = np.zeros(self.size)
        self.emptyIds.append(id)

    def addConnection(self, id1:int, id2:int):
        self.matrix[id1, id2] = self.matrix[id2, id1] = 1

    def addConnections(self, ids: List[Tuple[int, int]]):

        for id1, id2 in ids:
            self.matrix[id1, id2] = self.matrix[id2, id1] = 1

    def removeConnection(self, id1: int, id2: int):
        self.matrix[id1, id2] = self.matrix[id2, id1] = 0

    def getRandomIds(self, amount:int):
        
        if self.size < amount:
            return range(self.size)
        
        return random.sample(range(self.size), amount)
        
    def getConnections(self, id:int):

        raw = self.matrix[id,:]

        return [value*id for id, value in enumerate(raw) if value != 0]
    
    def getRandomConnection(self, id:int, exclude:List[int]=[]):

        connections = [x for x in self.getConnections(id) if x not in exclude]

        if len(connections) == 0:
            return -1

        return random.sample(connections, 1)[0]
    
    def getCloseRandomConnection(self, id: int,  homeId: int, exclude: List[int] = [], numSections: int = 1):

        connections = [x for x in self.getConnections(id) if x not in exclude and x in self.getCloseIds(homeId, numSections)]

        if len(connections) == 0:
            return -1

        return random.sample(connections, 1)[0]
    
    def fillMatrixRandom(self, xMin, yMin, xMax, yMax):

        while len(self.emptyIds) > 0:
            self.nodes[self.emptyIds.pop()] = (
                random.randint(xMin, xMax), random.randint(yMin, yMax))
        while self.nextIndex < self.size:
            self.nodes[self.nextIndex] = (
                random.randint(xMin, xMax), random.randint(yMin, yMax))
            self.nextIndex += 1

    def partition(self, xMin: int, xMax: int, width:int, yMin:int, yMax: int, height: int):

        numXSections = (xMax-xMin)//width
        numYSections = (yMax-yMin)//height

        self.partitions['numX'] = numXSections
        self.partitions['numY'] = numYSections

        sectionWidth = math.ceil((xMax-xMin)/numXSections)
        sectionHeight = math.ceil((yMax-yMin)/numYSections)

        self.partitions['width'] = sectionWidth
        self.partitions['height'] = sectionHeight

        self.partitions['array'] = [[[]]*numXSections]*numYSections

        for id, node in enumerate(self.nodes):
            self.partitions['array'][node[1]//sectionHeight][node[0]//sectionWidth].append(id)

    def getCloseIds(self, id:int, numSections:int=1):
        startTime = time.time()

        xSection = self.nodes[id][0] // self.partitions['width']
        ySection = self.nodes[id][1] // self.partitions['height']

        xBounds = range(max(0, xSection-numSections), min(int(self.partitions['numX']), xSection+numSections))
        yBounds = range(max(0, ySection-numSections), min(int(self.partitions['numY']), ySection+numSections))

        output = []
        for x in xBounds:
            for y in yBounds:
                output.extend(self.partitions['array'][y][x])

        # print(f'time to get close ids: {time.time() - startTime}')
        return output

    def getClosestDistance(self, id: int):
        '''assumes sections are squares'''

        currentX = self.nodes[id][0]
        currentY = self.nodes[id][1]

        xSection = currentX // self.partitions['width']
        ySection = currentY // self.partitions['height']

        centerX = (xSection+0.5)*self.partitions['width']
        centerY = (ySection+0.5)*self.partitions['height']

        minDistance = self.partitions['numX']*self.partitions['width']

        minDistanceId = -1

        extraIterationsLeft = 1

        for numSections in range(0, max(int(self.partitions['numX']), self.partitions['numY'])):

            xBounds = range(max(0, xSection-numSections),
                            min(int(self.partitions['numX']), xSection+numSections))
            yBounds = range(max(0, ySection-numSections),
                            min(int(self.partitions['numY']), ySection+numSections))

            
            for x in xBounds:
                for y in yBounds:
                    checkingIds = self.partitions['array'][y][x]
                    for id in checkingIds:
                        checkingX = self.nodes[id][0]
                        checkingY = self.nodes[id][1]
                        length = Line((currentX, currentY), (checkingX, checkingY)).calculateLength()
                        if length<minDistance:
                            minDistance = length
                            minDistanceId = id

            if minDistance > (numSections+1)*(self.partitions['width']**2+self.partitions['height']**2)**0.5:
                extraIterationsLeft = 2
                break

            if minDistanceId != -1:
                extraIterationsLeft -= 1

            if extraIterationsLeft == 0:
                break
        
        return minDistanceId

    def display(self):
        print(self.matrix)

    def reset(self, size=-1):
        if size != -1:
            self.size = size

        self.matrix = np.zeros((self.size, self.size), dtype=bool)
        self.nodes = np.zeros(self.size, dtype=object)
        self.nextIndex = 0
        self.emptyIds = []
        self.partitions = {"width":-1, "height":-1, "numX":0, "numY":0, "array":None}


class LinePartition:

    def __init__(self, xMin: int, xMax: int, width: int, yMin: int, yMax: int, height: int):

        numXSections = (xMax-xMin)//width
        numYSections = (yMax-yMin)//height

        self.partitions = {}

        self.partitions['numX'] = numXSections
        self.partitions['numY'] = numYSections

        sectionWidth = math.ceil((xMax-xMin)/numXSections)
        sectionHeight = math.ceil((yMax-yMin)/numYSections)

        self.partitions['width'] = sectionWidth
        self.partitions['height'] = sectionHeight

        
        matrix = []
        for _ in range(numYSections):
            row = []
            for __ in range(numXSections):
                row.append([])
            matrix.append(row)

        self.partitions['array'] = matrix

        # print(f'rows: {len(matrix)}')
        # print(f'cols: {len(matrix[0])}')

        self.totalLines = 0
        self.allLines = []

    def getAllLines(self):
        return self.allLines

    def addLine(self, line: Line):

        startXSection = line.start[0]//self.partitions['width']
        startYSection = line.start[1] // self.partitions['height']

        endXSection = line.end[0]//self.partitions['width']
        endYSection = line.end[1] // self.partitions['height']

        if startXSection != endXSection or startYSection != endYSection:

            self.partitions['array'][startYSection][startXSection].append(line)
            self.partitions['array'][endYSection][endXSection].append(line)

            # print(
            #     f'adding line to ({startXSection}, {startYSection}) and ({endXSection}, {endYSection})')
        else:
            self.partitions['array'][startYSection][startXSection].append(line)
            # print(
            #     f'adding line to ({startXSection}, {startYSection})')
            
        self.allLines.append(line)
        self.totalLines += 1
        
        

    def getCloseLines(self, node: Point, numSections: int = 1):

        xSection = node[0] // self.partitions['width']
        ySection = node[1] // self.partitions['height']

        xBounds = range(max(0, xSection-numSections),
                        min(int(self.partitions['numX']), xSection+numSections+1))
        yBounds = range(max(0, ySection-numSections),
                        min(int(self.partitions['numY']), ySection+numSections+1))

        # print(len(xBounds)*len(yBounds))

        output = []
        for x in xBounds:
            for y in yBounds:
                output.extend(self.partitions['array'][y][x])

        # print(f'output length: {len(output)}')
        # print(f'set output length: {len(set(output))}')

        # always returning every line in the LinePartition rather than just a subset that would increase efficiency
        return list(set(output))

    def reset(self):
        self.partitions['array'] = [[[]]*self.partitions['numX']]*self.partitions['numY']

    def partitionSizes(self):
        return [[len(set(x)) for x in y] for y in self.partitions['array']]


class PointPartition:

    def __init__(self, xMin: int, xMax: int, width: int, yMin: int, yMax: int, height: int):

        numXSections = (xMax-xMin)//width
        numYSections = (yMax-yMin)//height

        self.partitions = {}

        self.partitions['numX'] = numXSections
        self.partitions['numY'] = numYSections

        sectionWidth = math.ceil((xMax-xMin)/numXSections)
        sectionHeight = math.ceil((yMax-yMin)/numYSections)

        self.partitions['width'] = sectionWidth
        self.partitions['height'] = sectionHeight

        matrix = []
        for _ in range(numYSections):
            row = []
            for __ in range(numXSections):
                row.append([])
            matrix.append(row)

        self.partitions['array'] = matrix

        # print(f'rows: {len(matrix)}')
        # print(f'cols: {len(matrix[0])}')

        self.totalPoints = 0
        self.allPoints = []

    def getAllPoints(self):
        return self.allPoints

    def addPoint(self, point: Point):

        xSection = point[0]//self.partitions['width']
        ySection = point[1] // self.partitions['height']
        
        self.partitions['array'][ySection][xSection].append(point)

        self.allPoints.append(point)
        self.totalPoints += 1

    def getClosePoints(self, node: Point, numSections: int = 1):

        xSection = node[0] // self.partitions['width']
        ySection = node[1] // self.partitions['height']

        xBounds = range(max(0, xSection-numSections),
                        min(int(self.partitions['numX']), xSection+numSections+1))
        yBounds = range(max(0, ySection-numSections),
                        min(int(self.partitions['numY']), ySection+numSections+1))

        output = []
        for x in xBounds:
            for y in yBounds:
                output.extend(self.partitions['array'][y][x])

        return output

    def reset(self):
        self.partitions['array'] = [
            [[]]*self.partitions['numX']]*self.partitions['numY']

    def partitionSizes(self):
        return [[len(x) for x in y] for y in self.partitions['array']]

class Text:

    def __init__(self, text, color, font, x, y, slider=None, values=[]):

        self.font = font
        self.color = color

        self.text = text
        self.rect = self.font.render(self.text, True, self.color).get_rect()
        self.rect.center = (x, y)
        
        self.slider = slider
        self.values = values

    def render(self, window):
        currentText = self.font.render(self.text, True, self.color)
        if self.slider is not None:
            if self.values != []:
                currentText = self.font.render(
                    f'{self.text}{self.values[self.slider.getValue()]}', True, self.color)
            else:
                currentText = self.font.render(f'{self.text}{self.slider.getValue()}', True, self.color)
        window.blit(currentText, self.rect)

class WindowInfo:

    def __init__(self, map_width:int, slider_width:int, win_height:int, font, titleFont, default_density, default_continent_sides, 
                 default_min_distance, default_min_connections, default_num_continents, density_coefficient, default_water_levels, default_water_width) -> None:
        
        self.map_width = map_width
        self.slider_width = slider_width
        self.win_width = self.map_width+self.slider_width
        self.win_height = win_height

        self.font = font
        self.titleFont = titleFont
        self.buttonColor = (150,150,150)
        self.buttonRadius = 15


        self.density = default_density
        self.continent_sides = default_continent_sides
        self.min_distance = default_min_distance
        self.min_connections = default_min_connections
        self.num_continents = default_num_continents

        self.water_levels = default_water_levels
        self.water_width = default_water_width

        self.density_coefficient = density_coefficient

        self.shapes = ['dot [d]', 'square [s]', 'triangle [p]', 'blur [g]', 'water [o]']


        # create palettes
        self.palette = 'default'
        self.palettes = {}

        defaultPalette = ('default', 
                          [pygame.Color('#F0D197'), pygame.Color('#b6ad90'),
                          pygame.Color('#a68a64'), pygame.Color('#656d4a'), 
                          pygame.Color('#333d29'), pygame.Color('#676f54'), 
                          pygame.Color('#7d7d70'), pygame.Color('#858A89'),
                          pygame.Color('#faf3dd'), pygame.Color('#fcfffc')], (0, 50, 100), 10, False)
        
        originalPalette = ('original', 
                           [pygame.Color('#c2c5aa'), pygame.Color('#b6ad90'),
                           pygame.Color('#a68a64'), pygame.Color('#656d4a'), 
                            pygame.Color('#333d29'), pygame.Color('#676f54')], (0, 50, 100), 10, False)
        
        parchmentPalette = ('parchment', 
                            [pygame.Color('#ffc599'), pygame.Color('#d49961'),
                             pygame.Color('#eda268'), pygame.Color('#cb8849'),
                             pygame.Color('#eea561'), pygame.Color('#eda268')], (255, 209, 173), 10, False)

        redPalette = ('red',
                           [pygame.Color('#ff0022'), pygame.Color('#ff4422'),
                            pygame.Color('#c32f27'), pygame.Color('#d8572a'),
                            pygame.Color('#8f250c'), pygame.Color('#691e06'),
                            pygame.Color('#a63c06'), pygame.Color('#ec7505')], (45, 10, 10), 10, False)
        
        palettesList = [defaultPalette, originalPalette, parchmentPalette, redPalette]

        for palette in palettesList:

            if palette[4]:

                polarColorPalette = palette[1].copy()
                polarColorPalette.reverse()
                polarColorPalette.extend(palette[1])

                self.palettes[palette[0]] = {'list': polarColorPalette, 'water': palette[2], 'water_multiplier': palette[3], 'isPolar': palette[4]}

            else:

                self.palettes[palette[0]] = {
                    'list': palette[1], 'water': palette[2], 'water_multiplier': palette[3], 'isPolar': palette[4]}

        # print(self.getPalette())

        self.textSpacing = 25
        self.textBoxes = []

        self.sliders = {}

        self.buttons = {}

    def createSliders(self, window):

        densitySlider = Slider(
            window, self.map_width+20, 40, self.slider_width-40, 10, min=self.density[0], max=self.density[2], step=1, initial=self.density[1])

        
        distanceSlider = Slider(window, self.map_width+20, 80,
                                self.slider_width-40, 10, min=self.min_distance[0], max=self.min_distance[2], step=1, initial=self.min_distance[1])

        connectionsSlider = Slider(window, self.map_width+20, 120, self.slider_width -
                                   40, 10, min=self.min_connections[0], max=self.min_connections[2], step=1, initial=self.min_connections[1])
        

        sidesSlider = Slider(window, self.map_width+20, 240, self.slider_width -
                     40, 10, min=self.continent_sides[0], max=self.continent_sides[2], step=1, initial=self.continent_sides[1])


        continentsSlider = Slider(window, self.map_width+20, 280,
                                  self.slider_width-40, 10, min=self.num_continents[0], max=self.num_continents[2], step=1, initial=self.num_continents[1])

        shapeSlider = Slider(window, self.map_width+20, 320,
                             self.slider_width-40, 10, min=0, max=len(self.shapes)-1, step=1, initial=1)

        colorSlider = Slider(window, self.map_width+20, 360,
                            self.slider_width-40, 10, min=0, max=len(self.palettes.keys())-1, step=1, initial=0)
        
        waterLevelsSlider = Slider(window, self.map_width+20, 560,
                                   self.slider_width-40, 10, min=self.water_levels[0], max=self.water_levels[2], step=1, initial=self.water_levels[1])
        
        waterWidthSlider = Slider(window, self.map_width+20, 600,
                                  self.slider_width-40, 10, min=self.water_width[0], max=self.water_width[2], step=1, initial=self.water_width[1])

        self.sliders['density'] = densitySlider
        self.sliders['sides'] = sidesSlider
        self.sliders['distance'] = distanceSlider
        self.sliders['connections'] = connectionsSlider
        self.sliders['continents'] = continentsSlider
        self.sliders['shape'] = shapeSlider
        self.sliders['color'] = colorSlider
        self.sliders['water_levels'] = waterLevelsSlider
        self.sliders['water_width'] = waterWidthSlider
        
        return densitySlider, sidesSlider, distanceSlider, connectionsSlider, continentsSlider, shapeSlider, colorSlider, waterLevelsSlider, waterWidthSlider
        
    def createButtons(self, window, generateNodes, changePalette, generateContinents, clearContinents, refine, redraw, autoGenerate, colorWater, exportWindow):

        nodeButton = Button(window, self.map_width+20, 160, self.slider_width -
                            40, 30, onClick=generateNodes, inactiveColour=(150, 100, 100), radius=self.buttonRadius)
        
        colorButton = Button(window, self.map_width+20, 400, self.slider_width -
                             40, 30, onClick=changePalette, inactiveColour=self.buttonColor, radius=self.buttonRadius)
        
        mapButton = Button(window, self.map_width+20, 440, self.slider_width//2 -
                           20, 30, onClick=generateContinents, inactiveColour=self.buttonColor, radius=self.buttonRadius)
        
        clearButton = Button(window, self.map_width+self.slider_width//2+10, 440, self.slider_width//2 -
                             30, 30, onClick=clearContinents, inactiveColour=self.buttonColor, radius=self.buttonRadius)

        refineButton = Button(window, self.map_width+20, 480, self.slider_width//2 -
                              20, 30, onClick=refine, inactiveColour=self.buttonColor, radius=self.buttonRadius)
        
        redrawButton = Button(window, self.map_width+self.slider_width//2+10, 480, self.slider_width//2 -
                             30, 30, onClick=redraw, inactiveColour=self.buttonColor, radius=self.buttonRadius)

        
        waterButton = Button(window, self.map_width+20, 640, self.slider_width -
                             40, 30, onClick=colorWater, inactiveColour=(100, 100, 150), radius=self.buttonRadius)
        
        autoButton = Button(window, self.map_width+20, 680, 2*self.slider_width//3 -
                            30, 30, onClick=autoGenerate, inactiveColour=(100, 150, 100), radius=self.buttonRadius)
        
        exportButton = Button(window, self.map_width+2*self.slider_width//3, 680, self.slider_width//3 -
                            20, 30, onClick=exportWindow, inactiveColour=(150, 100, 150), radius=self.buttonRadius)
        
        self.buttons['node'] = nodeButton
        self.buttons['map'] = mapButton
        self.buttons['refine'] = refineButton
        self.buttons['auto'] = autoButton
        self.buttons['color'] = colorButton
        self.buttons['water'] = waterButton
        self.buttons['redraw'] = redrawButton
        self.buttons['clear'] = clearButton
        self.buttons['export'] = exportButton
        
        return nodeButton, mapButton, clearButton, refineButton, autoButton, colorButton, waterButton, redrawButton, exportButton
    
    def createTextBoxes(self):

        black = (0,0,0)

        nodeText = Text('Node Generation', black, self.titleFont,
                        self.win_width - self.slider_width//2, 20)

        mapText = Text('Continent Generation', black, self.titleFont,
                        self.win_width - self.slider_width//2, 220)
        
        waterText = Text('Water Depth', black, self.titleFont,
                       self.win_width - self.slider_width//2, 540)

        if len(self.sliders) == 0:
            raise Exception('must create sliders before text boxes')
        
        densityText = Text('Density: ', black, self.font,
                       self.win_width - self.slider_width//2, self.sliders['density'].getY()+self.textSpacing, slider=self.sliders['density'])
        
        sidesText = Text('Continent Sides: ', black, self.font,
                         self.win_width - self.slider_width//2, self.sliders['sides'].getY()+self.textSpacing, slider=self.sliders['sides'])
        
        distanceText = Text('Maximum Distance: ', black, self.font,
                            self.win_width - self.slider_width//2, self.sliders['distance'].getY()+self.textSpacing, slider=self.sliders['distance'])
        
        connectionsText = Text('Connections: ', black, self.font,
                               self.win_width - self.slider_width//2, self.sliders['connections'].getY()+self.textSpacing, slider=self.sliders['connections'])
        
        continentsText = Text('Continents: ', black, self.font,
                              self.win_width - self.slider_width//2, self.sliders['continents'].getY()+self.textSpacing, slider=self.sliders['continents'])
        
        shapeText = Text('Refinement: ', black, self.font,
                         self.win_width - self.slider_width//2 - 25, self.sliders['shape'].getY()+self.textSpacing, slider=self.sliders['shape'], values=self.shapes)
        
        colorText = Text('Color: ', black, self.font,
                         self.win_width - self.slider_width//2 - 25, self.sliders['color'].getY()+self.textSpacing, slider=self.sliders['color'], values=[x for x in self.palettes.keys()])
        
        waterLevelsText = Text('Water Levels: ', black, self.font,
                         self.win_width - self.slider_width//2, self.sliders['water_levels'].getY()+self.textSpacing, slider=self.sliders['water_levels'])
        
        waterWidthText = Text('Water Level Width: ', black, self.font,
                               self.win_width - self.slider_width//2, self.sliders['water_width'].getY()+self.textSpacing, slider=self.sliders['water_width'])

        if len(self.buttons) == 0:
            raise Exception('must create buttons before text boxes')
        
        nodeButtonText = Text('Generate Nodes', black, self.font,
                         self.win_width - self.slider_width//2, self.buttons['node'].getY()+self.buttons['node'].getHeight()//2)
        
        colorButtonText = Text('Update Color Palette', black, self.font,
                               self.win_width - self.slider_width//2, self.buttons['color'].getY()+self.buttons['color'].getHeight()//2)

        mapButtonText = Text('Generate [ ]', black, self.font,
                             self.buttons['map'].getX()+self.buttons['map'].getWidth()//2, self.buttons['map'].getY()+self.buttons['map'].getHeight()//2)
        
        clearButtonText = Text('Clear', black, self.font,
                               self.buttons['clear'].getX()+self.buttons['clear'].getWidth()//2, self.buttons['clear'].getY()+self.buttons['clear'].getHeight()//2)
        
        refineButtonText = Text('Refine', black, self.font,
                                self.buttons['refine'].getX()+self.buttons['refine'].getWidth()//2, self.buttons['refine'].getY()+self.buttons['refine'].getHeight()//2)
        
        redrawButtonText = Text('Redraw', black, self.font,
                                self.win_width - self.slider_width//4-5, self.buttons['redraw'].getY()+self.buttons['redraw'].getHeight()//2)
        
        waterButtonText = Text('Water', black, self.font,
                               self.win_width - self.slider_width//2, self.buttons['water'].getY()+self.buttons['water'].getHeight()//2)
        
        autoButtonText = Text('Auto Generate', black, self.font,
                              self.buttons['auto'].getX()+self.buttons['auto'].getWidth()//2, self.buttons['auto'].getY()+self.buttons['auto'].getHeight()//2)
        
        exportButtonText = Text('Export', black, self.font,
                                self.buttons['export'].getX()+self.buttons['export'].getWidth()//2, self.buttons['export'].getY()+self.buttons['export'].getHeight()//2)
        
        self.textBoxes = [nodeText, mapText, waterText, nodeButtonText, mapButtonText, clearButtonText, refineButtonText, redrawButtonText, autoButtonText, colorButtonText,
                          waterButtonText, exportButtonText, densityText, sidesText, distanceText, connectionsText, continentsText, shapeText, colorText, waterLevelsText, waterWidthText]

        return self.textBoxes
    
    def getMinimumContinentSides(self):
        return self.sliders['sides'].getValue()
    
    def getMinimumConnections(self):
        return self.sliders['connections'].getValue()
    
    def getMaximumLength(self):
        return self.sliders['distance'].getValue()
    
    def getNumPoints(self):
        return int(self.sliders['density'].getValue()
                   * self.density_coefficient/self.map_width/self.win_height)
    
    def getPalette(self):
        return self.palettes[self.palette]['list']
    
    def getWater(self):
        return self.palettes[self.palette]['water']
    
    def updatePalette(self):
        paletteNames = [x for x in self.palettes.keys()]
        self.palette = paletteNames[self.sliders['color'].getValue()]

    def getSemiRandomColor(self, percent_height):
        if self.palettes[self.palette]['isPolar']:
            value = int(percent_height*(len(self.getPalette())))
            noise = random.randrange(-1, 1)

            color = self.getPalette()[min(len(self.getPalette())-1, max(
                0, value+noise))]
            
        color = self.getPalette()[random.randint(
            0, len(self.getPalette())-1)]
        
        return color
    
    def getWaterLevels(self):
        return self.sliders['water_levels'].getValue()
    
    def getWaterWidth(self):
        return self.sliders['water_width'].getValue()
    
    def getWaterMultiplier(self):
        return self.palettes[self.palette]['water_multiplier']
    
    def getWaterMinLength(self):
        levels = self.sliders['water_levels'].getValue()
        width = self.sliders['water_width'].getValue()
        return levels*width

class WorldInfo:

    def __init__(self, xMin: int, xMax: int, width: int, yMin: int, yMax: int, height: int):

        self.continents = []
        self.continentPoints = PointPartition(xMin, xMax, int(width*1.5), yMin, yMax, int(height*1.5))
        self.continentColors = []

        self.path = []
        self.pathPoints = []

        self.graph = Graph()

        self.lines = LinePartition(xMin, xMax, int(width*1.5), yMin, yMax, int(height*1.5))
        

    def clearContinents(self):
        self.continents = []
        self.continentColors = []

    def clearPath(self):
        self.path = []
        self.pathPoints = []

    def clearLines(self, xMin: int, xMax: int, width: int, yMin: int, yMax: int, height: int):
        self.lines = LinePartition(xMin, xMax, int(width*1.5), yMin, yMax, int(height*1.5))

def export_window_as_png(window, width, height):
    # Get the surface of the window
    surface = pygame.display.get_surface()

    # Create a new surface with the same dimensions as the window
    image = pygame.Surface((width, height))

    # Draw the contents of the window onto the new surface
    image.blit(window, (0, 0))

    filename = f'export/map-generator_{time.strftime("%Y-%m-%d")}_{time.time()}.png'

    # Save the new surface as a PNG file
    pygame.image.save(image, filename)

    print(f'Exported to {filename}')
