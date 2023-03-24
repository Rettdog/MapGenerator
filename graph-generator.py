import pygame
import random
from mapclasses import Line, Point, ConnectedPoint, Graph

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

# Clear the screen
window.fill(white)

graph = Graph()


# Setup Initial 
# pos1 = Point(random.randint(0, win_width),
#                       random.randint(0, win_height))
# pos2 = Point(random.randint(0, win_width),
#                       random.randint(0, win_height))
# pos3 = Point(random.randint(0, win_width),
#                       random.randint(0, win_height))
# id1 = graph.addNode(pos1)
# id2 = graph.addNode(pos2)
# id3 = graph.addNode(pos2)
# graph.addConnection(id1, id2)
# graph.addConnection(id1, id3)
# graph.addConnection(id2, id3)

# Set up the game loop
running = True
clock = pygame.time.Clock()

connectionAmount = 3
lines=[]

for i in range(250):
    pos = Point(random.randint(0, win_width),
                      random.randint(0, win_height))
    currentAmount = 0
    connectionIds = []
    for id in graph.getGraph().keys():
        node = graph.getGraph()[id]
        # if len(node[1])>=5:
        #     break
        currentLine = Line(pos, node[0])
        # currentLine.drawLine(window, green)
        foundIntersection = False
        for line in lines:
            if currentLine.isIntersecting(line):
                foundIntersection = True
                # currentLine.drawLine(window, red)
        if not foundIntersection:
            currentAmount+=1
            print(currentAmount)
            lines.append(currentLine)
            pygame.draw.line(window, black, currentLine.startPos, currentLine.endPos)
            connectionIds.append(id)

        if currentAmount==connectionAmount:
            break
    graph.addNodeWithConnections(pos, connectionIds)

for id in graph.getIds():
    currentPoint = start = graph.getGraph()[id]
    start = currentPoint[0]
    pygame.draw.circle(window, red, start.asCoordinate(), 4)
    for connectionId in graph.getGraph()[id][1]:
        end = graph.getGraph()[connectionId][0]
        pygame.draw.line(window, black, start.asCoordinate(), end.asCoordinate())

# Loop until the user clicks the close button
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update the screen
    pygame.display.update()

    # Limit the frame rate
    clock.tick(60)

# Clean up
pygame.quit()
