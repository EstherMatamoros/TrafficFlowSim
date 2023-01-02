import random
import time
import threading
import pygame
import sys

# Default values of signal timers
defaultPGreen = {0: 10, 1: 10, 2: 10, 3: 10}
defaultPRed = 150

signals = []
noOfSignals = 4
currentPGreen = 0  # Indicates which signal is green currently
nextPGreen = (currentPGreen + 1) % noOfSignals  # Indicates which signal will turn green next
# currentyellow = 0   # Indicates whether yellow signal is on or off

speedsp = {'person1': 0.5, 'person2': 0.4, 'person3': 0.4, 'person4': 0.6}  # average speeds of pedestrians

# Coordinates of pedestrians' start
a = {'right': [0, 0, 0], 'down': [890, 830, 809], 'left': [1400, 1400, 1400], 'up': [485, 500, 526]}  # -15 -30
b = {'right': [223, 258, 269], 'down': [0, 0, 0], 'left': [546, 567, 586], 'up': [800, 800, 800]}  # 25 41

pedestrians = {'right': {0: [], 1: [], 2: [], 'crossed': 0}, 'down': {0: [], 1: [], 2: [], 'crossed': 0},
               'left': {0: [], 1: [], 2: [], 'crossed': 0}, 'up': {0: [], 1: [], 2: [], 'crossed': 0}}
pedestrianTypes = {0: 'person1', 1: 'person2', 2: 'person3', 3: 'person4'}
directionNumbers = {0: 'right', 1: 'down', 2: 'left', 3: 'up'}

# Coordinates of signal image, timer, and pedestrian count  (x y) [right,down,left,up}
psignalCoods = [(460, 200), (850, 210), (860, 630), (455, 630)]
psignalTimerCoods = [(470, 690), (470, 170), (860, 180), (870, 690)]  # up,right,down,left

# Coordinates of stop lines
stopLinesP = {'right': 560, 'down': 340, 'left': 810, 'up': 575}
defaultStop2 = {'right': 550, 'down': 330, 'left': 820, 'up': 590}
# stops = {'right': [580,580,580], 'down': [320,320,320], 'left': [810,810,810], 'up': [545,545,545]}

# Gap between pedestrians
stoppingGap = 25  # stopping gap
movingGap = 25  # moving gap

pygame.init()
simulation = pygame.sprite.Group()


class PedestrianSignal:
    def __init__(self, red, green):
        self.red = red
        self.green = green
        self.signalText = ""


class Pedestrian(pygame.sprite.Sprite):
    def __init__(self, lane, pedestrianClass, direction_number, direction):
        pygame.sprite.Sprite.__init__(self)
        self.lane = lane
        self.pedestrianClass = pedestrianClass
        self.speed = speedsp[pedestrianClass]
        self.direction_number = direction_number
        self.direction = direction
        self.a = a[direction][lane]
        self.b = b[direction][lane]
        self.crossed = 0
        pedestrians[direction][lane].append(self)
        self.indea = len(pedestrians[direction][lane]) - 1
        path = "images/" + "Pdirection/" + direction + "/" + pedestrianClass + ".png"
        self.image = pygame.image.load(path)

        if len(pedestrians[direction][lane]) > 1 and pedestrians[direction][lane][
            self.indea - 1].crossed == 0:  # if more than 1 pedestrian in the lane of pedestrian before it has crossed stop line
            if (direction == 'right'):
                self.stop = pedestrians[direction][lane][self.indea - 1].stop - pedestrians[direction][lane][
                    self.indea - 1].image.get_rect().width - stoppingGap  # setting stop coordinate as: stop coordinate of next pedestrian - width of next pedestrian - gap
            elif (direction == 'left'):
                self.stop = pedestrians[direction][lane][self.indea - 1].stop + pedestrians[direction][lane][
                    self.indea - 1].image.get_rect().width + stoppingGap
            elif (direction == 'down'):
                self.stop = pedestrians[direction][lane][self.indea - 1].stop - pedestrians[direction][lane][
                    self.indea - 1].image.get_rect().height - stoppingGap
            elif (direction == 'up'):
                self.stop = pedestrians[direction][lane][self.indea - 1].stop + pedestrians[direction][lane][
                    self.indea - 1].image.get_rect().height + stoppingGap
        else:
            self.stop = defaultStop2[direction]

        # Set new starting and stopping coordinate
        if (direction == 'right'):
            temp = self.image.get_rect().width + stoppingGap
            a[direction][lane] -= temp
        elif (direction == 'left'):
            temp = self.image.get_rect().width + stoppingGap
            a[direction][lane] += temp
        elif (direction == 'down'):
            temp = self.image.get_rect().height + stoppingGap
            b[direction][lane] -= temp
        elif (direction == 'up'):
            temp = self.image.get_rect().height + stoppingGap
            b[direction][lane] += temp
        simulation.add(self)

    def render(self, screen):
        screen.blit(self.image, (self.a, self.b))

    def move(self):
        if self.direction == 'right':
            if (self.crossed == 0 and self.a + self.image.get_rect().width > stopLinesP[
                self.direction]):  # if the image has crossed stop line now
                self.crossed = 1
            if ((self.a + self.image.get_rect().width <= self.stop or self.crossed == 1 or (currentPGreen == 0)) and (
                    self.indea == 0 or self.a + self.image.get_rect().width < (
                    pedestrians[self.direction][self.lane][self.indea - 1].a - movingGap))):
                # (if the image has not reached its stop coordinate or has crossed stop line or has green signal) and (it is either the first pedestrian in that lane or it is has enough gap to the next pedestrian in that lane)
                self.a += self.speed  # move the pedestrian
        elif (self.direction == 'down'):
            if (self.crossed == 0 and self.b + self.image.get_rect().height > stopLinesP[self.direction]):
                self.crossed = 1
            if ((self.b + self.image.get_rect().height <= self.stop or self.crossed == 1 or (currentPGreen == 1)) and (
                    self.indea == 0 or self.b + self.image.get_rect().height < (
                    pedestrians[self.direction][self.lane][self.indea - 1].b - movingGap))):
                self.b += self.speed
        elif (self.direction == 'left'):
            if (self.crossed == 0 and self.a < stopLinesP[self.direction]):
                self.crossed = 1
            if ((self.a >= self.stop or self.crossed == 1 or (currentPGreen == 2)) and (self.indea == 0 or self.a > (
                    pedestrians[self.direction][self.lane][self.indea - 1].a + pedestrians[self.direction][self.lane][
                self.indea - 1].image.get_rect().width + movingGap))):
                self.a -= self.speed
        elif (self.direction == 'up'):
            if (self.crossed == 0 and self.b < stopLinesP[self.direction]):
                self.crossed = 1
            if ((self.b >= self.stop or self.crossed == 1 or (currentPGreen == 3)) and (self.indea == 0 or self.b > (
                    pedestrians[self.direction][self.lane][self.indea - 1].b + pedestrians[self.direction][self.lane][
                self.indea - 1].image.get_rect().height + movingGap))):
                self.b -= self.speed


# Initialization of signals with default values
def initialize():
    ts1 = PedestrianSignal(0, defaultPGreen[0])
    signals.append(ts1)
    ts2 = PedestrianSignal(ts1.red + ts1.green, defaultPGreen[1])
    signals.append(ts2)
    ts3 = PedestrianSignal(defaultPRed, defaultPGreen[2])
    signals.append(ts3)
    ts4 = PedestrianSignal(defaultPRed, defaultPGreen[3])
    signals.append(ts4)
    repeat()


def repeat():
    global currentPGreen, nextPGreen
    while (signals[currentPGreen].green > 0):  # while the timer of current green signal is not zero
        updateValues()
        time.sleep(1)
    # reset stop coordinates of lanes and pedestrians 
    for i in range(0, 3):
        for pedestrian in pedestrians[directionNumbers[currentPGreen]][i]:
            pedestrian.stop = defaultStop2[directionNumbers[currentPGreen]]

    # reset all signal times of current signal to default times
    signals[currentPGreen].green = defaultPGreen[currentPGreen]
    signals[currentPGreen].red = defaultPRed

    currentPGreen = nextPGreen  # set next signal as green signal
    nextPGreen = (currentPGreen + 1) % noOfSignals  # set next green signal
    signals[nextPGreen].red = signals[
        currentPGreen].green  # set the red time of next to next signal as (yellow time + green time) of next signal
    repeat()


# Update values of the signal timers after every second
def updateValues():
    for i in range(0, noOfSignals):
        if (i == currentPGreen):
            signals[i].green -= 1
        else:
            signals[i].red -= 1


# Generating pedestrians in the simulation
def generatepedestrians():
    while (True):
        pedestrian_Type = random.randint(0, 3)
        lane_number = random.randint(1, 2)
        temp = random.randint(0, 99)
        direction_number = 0
        dist = [10, 20, 30, 100]
        if (temp < dist[0]):
            direction_number = 0
        elif (temp < dist[1]):
            direction_number = 1
        elif (temp < dist[2]):
            direction_number = 2
        elif (temp < dist[3]):
            direction_number = 3
        Pedestrian(lane_number, pedestrianTypes[pedestrian_Type], direction_number, directionNumbers[direction_number])
        time.sleep(1)


class Main:
    thread1 = threading.Thread(name="initialization", target=initialize, args=())  # initialization
    thread1.daemon = True
    thread1.start()

    # Colours 
    black = (0, 0, 0)
    white = (255, 255, 255)

    # Screensize 
    screenWidth = 1400
    screenHeight = 800
    screenSize = (screenWidth, screenHeight)

    # Setting background image i.e. image of intersection
    background = pygame.image.load('images/intersection.png')

    screen = pygame.display.set_mode(screenSize)
    pygame.display.set_caption("SIMULATION")

    # Loading signal images and font
    PredSignal = pygame.image.load('images/signals/Pred.png')
    # yellowSignal = pygame.image.load('images/signals/yellow.png')
    PgreenSignal = pygame.image.load('images/signals/Pgreen.png')
    font = pygame.font.Font(None, 30)

    thread2 = threading.Thread(name="generatepedestrians", target=generatepedestrians,
                               args=())  # Generating pedestrians
    thread2.daemon = True
    thread2.start()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        screen.blit(background, (-260, -50))  # display background in simulation
        for i in range(0, noOfSignals):  # display signal and set timer according to current status: green or red
            if i == currentPGreen:
                signals[i].signalText = signals[i].green
                screen.blit(PgreenSignal, psignalCoods[i])
            else:
                if signals[i].red <= 10:
                    signals[i].signalText = signals[i].red
                else:
                    signals[i].signalText = "---"
                screen.blit(PredSignal, psignalCoods[i])
        signalTexts = ["", "", "", ""]

        # display signal timer
        for i in range(0, noOfSignals):
            signalTexts[i] = font.render(str(signals[i].signalText), True, white, black)
            screen.blit(signalTexts[i], psignalTimerCoods[i])

        # display the pedestrians
        for pedestrian in simulation:
            screen.blit(pedestrian.image, [pedestrian.a, pedestrian.b])
            pedestrian.move()
        pygame.display.update()


Main()
