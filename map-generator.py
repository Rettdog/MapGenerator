import pygame
import random
from mapclasses import Line, Point, ConnectedPoint

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

# Set up the lines
lines = []
for i in range(25):
    start_pos = Point(random.randint(0, win_width), random.randint(0, win_height))
    end_pos = Point(random.randint(0, win_width), random.randint(0, win_height))
    lines.append(Line(start_pos, end_pos))

points = []
connectedPoints = []

# for line in lines:
#     line.display()

# Clear the screen
window.fill(white)

# Draw the lines
for line in lines:
    pygame.draw.line(window, black, line.startPos, line.endPos, 2)

# Set up the game loop
running = True
clock = pygame.time.Clock()

currentLineIndex = 0

while currentLineIndex < len(lines):
    checkingLineIndex = 0
    while checkingLineIndex < len(lines):
        intersection = lines[checkingLineIndex].findIntersection(
            lines[currentLineIndex])
        if intersection == None:
            checkingLineIndex += 1
            continue
        points.append(intersection)

        point = ConnectedPoint(intersection)
        pygame.draw.circle(window, red, intersection.asCoordinate(), 2)
        # point.addConnection(lines[currentLineIndex].start)
        # point.addConnection(lines[currentLineIndex].end)
        # point.addConnection(lines[checkingLineIndex].start)
        # point.addConnection(lines[checkingLineIndex].end)
        point.addLine(lines[currentLineIndex])
        point.addLine(lines[checkingLineIndex])

        connectedPoints.append(point)
        checkingLineIndex += 1
        
    currentLineIndex+=1

print(len(connectedPoints))

lines = []

for connectedPoint in connectedPoints:
    for checkingPoint in connectedPoints:
        for line1 in connectedPoint.lines:
            for line2 in checkingPoint.lines:
                if line1 == line2:
                    lines.append(Line(connectedPoint, checkingPoint))

# window.fill(white)

for line in lines:
    pygame.draw.line(window, blue, line.start.asCoordinate(), line.end.asCoordinate())

# for connectedPoint in connectedPoints:
#     pygame.draw.circle(
#         window, red, connectedPoint.asCoordinate(), 4)
#     for connection in connectedPoint.connections:
#         for checkPoint in connectedPoints:
            
#             if checkPoint.asCoordinate() == connection.asCoordinate():
#                 print(
#                     f'checkPoint: {checkPoint.asCoordinate()} connection: {connection.asCoordinate()}')
#                 pygame.draw.line(window, blue, connectedPoint.asCoordinate(),
#                                 connection.asCoordinate())
#                 break
#             try:
#                 connectedPoint.removeConnection(connection)
#             except:
#                 print('error')
            
            
        
    pygame.display.update()
    clock.tick(60)

# Loop until the user clicks the close button
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # for line in lines:
    #     if not line.isParellel(lines[currentLine]):
    #         intersection = line.findIntersection(lines[currentLine])
    #         intersection.display()
    #         pygame.draw.circle(window, red, (intersection.x, intersection.y), 5)
    #         pygame.display.update()

    #     clock.tick(60)

    # Update the screen
    pygame.display.update()

    # Limit the frame rate
    clock.tick(60)

# Clean up
pygame.quit()
