import pygame
import random
import time
from mapclasses import Line, Point, ConnectedPoint, Graph
from mapclasses import export_window_as_png
import numpy as np

# Initialize Pygame
pygame.init()

# Set up the window
win_width = 1000
win_height = 750
window = pygame.display.set_mode((win_width, win_height))
pygame.display.set_caption("Random Lines")

# Set up the colors
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)

# continentColors = ['#c2c5aa', '#b6ad90',
#     '#a68a64', '#656d4a', '#333d29', '#676f54']

colorPallete = [pygame.Color('#F0D197'), pygame.Color('#b6ad90'),
                pygame.Color('#a68a64'), pygame.Color('#656d4a'), pygame.Color('#333d29'), 
                pygame.Color('#676f54'), pygame.Color('#7d7d70'), pygame.Color('#858A89'), pygame.Color('#faf3dd')]

polarColorPallete = colorPallete.copy()
polarColorPallete.reverse()

polarColorPallete.extend(colorPallete)

water = (0, 50, 100)

# Clear the screen
window.fill(white)

graph = Graph()

# Set up the game loop
running = True
clock = pygame.time.Clock()

#constants
connectionAmount = 3
minContinentSides = 15
maxLength = 45
numPoints = 750

lines=[]

for i in range(numPoints):
    pos = Point(random.randint(0, win_width),
                      random.randint(0, win_height))
    currentAmount = 0
    connectionIds = []
    for id in graph.getGraph().keys():
        node = graph.getGraph()[id]
        currentLine = Line(pos, node[0])

        if currentLine.calculateLength() > maxLength:
            continue

        shouldDrawLine = True
        for line in lines:
            if currentLine.isIntersecting(line):
                shouldDrawLine=False
                break
        if shouldDrawLine:
            currentAmount+=1
            lines.append(currentLine)
            pygame.draw.line(window, black, currentLine.startPos, currentLine.endPos)
            connectionIds.append(id)

        if currentAmount>=connectionAmount:
            break
    graph.addNodeWithConnections(pos, connectionIds)

for id in graph.getIds():
    currentPoint = start = graph.getGraph()[id]
    start = currentPoint[0]
    pygame.draw.circle(window, red, start.asCoordinate(), 4)
    for connectionId in graph.getGraph()[id][1]:
        end = graph.getGraph()[connectionId][0]
        pygame.draw.line(window, black, start.asCoordinate(), end.asCoordinate())

continents = []
continentColors = []

path = []
pathPoints = []

def initPath():
    global path, pathPoints
    path = []
    pathPoints = []
    currentId = graph.getRandomNodes(1)[0]
    path.append(currentId)
    pathPoints.append(graph.getGraph()[currentId][0].asCoordinate())
    # pygame.draw.circle(window, blue, graph.getGraph()[currentId][0].asCoordinate(), 5)

def step():
    global path, pathPoints
    currentId = path[-1]
    if len(path)>1:
        nextId = graph.getRandomConnection(currentId, path[1:])
    else:
        nextId = graph.getRandomConnection(currentId, [])

    if nextId == -1:
        nextId = graph.getRandomConnection(currentId, [])
        return -1

    if nextId in path:
        if len(path) > minContinentSides:
            if nextId in path[:-minContinentSides]:
                firstIndex = path.index(nextId)
                # print(f'nextId: {nextId} firstIndex: {firstIndex}')
                path = path[firstIndex:]
                # print(f'path: {path}')
                pathPoints = pathPoints[firstIndex:]
                continents.append(pathPoints)

                value = int(2+pathPoints[0][1]/win_height*(len(polarColorPallete)-4))
                print(f'latitude: {value}')
                color = polarColorPallete[random.randint(value-2, value+2)]

                continentColors.append(color)
                return 1
            else:
                return -1
        else:
            return -1
    if nextId != -1:
        path.append(nextId)
        pathPoints.append(graph.getGraph()[nextId][0].asCoordinate())
    # pygame.draw.line(window, blue, graph.getGraph()[currentId][0].asCoordinate(),
    #                  graph.getGraph()[nextId][0].asCoordinate(), 2)
    # pygame.draw.circle(window, blue, graph.getGraph()[
    #                    nextId][0].asCoordinate(), 5)
    if len(path) > maxLength*2:
        print('length exceded')
        return -1
    return 0
    
def fill():
    if len(path)<3:
        return
    pygame.draw.polygon(window, green, pathPoints)


def drawContinents():
    opacity = 120
    for i in range(len(continents)):

        path = continents[i]
        color = continentColors[i]

        coefficient = max((i/len(continents))**0.8, 0.5)

        if len(path) < 3:
            continue
        try:
            pygame.draw.polygon(
                window, (coefficient*pygame.Color(color).r, coefficient*pygame.Color(
                    color).g, coefficient*pygame.Color(color).b), path)
        except:
            pygame.draw.polygon(
                window, (0,0,0), path)

def generateContinent():    

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
        if timeout>1000:
            # print("timeout")
            break
    drawContinents()


# Loop until the user clicks the close button
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            generateContinent()

        if event.type == pygame.KEYDOWN:

            # make screen white
            if event.key == pygame.K_c:
                window.fill(white)

            # export current screen to .png file
            if event.key == pygame.K_e:
                filename = f'export/{time.strftime("%Y-%m-%d_%H-%M-%S")}.png'
                export_window_as_png(window, filename)

            # add water background
            if event.key == pygame.K_r:
                window.fill(water)
                drawContinents()

            # blur continent colors
            if event.key == pygame.K_g:
                window.set_colorkey(water)
                waterMask = pygame.mask.from_surface(window)
                waterMask.invert()
                # print(waterMask)
                window.fill(water)
                drawContinents()
                blurred_image = pygame.transform.gaussian_blur(window, 10)
                rect = blurred_image.get_rect()
                rect.center = (win_width//2, win_height//2)
                blurred_image.blit(waterMask.to_surface(setcolor=water, unsetcolor=(0,0,0,0)), rect)
                window.blit(blurred_image, rect)

                print('blurred')

            # convert to black and white
            if event.key == pygame.K_w:
                window.set_colorkey(water)
                waterMask = pygame.mask.from_surface(window)
                rect = window.get_rect()
                rect.center = (win_width//2, win_height//2)
                window.blit(waterMask.to_surface(), rect, None, 0)

        # Get the state of all keys on the keyboard
        keys = pygame.key.get_pressed()

        # repeated generate continents
        if keys[pygame.K_SPACE]:
            generateContinent()

        # roughen edges with dots
        if keys[pygame.K_d]:
            for j in range(5, 1, -1):
                for i in range(0, 500):
                    x = random.randint(0, win_width-1)
                    y = random.randint(0, win_height-1)
                    color = window.get_at((x, y))
                    pygame.draw.circle(window, color, (x, y), j)

        # roughen edges with squares
        if keys[pygame.K_s]:
            for j in range(5, 1, -1):
                for i in range(0, 500):
                    x = random.randint(0, win_width-1)
                    y = random.randint(0, win_height-1)
                    color = window.get_at((x, y))
                    rect = pygame.Rect(x-j//2, y-j//2, j, j)
                    pygame.draw.rect(window, color, rect)

        # roughen edges with polygons
        if keys[pygame.K_p]:
            for j in range(5, 1, -1):
                for i in range(0, 500):
                    x = random.randint(0, win_width-1)
                    y = random.randint(0, win_height-1)
                    x1 = random.randint(x-j, x+j+1)
                    y1 = random.randint(y-j, y+j+1)
                    x2 = random.randint(x-j, x+j+1)
                    y2 = random.randint(y-j, y+j+1)
                    x3 = random.randint(x-j, x+j+1)
                    y3 = random.randint(y-j, y+j+1)
                    x4 = random.randint(x-j, x+j+1)
                    y4 = random.randint(y-j, y+j+1)
                    color = window.get_at((x, y))
                    pygame.draw.polygon(window, color, [(x1, y1), (x2, y2), (x3, y3), (x4, y4)])
        




    

    # Update the screen
    pygame.display.update()

    # Limit the frame rate
    clock.tick(60)

# Clean up
pygame.quit()
