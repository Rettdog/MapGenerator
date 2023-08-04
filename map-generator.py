import pygame_widgets
from pygame_widgets.slider import Slider
from pygame_widgets.textbox import TextBox
from pygame_widgets.button import Button
import pygame
import random
import time
from mapclasses import Line, Point, Graph, WindowInfo, WorldInfo, LinePartition
from mapclasses import export_window_as_png
import numpy as np

# TODO: migrate some functions to WorldInfo class?
# TODO: implement make file
# TODO: make outlines for certain palettes to make coastlines?
# TODO: Use sets to make depth first search (continent generation) more efficient

# Initialize Pygame
pygame.init()

# create basic colors
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)

# Set up constants
map_width = 1000
slider_width = 300
win_height = 750

font = pygame.font.Font('freesansbold.ttf', 15)
titleFont = pygame.font.Font('freesansbold.ttf', 20)

default_density = (1, 85, 150)
default_continent_sides = (1, 10, 99)
default_min_distance = (1, 55, 99)
default_min_connections = (1, 3, 5)
default_num_continents = (1, 35, 100)
default_water_levels = (1,8,20)
default_water_width = (10,30,100)

density_coefficient = 5*10**6

info = WindowInfo(map_width, slider_width, win_height, font, titleFont, default_density, 
                  default_continent_sides, default_min_distance, default_min_connections, 
                  default_num_continents, density_coefficient, default_water_levels, default_water_width)

# Set up the window
window = pygame.display.set_mode((info.win_width, info.win_height))
pygame.display.set_caption("Map Generator")

# Set up sliders
densitySlider, sidesSlider, distanceSlider, connectionsSlider, continentsSlider, shapeSlider, colorSlider, waterLevelsSlider, waterWidthSlider = info.createSliders(window)

#Set up buttons
nodeButton, mapButton, clearButton, refineButton, autoButton, colorButton, waterButton, redrawButton, exportButton = info.createButtons(
    window, lambda: generateNodes(), lambda: updateColor(), lambda:  generateMultipleContinents(), lambda: clearContinents(), lambda: refine(), lambda: redraw(), lambda: autoGenerate(), lambda: refine('water'), lambda: exportFromButton())

# Set up text boxes
textBoxes = info.createTextBoxes()

# Clear the screen
window.fill(white)

world = WorldInfo(0, info.map_width, info.getMaximumLength(),
                  0, info.win_height, info.getMaximumLength())

#currently takes about 5 seconds
def generateNodes():
    startTime = time.time()
    drawLoading()

    world.graph.reset(info.getNumPoints())

    pygame.draw.rect(window, white, pygame.Rect(
        0, 0, info.map_width, info.win_height))

    world.graph.fillMatrixRandom(0, 0, info.map_width, info.win_height)
    world.graph.partition(0, info.map_width, info.getMaximumLength(), 0, info.win_height, info.getMaximumLength())

    world.clearLines(0, info.map_width, info.getMaximumLength(), 0, info.win_height, info.getMaximumLength())

    needConnections = list(range(world.graph.size))

    iterations = 0
    while len(needConnections) > world.graph.size*0.05 and iterations < 5:

        for currentId in needConnections:

            #saves a lot of time
            if sum(world.graph.matrix[currentId, :]) >= info.getMinimumConnections():
                continue

            currentNode = world.graph.getNode(currentId)

            closeIds = world.graph.getCloseIds(currentId).copy()
            random.shuffle(closeIds)
            for checkingId in closeIds:
                checkingNode = world.graph.getNode(checkingId)

                currentLine = Line(currentNode, checkingNode)

                # not the bottle neck
                if currentLine.calculateLength() > info.getMaximumLength():
                    closeIds.remove(checkingId)
                    continue

                # takes 3 seconds (current bottleneck)
                shouldDrawLine = True
                # print(f'total lines: {lines.totalLines}')

                closeLines = world.lines.getCloseLines(currentNode).copy()

                # print(f'close lines: {len(closeLines)}')
                for line in closeLines:
                    if currentLine.isIntersecting(line):
                        shouldDrawLine=False
                        break

                if shouldDrawLine:
                    world.lines.addLine(currentLine)
                    world.graph.addConnection(currentId, checkingId)

                    #saves 4 seconds
                    if sum(world.graph.matrix[currentId, :]) > info.getMinimumConnections():
                        continue
                    # if sum(world.graph.matrix[checkingId, :]) > info.getMinimumConnections():
                    #     removeIds.add(checkingId)
            
        needConnections = [x for x in needConnections if sum(
            world.graph.matrix[x, :]) < info.getMinimumConnections()]
        
        iterations+=1

    endTime = time.time()
    print(f'time to create graph: {endTime-startTime}')

    # not the bottleneck
    for line in world.lines.allLines:

        pygame.draw.line(window, black, line.start, line.end)

    for node in world.graph.getAllNodes():

        pygame.draw.circle(window, red, node, 4)

    pygame.display.update()

def initPath():
    world.clearPath()
    currentId = world.graph.getRandomIds(1)[0]
    world.path.append(currentId)
    world.pathPoints.append(world.graph.getNode(currentId))
    # pygame.draw.circle(window, blue, graph.getGraph()[currentId][0].asCoordinate(), 5)

def step():
    minContinentSides = sidesSlider.getValue()
    currentId = world.path[-1]
    if len(world.path) > 1:
        nextId = world.graph.getCloseRandomConnection(currentId, world.path[0], world.path[1:], 2)
    else:
        nextId = world.graph.getRandomConnection(currentId)

    if nextId == -1:
        nextId = world.graph.getCloseRandomConnection(currentId, world.path[0], world.path[1:], 2)
        return -1

    if nextId in world.path:
        if len(world.path) > minContinentSides:
            if nextId in world.path[:-minContinentSides]:
                firstIndex = world.path.index(nextId)
                path = world.path[firstIndex:]
                pathPoints = world.pathPoints[firstIndex:]
                world.continents.append(pathPoints)
                for point in pathPoints:
                    world.continentPoints.addPoint(point)

                color = info.getSemiRandomColor(
                        pathPoints[0][1]/info.win_height)

                world.continentColors.append(color)
                return 1
            else:
                return -1
        else:
            return -1
    if nextId != -1:
        world.path.append(nextId)
        world.pathPoints.append(world.graph.getNode(nextId))

        # # Remove next two lines
        # Line(world.pathPoints[-2], world.pathPoints[-1]).drawLine(window, black)
        # pygame.display.update()

    if len(world.path) > 100:
        return -1
    return 0
    
def fill():
    if len(world.path) < 3:
        return
    pygame.draw.polygon(window, green, world.pathPoints)

def drawContinents():
    drawLoading()
    for i in range(len(world.continents)):

        path = world.continents[i]
        color = world.continentColors[i]

        coefficient = max((i/len(world.continents))**0.8, 0.5)

        if len(path) < 3:
            continue
        try:
            pygame.draw.polygon(
                window, (coefficient*pygame.Color(color).r, coefficient*pygame.Color(
                    color).g, coefficient*pygame.Color(color).b), path)
        except:
            pygame.draw.polygon(
                window, (0,0,0), path)
    pygame.display.update()

def generateContinent():
    startTime = time.time()
    drawLoading()
    if world.graph.nextIndex == 0:
        return
    timeout = 0
    createdContinent = False
    while not createdContinent:
        initPath()
        isStepping = True
        while isStepping:
            stepOutcome = step()
            if stepOutcome == 1:
                createdContinent = True
                isStepping = False
            if stepOutcome == -1:
                isStepping = False
        timeout+=1
        if timeout>200:
            break
    endTime = time.time()
    # print(f'time to generate continent: {endTime-startTime} (timeout={timeout})')
    redraw()

def updateColor():
    drawLoading()
    print('update color')
    info.updatePalette()
    world.continentColors = []
    for continent in world.continents:
        color = info.getSemiRandomColor(continent[0][1]/info.win_height)
        world.continentColors.append(color)
    redraw()

def generateMultipleContinents():
    drawLoading()
    pygame.draw.rect(window, info.getWater(), pygame.Rect(
        0, 0, map_width, info.win_height))
    for _ in range(info.sliders['continents'].getValue()):
        generateContinent()
    redraw()
    pygame.display.update()

def waterDepth(x,y, color):
    point:Point = (x, y)
    minLength = info.getWaterMinLength()
    width = info.getWaterWidth()
    multiplier = info.getWaterMultiplier()
    sections = 6
    firstLayerMultiplier = 1.1

    for continentPoint in world.continentPoints.getClosePoints((x,y), (width*6)//world.continentPoints.partitions['width']):

        length = Line(continentPoint, (x,y)).calculateLength()

        if length < minLength:
            minLength = length
            if minLength < width*firstLayerMultiplier:
                layer = minLength//(width*firstLayerMultiplier)
                offset = int(random.randrange(1, 3) -
                            multiplier*layer)
                color[0] = max(0, min(info.getWater()[0] + offset, 255))
                color[1] = max(0, min(info.getWater()[1] + offset, 255))
                color[2] = max(0, min(info.getWater()[2] + offset, 255))

                return (layer, color)

    layer = (minLength-width*(firstLayerMultiplier-1))//width
    offset = int(random.randrange(1, 3) -
                    multiplier*layer)
    color[0] = max(0, min(info.getWater()[0] + offset, 255))
    color[1] = max(0, min(info.getWater()[1] + offset, 255))
    color[2] = max(
        0, min(info.getWater()[2] + offset, 255))
    
    return (layer, color)
    
def refine(shape=None, attemptsPerIteration=10000):
    drawLoading()
    if shape is None:
        shape = info.shapes[shapeSlider.getValue()]
    print(shape)
    if shape == 'dot' or shape == 'dot [d]':

        for j in range(5, 1, -1):
            for i in range(0, attemptsPerIteration):
                x = random.randint(0, map_width-1)
                y = random.randint(0, info.win_height-1)
                color = window.get_at((x, y))
                if color == info.getWater():
                    layer, color = waterDepth(x, y, color)
                    pygame.draw.circle(
                        window, color, (x, y), j*(layer+1)/2)
                else:
                    pygame.draw.circle(window, color, (x, y), j)

    elif shape == 'square' or shape == 'square [s]':

        for j in range(6, 1, -1):
            for i in range(0, attemptsPerIteration):
                x = random.randint(0, map_width-1)
                y = random.randint(0, info.win_height-1)
                color = window.get_at((x, y))
                if color == info.getWater():
                    layer, color = waterDepth(x, y, color)
                    rect = pygame.Rect(
                        x-j*(layer+1)//2, y-j*(layer+1)//2, j*(layer+1), j*(layer+1))
                    pygame.draw.rect(window, color, rect)
                else:
                    rect = pygame.Rect(x-j//2, y-j//2, j, j)
                    pygame.draw.rect(window, color, rect)

    elif shape == 'triangle' or shape == 'triangle [p]':

        for j in range(7, 2, -1):
            for i in range(0, attemptsPerIteration):
                x = random.randint(0, map_width-1)
                y = random.randint(0, info.win_height-1)
                width = j
                color = window.get_at((x, y))
                if color == info.getWater():
                    layer, color = waterDepth(x, y, color)
                    width = int(j+layer*2)
                x1 = random.randint(x-width, x+width+1)
                y1 = random.randint(y-width, y+width+1)
                x2 = random.randint(x-width, x+width+1)
                y2 = random.randint(y-width, y+width+1)
                x3 = random.randint(x-width, x+width+1)
                y3 = random.randint(y-width, y+width+1)

                pygame.draw.polygon(window, color, [(x1, y1), (x2, y2), (x3, y3)])

    elif shape == 'blur' or shape == 'blur [g]':

        window.set_colorkey(info.getWater())
        waterMask = pygame.mask.from_surface(window)
        waterMask.invert()
        # print(waterMask)
        #window.fill(water)
        #drawContinents()
        blurred_image = pygame.transform.gaussian_blur(window, 3)
        rect = blurred_image.get_rect()
        rect.center = (info.win_width//2, info.win_height//2)
        blurred_image.blit(waterMask.to_surface(
            setcolor=info.getWater(), unsetcolor=(0, 0, 0, 0)), rect)
        window.blit(blurred_image, rect)

    elif shape == 'water' or shape == 'water [o]':

        approachingEnd = False
        while not approachingEnd:
            for j in range(5, 1, -1):
                totalHits = 0
                for i in range(0, attemptsPerIteration):
                    x = random.randint(0, info.win_width-1)
                    y = random.randint(0, info.win_height-1)
                    color = window.get_at((x, y))
                    if color == info.getWater():
                        layer, color = waterDepth(x, y, color)
                        if layer > 1:
                            pygame.draw.circle(
                                window, color, (x, y), j*(layer+1)/1.5)
                            totalHits += 1
                if totalHits < attemptsPerIteration/100:
                    approachingEnd = True

    elif shape == 'black-white':

        window.set_colorkey(info.getWater())
        waterMask = pygame.mask.from_surface(window)
        rect = window.get_rect()
        rect.center = (info.win_width//2, info.win_height//2)
        window.blit(waterMask.to_surface(), rect, None, 0)

    pygame.display.update()

def clearContinents():
    drawLoading()
    world.clearContinents()
    world.continentPoints.reset()
    redraw()

def redraw():
    pygame.draw.rect(window, info.getWater(), pygame.Rect(
        0, 0, info.map_width, info.win_height))
    drawContinents()

def drawLoading():
    text = info.font.render('Loading...', True, (0, 0, 0))
    rect = text.get_rect()
    rect.center = (info.win_width-info.slider_width//2, info.win_height-20)
    window.blit(text, rect)
    pygame.display.update()

def autoGenerate():
    drawLoading()
    clearContinents()
    updateColor()
    generateNodes()
    generateMultipleContinents()
    refine('water')
    drawContinents()
    refine(shape='dot', attemptsPerIteration=500)
    for i in range(25):
        refine(attemptsPerIteration=1500)

def exportFromButton():
    pygame.display.update()
    export_window_as_png(window, info.map_width, info.win_height)

running = True
clock = pygame.time.Clock()

# Loop until the user clicks the close button
while running:

    # Handle events
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False

        # if event.type == pygame.MOUSEBUTTONDOWN:
        #     generateContinent()

        if event.type == pygame.KEYDOWN:

            # make screen white
            if event.key == pygame.K_c:
                window.fill(white)

            # export current screen to .png file
            if event.key == pygame.K_e:
                export_window_as_png(window, info.map_width, info.win_height)

            # add water background
            if event.key == pygame.K_r:
                window.fill(info.getWater())
                drawContinents()

            # blur continent colors
            if event.key == pygame.K_g:
                refine('blur', 1500)

            # convert to black and white
            if event.key == pygame.K_w:
                refine('black-white')

        # Get the state of all keys on the keyboard
        keys = pygame.key.get_pressed()

        # repeated generate continents
        if keys[pygame.K_SPACE]:
            generateContinent()

        # roughen edges with dots
        if keys[pygame.K_d]:
            refine('dot', 1000)

        # roughen edges with squares
        if keys[pygame.K_s]:
            refine('square', 1000)
                    
        # roughen edges with triangles
        if keys[pygame.K_p]:
            refine('triangle', 1000)

        # add color to just deep ocean for faster rendering of other roughening algorthims
        if keys[pygame.K_o]:
            refine('water', 1000)

    pygame.draw.rect(window, white, pygame.Rect(info.map_width, 0, info.slider_width, info.win_height))

    pygame_widgets.update(events)

    for box in info.textBoxes:
        box.render(window)

    pygame.display.update()

    # Limit the frame rate
    clock.tick(60)

# Clean up
pygame.quit()
