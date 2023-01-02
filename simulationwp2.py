import random
import time
import threading
import pygame
import sys
import os

# Default values of signal timers
defaultGreen = {0: 10, 1: 10, 2: 10, 3: 10}
defaultRed = 150
defaultYellow = 5

# For violations
violations = 0
violationsCoods = (900, 50)

timeElapsed = 0
simulationTime = 300
timeElapsedCoods = (900, 70)

signals = []
noOfSignals = 4
currentGreen = 0  # Indicates which signal is green currently
nextGreen = (currentGreen + 1) % noOfSignals  # Indicates which signal will turn green next
currentYellow = 0  # Indicates whether yellow signal is on or off

speeds = {'car': 2.25, 'bus': 1.8, 'truck': 1.8, 'bike': 2.6}  # average speeds of vehicles
speedsp = {'person1': 0.5, 'person2': 0.4, 'person3': 0.4, 'person4': 0.6}

# Coordinates of vehicles' start
x = {'right': [0, 0, 0], 'down': [615, 635, 576], 'left': [1400, 1400, 1400], 'up': [790, 750, 709]}
y = {'right': [446, 517, 476], 'down': [0, 0, 0], 'left': [323, 358, 399], 'up': [800, 800, 800]}

# Coordinates of pedestrians' start
a = {'right': [0, 0, 0], 'down': [890, 830, 809], 'left': [1400, 1400, 1400], 'up': [485, 500, 526]}  # -15 -30
b = {'right': [223, 258, 269], 'down': [0, 0, 0], 'left': [546, 567, 586], 'up': [800, 800, 800]}  # 25 41

vehicles = {'right': {0: [], 1: [], 2: [], 'crossed': 0}, 'down': {0: [], 1: [], 2: [], 'crossed': 0},
            'left': {0: [], 1: [], 2: [], 'crossed': 0}, 'up': {0: [], 1: [], 2: [], 'crossed': 0}}
vehicleTypes = {0: 'car', 1: 'bus', 2: 'truck', 3: 'bike'}

pedestrians = {'right': {0: [], 1: [], 2: [], 'crossed': 0}, 'down': {0: [], 1: [], 2: [], 'crossed': 0},
               'left': {0: [], 1: [], 2: [], 'crossed': 0}, 'up': {0: [], 1: [], 2: [], 'crossed': 0}}
pedestrianTypes = {0: 'person1', 1: 'person2', 2: 'person3', 3: 'person4'}

directionNumbers = {0: 'right', 1: 'down', 2: 'left', 3: 'up'}

# Coordinates of signal image, timer, and vehicle count ( up, right, left, down)(x,y)
signalCoods = [(515, 550), (490, 200), (845, 180), (850, 570)]
signalTimerCoods = [(515, 530), (490, 190), (845, 165), (830, 560)]

# Coordinates of signal image, timer, and vehicle count for pedestrian light
psignalCoods = [(495, 550), (470, 200), (820, 200), (895, 550)]
psignalTimerCoods = [(495, 510), (470, 180), (820, 160), (910, 540)]

# Coordinates of stop lines for vehicles
stopLines = {'right': 450, 'down': 230, 'left': 900, 'up': 635}
defaultStop = {'right': 440, 'down': 220, 'left': 910, 'up': 650}
# stops = {'right': [580,580,580], 'down': [320,320,320], 'left': [810,810,810], 'up': [545,545,545]}

# Coordinates of stop lines for pedestrians
stopLinesP = {'right': 560, 'down': 340, 'left': 810, 'up': 575}
defaultStop2 = {'right': 550, 'down': 330, 'left': 820, 'up': 590}

# Gap between vehicles
stoppingGap = 20  # stopping gap
movingGap = 20  # moving gap

# variables for turning
allowedVehicleTypes = {'car': True, 'bus': True, 'truck': True, 'bike': True}
allowedVehicleTypesList = []
vehiclesTurned = {'right': {1: [], 2: []}, 'down': {1: [], 2: []}, 'left': {1: [], 2: []}, 'up': {1: [], 2: []}}
vehiclesNotTurned = {'right': {1: [], 2: []}, 'down': {1: [], 2: []}, 'left': {1: [], 2: []}, 'up': {1: [], 2: []}}
rotationAngle = 3
mid = {'right': {'x': 705, 'y': 445}, 'down': {'x': 695, 'y': 450}, 'left': {'x': 695, 'y': 425},
       'up': {'x': 695, 'y': 400}}
randomGreenSignalTimer = True
randomGreenSignalTimerRange = [10, 20]

pygame.init()
simulation = pygame.sprite.Group()


class TrafficSignal:
    def __init__(self, red, yellow, green):
        self.red = red
        self.yellow = yellow
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
        self.x = -100
        self.y = -100

        self.crossed = 0
        pedestrians[direction][lane].append(self)
        self.indea = len(pedestrians[direction][lane]) - 1
        path = "images/" + "Pdirection/" + direction + "/" + pedestrianClass + ".png"
        self.image = pygame.image.load(path).convert_alpha()

        if len(pedestrians[direction][lane]) > 1 and pedestrians[direction][lane][
            self.indea - 1].crossed == 0:  # if more than 1 pedestrian in the lane of pedestrian before it has crossed stop line
            if direction == 'right':
                self.stop = pedestrians[direction][lane][self.indea - 1].stop - pedestrians[direction][lane][
                    self.indea - 1].image.get_rect().width - stoppingGap  # setting stop coordinate as: stop coordinate
                # of next pedestrian - width of next pedestrian - gap
            elif direction == 'left':
                self.stop = pedestrians[direction][lane][self.indea - 1].stop + pedestrians[direction][lane][
                    self.indea - 1].image.get_rect().width + stoppingGap
            elif direction == 'down':
                self.stop = pedestrians[direction][lane][self.indea - 1].stop - pedestrians[direction][lane][
                    self.indea - 1].image.get_rect().height - stoppingGap
            elif direction == 'up':
                self.stop = pedestrians[direction][lane][self.indea - 1].stop + pedestrians[direction][lane][
                    self.indea - 1].image.get_rect().height + stoppingGap
        else:
            self.stop = defaultStop2[direction]

        # Set new starting and stopping coordinate
        if direction == 'right':
            temp = self.image.get_rect().width + stoppingGap
            a[direction][lane] -= temp
        elif direction == 'left':
            temp = self.image.get_rect().width + stoppingGap
            a[direction][lane] += temp
        elif direction == 'down':
            temp = self.image.get_rect().height + stoppingGap
            b[direction][lane] -= temp
        elif direction == 'up':
            temp = self.image.get_rect().height + stoppingGap
            b[direction][lane] += temp
        simulation.add(self)

    def render(self, screen):
        screen.blit(self.image, (self.a, self.b))

    def move(self):
        if self.direction == 'right':
            if self.crossed == 0 and self.a + self.image.get_rect().width > stopLinesP[self.direction]:  # if the
                # image has crossed stop line now
                self.crossed = 1
            if ((self.a + self.image.get_rect().width <= self.stop or self.crossed == 1 or (currentGreen == 0)) and (
                    self.indea == 0 or self.a + self.image.get_rect().width < (
                    pedestrians[self.direction][self.lane][self.indea - 1].a - movingGap))):
                # (if the image has not reached its stop coordinate or has crossed stop line or has green signal) and
                # (it is either the first pedestrian in that lane or it is has enough gap to the next pedestrian in
                # that lane)
                self.a += self.speed  # move the pedestrian
        elif self.direction == 'down':
            if self.crossed == 0 and self.b + self.image.get_rect().height > stopLinesP[self.direction]:
                self.crossed = 1
            if ((self.b + self.image.get_rect().height <= self.stop or self.crossed == 1 or (currentGreen == 1)) and (
                    self.indea == 0 or self.b + self.image.get_rect().height < (
                    pedestrians[self.direction][self.lane][self.indea - 1].b - movingGap))):
                self.b += self.speed
        elif self.direction == 'left':
            if self.crossed == 0 and self.a < stopLinesP[self.direction]:
                self.crossed = 1
            if ((self.a >= self.stop or self.crossed == 1 or (currentGreen == 2)) and (self.indea == 0 or self.a > (
                    pedestrians[self.direction][self.lane][self.indea - 1].a +
                    pedestrians[self.direction][self.lane][self.indea - 1].image.get_rect().width + movingGap))):
                self.a -= self.speed
        elif self.direction == 'up':
            if self.crossed == 0 and self.b < stopLinesP[self.direction]:
                self.crossed = 1
            if ((self.b >= self.stop or self.crossed == 1 or (currentGreen == 3)) and (self.indea == 0 or self.b > (
                    pedestrians[self.direction][self.lane][self.indea - 1].b +
                    pedestrians[self.direction][self.lane][self.indea - 1].image.get_rect().height + movingGap))):
                self.b -= self.speed


class Vehicle(pygame.sprite.Sprite):
    def __init__(self, lane, vehicleClass, direction_number, direction, will_turn):
        pygame.sprite.Sprite.__init__(self)
        self.lane = lane
        self.vehicleClass = vehicleClass
        self.speed = speeds[vehicleClass]
        self.direction_number = direction_number
        self.direction = direction
        self.x = x[direction][lane]
        self.y = y[direction][lane]
        self.a = -45
        self.b = -45

        self.crossed = 0
        self.willTurn = will_turn
        self.turned = 0
        self.rotateAngle = 0
        vehicles[direction][lane].append(self)
        self.index = len(vehicles[direction][lane]) - 1
        self.crossedIndex = 0
        path = "images/" + direction + "/" + vehicleClass + ".png"
        self.originalImage = pygame.image.load(path).convert_alpha()
        self.image = pygame.image.load(path).convert_alpha()

        if (len(vehicles[direction][lane]) > 1 and vehicles[direction][lane][
            self.index - 1].crossed == 0):  # if more than 1 vehicle in the lane of vehicle before it has crossed
            # stop line
            if direction == 'right':
                self.stop = vehicles[direction][lane][self.index - 1].stop - vehicles[direction][lane][
                    self.index - 1].image.get_rect().width - stoppingGap  # setting stop coordinate as: stop
                # coordinate of next vehicle - width of next vehicle - gap
            elif direction == 'left':
                self.stop = vehicles[direction][lane][self.index - 1].stop + vehicles[direction][lane][
                    self.index - 1].image.get_rect().width + stoppingGap
            elif direction == 'down':
                self.stop = vehicles[direction][lane][self.index - 1].stop - vehicles[direction][lane][
                    self.index - 1].image.get_rect().height - stoppingGap
            elif direction == 'up':
                self.stop = vehicles[direction][lane][self.index - 1].stop + vehicles[direction][lane][
                    self.index - 1].image.get_rect().height + stoppingGap
        else:
            self.stop = defaultStop[direction]

        # Set new starting and stopping coordinate
        if direction == 'right':
            temp = self.image.get_rect().width + stoppingGap
            x[direction][lane] -= temp
        elif direction == 'left':
            temp = self.image.get_rect().width + stoppingGap
            x[direction][lane] += temp
        elif direction == 'down':
            temp = self.image.get_rect().height + stoppingGap
            y[direction][lane] -= temp
        elif direction == 'up':
            temp = self.image.get_rect().height + stoppingGap
            y[direction][lane] += temp
        simulation.add(self)

    def render(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def move(self):
        if self.direction == 'right':
            if self.crossed == 0 and self.x + self.image.get_rect().width > stopLines[self.direction]:
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
                if self.willTurn == 0:
                    vehiclesNotTurned[self.direction][self.lane].append(self)
                    self.crossedIndex = len(vehiclesNotTurned[self.direction][self.lane]) - 1
            if self.willTurn == 1:
                if self.lane == 2:
                    if self.crossed == 0 or self.x + self.image.get_rect().width < mid[self.direction]['x'] + 10:
                        if ((self.x + self.image.get_rect().width <= self.stop or (
                                currentGreen == 0 and currentYellow == 0) or self.crossed == 1) and (
                                self.index == 0 or self.x + self.image.get_rect().width < (
                                vehicles[self.direction][self.lane][self.index - 1].x - movingGap) or
                                vehicles[self.direction][self.lane][self.index - 1].turned == 1)):
                            self.x += self.speed
                    else:
                        if self.turned == 0:
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(self.originalImage, self.rotateAngle)
                            self.x += 2.4
                            self.y -= 2.8
                            if self.rotateAngle == 90:
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                        else:
                            if (self.crossedIndex == 0 or (self.y > (
                                    vehiclesTurned[self.direction][self.lane][self.crossedIndex - 1].y +
                                    vehiclesTurned[self.direction][self.lane][
                                        self.crossedIndex - 1].image.get_rect().height + movingGap))):
                                self.y -= self.speed
                elif self.lane == 1:
                    if self.crossed == 0 or self.x + self.image.get_rect().width < stopLines[self.direction] + 150:

                        if ((self.x + self.image.get_rect().width <= self.stop or (
                                currentGreen == 0 and currentYellow == 0) or self.crossed == 1) and (
                                self.index == 0 or self.x + self.image.get_rect().width < (
                                vehicles[self.direction][self.lane][self.index - 1].x - movingGap) or
                                vehicles[self.direction][self.lane][self.index - 1].turned == 1)):
                            self.x += self.speed
                    else:
                        if self.turned == 0:
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(self.originalImage, -self.rotateAngle)
                            self.x += 2
                            self.y += 1.8
                            if self.rotateAngle == 90:
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                        else:
                            if (self.crossedIndex == 0 or ((self.y + self.image.get_rect().height) < (
                                    vehiclesTurned[self.direction][self.lane][self.crossedIndex - 1].y - movingGap))):
                                self.y += self.speed
            else:
                if self.crossed == 0:
                    if ((self.x + self.image.get_rect().width <= self.stop or (
                            currentGreen == 0 and currentYellow == 0)) and (
                            self.index == 0 or self.x + self.image.get_rect().width < (
                            vehicles[self.direction][self.lane][self.index - 1].x - movingGap))):
                        self.x += self.speed
                else:
                    if ((self.crossedIndex == 0) or (self.x + self.image.get_rect().width < (
                            vehiclesNotTurned[self.direction][self.lane][self.crossedIndex - 1].x - movingGap))):
                        self.x += self.speed
        elif self.direction == 'down':
            if self.crossed == 0 and self.y + self.image.get_rect().height > stopLines[self.direction]:
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
                if self.willTurn == 0:
                    vehiclesNotTurned[self.direction][self.lane].append(self)
                    self.crossedIndex = len(vehiclesNotTurned[self.direction][self.lane]) - 1
            if self.willTurn == 1:
                if self.lane == 1:
                    if self.crossed == 0 or self.y + self.image.get_rect().height < mid[self.direction]['y'] + 50:
                        if ((self.y + self.image.get_rect().height <= self.stop or (
                                currentGreen == 1 and currentYellow == 0) or self.crossed == 1) and (
                                self.index == 0 or self.y + self.image.get_rect().height < (
                                vehicles[self.direction][self.lane][self.index - 1].y - movingGap) or
                                vehicles[self.direction][self.lane][self.index - 1].turned == 1)):
                            self.y += self.speed
                    else:
                        if self.turned == 0:
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(self.originalImage, self.rotateAngle)
                            self.x += 1.2
                            self.y += 1.8
                            if self.rotateAngle == 90:
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                        else:
                            if (self.crossedIndex == 0 or ((self.x + self.image.get_rect().width) < (
                                    vehiclesTurned[self.direction][self.lane][self.crossedIndex - 1].x - movingGap))):
                                self.x += self.speed
                elif self.lane == 2:
                    if self.crossed == 0 or self.y + self.image.get_rect().height < stopLines[self.direction] + 150:
                        if ((self.y + self.image.get_rect().height <= self.stop or (
                                currentGreen == 1 and currentYellow == 0) or self.crossed == 1) and (
                                self.index == 0 or self.y + self.image.get_rect().height < (
                                vehicles[self.direction][self.lane][self.index - 1].y - movingGap) or
                                vehicles[self.direction][self.lane][self.index - 1].turned == 1)):
                            self.y += self.speed
                    else:
                        if self.turned == 0:
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(self.originalImage, -self.rotateAngle)
                            self.x -= 2.5
                            self.y += 2
                            if self.rotateAngle == 90:
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                        else:
                            if (self.crossedIndex == 0 or (self.x > (
                                    vehiclesTurned[self.direction][self.lane][self.crossedIndex - 1].x +
                                    vehiclesTurned[self.direction][self.lane][
                                        self.crossedIndex - 1].image.get_rect().width + movingGap))):
                                self.x -= self.speed
            else:
                if self.crossed == 0:
                    if ((self.y + self.image.get_rect().height <= self.stop or (
                            currentGreen == 1 and currentYellow == 0)) and (
                            self.index == 0 or self.y + self.image.get_rect().height < (
                            vehicles[self.direction][self.lane][self.index - 1].y - movingGap))):
                        self.y += self.speed
                else:
                    if ((self.crossedIndex == 0) or (self.y + self.image.get_rect().height < (
                            vehiclesNotTurned[self.direction][self.lane][self.crossedIndex - 1].y - movingGap))):
                        self.y += self.speed
        elif self.direction == 'left':
            if self.crossed == 0 and self.x < stopLines[self.direction]:
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
                if self.willTurn == 0:
                    vehiclesNotTurned[self.direction][self.lane].append(self)
                    self.crossedIndex = len(vehiclesNotTurned[self.direction][self.lane]) - 1
            if self.willTurn == 1:
                if self.lane == 2:
                    # if self.crossed == 0 or self.x > stopLines[self.direction] - 70:
                    if self.crossed == 0 or self.x > mid[self.direction]['x'] - 40:
                        if ((self.x >= self.stop or (
                                currentGreen == 2 and currentYellow == 0) or self.crossed == 1) and (
                                self.index == 0 or self.x > (vehicles[self.direction][self.lane][self.index - 1].x +
                                                             vehicles[self.direction][self.lane][
                                                                 self.index - 1].image.get_rect().width + movingGap) or
                                vehicles[self.direction][self.lane][self.index - 1].turned == 1)):
                            self.x -= self.speed
                    else:
                        if self.turned == 0:
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(self.originalImage, self.rotateAngle)
                            self.x -= 1
                            self.y += 1.2
                            if self.rotateAngle == 90:
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                        else:
                            if (self.crossedIndex == 0 or ((self.y + self.image.get_rect().height) < (
                                    vehiclesTurned[self.direction][self.lane][self.crossedIndex - 1].y - movingGap))):
                                self.y += self.speed
                elif self.lane == 1:
                    if self.crossed == 0 or self.x > stopLines[self.direction] - 130:
                        if ((self.x >= self.stop or (
                                currentGreen == 2 and currentYellow == 0) or self.crossed == 1) and (
                                self.index == 0 or self.x > (vehicles[self.direction][self.lane][self.index - 1].x +
                                                             vehicles[self.direction][self.lane][
                                                                 self.index - 1].image.get_rect().width + movingGap) or
                                vehicles[self.direction][self.lane][self.index - 1].turned == 1)):
                            self.x -= self.speed
                    else:
                        if self.turned == 0:
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(self.originalImage, -self.rotateAngle)
                            self.x -= 1.8
                            self.y -= 2.5
                            if self.rotateAngle == 90:
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                        else:
                            if (self.crossedIndex == 0 or (self.y > (
                                    vehiclesTurned[self.direction][self.lane][self.crossedIndex - 1].y +
                                    vehiclesTurned[self.direction][self.lane][
                                        self.crossedIndex - 1].image.get_rect().height + movingGap))):
                                self.y -= self.speed
            else:
                if self.crossed == 0:
                    if ((self.x >= self.stop or (currentGreen == 2 and currentYellow == 0)) and (
                            self.index == 0 or self.x > (
                            vehicles[self.direction][self.lane][self.index - 1].x +
                            vehicles[self.direction][self.lane][self.index - 1].image.get_rect().width + movingGap))):
                        self.x -= self.speed
                else:
                    if ((self.crossedIndex == 0) or (self.x > (
                            vehiclesNotTurned[self.direction][self.lane][self.crossedIndex - 1].x +
                            vehiclesNotTurned[self.direction][self.lane][
                                self.crossedIndex - 1].image.get_rect().width + movingGap))):
                        self.x -= self.speed
        elif self.direction == 'up':
            if self.crossed == 0 and self.y < stopLines[self.direction]:
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
                if self.willTurn == 0:
                    vehiclesNotTurned[self.direction][self.lane].append(self)
                    self.crossedIndex = len(vehiclesNotTurned[self.direction][self.lane]) - 1
            if self.willTurn == 1:
                if self.lane == 2:
                    # if self.crossed == 0 or self.y > stopLines[self.direction] - 60:
                    if self.crossed == 0 or self.y > mid[self.direction]['y'] - 20:
                        if ((self.y >= self.stop or (
                                currentGreen == 3 and currentYellow == 0) or self.crossed == 1) and (
                                self.index == 0 or self.y > (vehicles[self.direction][self.lane][self.index - 1].y +
                                                             vehicles[self.direction][self.lane][
                                                                 self.index - 1].image.get_rect().height + movingGap) or
                                vehicles[self.direction][self.lane][self.index - 1].turned == 1)):
                            self.y -= self.speed
                    else:
                        if self.turned == 0:
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(self.originalImage, self.rotateAngle)
                            self.x -= 2
                            self.y -= 1.2
                            if self.rotateAngle == 90:
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                        else:
                            if (self.crossedIndex == 0 or (self.x > (
                                    vehiclesTurned[self.direction][self.lane][self.crossedIndex - 1].x +
                                    vehiclesTurned[self.direction][self.lane][
                                        self.crossedIndex - 1].image.get_rect().width + movingGap))):
                                self.x -= self.speed
                elif self.lane == 1:
                    # if self.crossed == 0 or self.y > mid[self.direction]['y']:
                    if self.crossed == 0 or self.y > stopLines[self.direction] - 100:
                        if ((self.y >= self.stop or (
                                currentGreen == 3 and currentYellow == 0) or self.crossed == 1) and (
                                self.index == 0 or self.y > (vehicles[self.direction][self.lane][self.index - 1].y +
                                                             vehicles[self.direction][self.lane][
                                                                 self.index - 1].image.get_rect().height + movingGap) or
                                vehicles[self.direction][self.lane][self.index - 1].turned == 1)):
                            self.y -= self.speed
                    else:
                        if self.turned == 0:
                            self.rotateAngle += rotationAngle
                            self.image = pygame.transform.rotate(self.originalImage, -self.rotateAngle)
                            self.x += 1
                            self.y -= 1
                            if self.rotateAngle == 90:
                                self.turned = 1
                                vehiclesTurned[self.direction][self.lane].append(self)
                                self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                        else:
                            if (self.crossedIndex == 0 or (self.x < (
                                    vehiclesTurned[self.direction][self.lane][self.crossedIndex - 1].x -
                                    vehiclesTurned[self.direction][self.lane][
                                        self.crossedIndex - 1].image.get_rect().width - movingGap))):
                                self.x += self.speed
            else:
                if self.crossed == 0:
                    if ((self.y >= self.stop or (currentGreen == 3 and currentYellow == 0)) and (
                            self.index == 0 or self.y > (
                            vehicles[self.direction][self.lane][self.index - 1].y +
                            vehicles[self.direction][self.lane][self.index - 1].image.get_rect().height + movingGap))):
                        self.y -= self.speed
                else:
                    if ((self.crossedIndex == 0) or (self.y > (
                            vehiclesNotTurned[self.direction][self.lane][self.crossedIndex - 1].y +
                            vehiclesNotTurned[self.direction][self.lane][
                                self.crossedIndex - 1].image.get_rect().height + movingGap))):
                        self.y -= self.speed

                    # Initialization of signals with default values


def initialize():
    minTime = randomGreenSignalTimerRange[0]
    maxTime = randomGreenSignalTimerRange[1]
    if randomGreenSignalTimer:
        ts1 = TrafficSignal(0, defaultYellow, random.randint(minTime, maxTime))
        signals.append(ts1)
        ts2 = TrafficSignal(ts1.yellow + ts1.green, defaultYellow, random.randint(minTime, maxTime))
        signals.append(ts2)
        ts3 = TrafficSignal(defaultRed, defaultYellow, random.randint(minTime, maxTime))
        signals.append(ts3)
        ts4 = TrafficSignal(defaultRed, defaultYellow, random.randint(minTime, maxTime))
        signals.append(ts4)
    else:
        ts1 = TrafficSignal(0, defaultYellow, defaultGreen[0])
        signals.append(ts1)
        ts2 = TrafficSignal(ts1.yellow + ts1.green, defaultYellow, defaultGreen[1])
        signals.append(ts2)
        ts3 = TrafficSignal(defaultRed, defaultYellow, defaultGreen[2])
        signals.append(ts3)
        ts4 = TrafficSignal(defaultRed, defaultYellow, defaultGreen[3])
        signals.append(ts4)
    repeat()


def repeat():
    global currentGreen, currentYellow, nextGreen
    while signals[currentGreen].green > 0:
        updateValues()
        time.sleep(1)
    currentYellow = 1
    for i in range(0, 3):
        for vehicle in vehicles[directionNumbers[currentGreen]][i]:
            vehicle.stop = defaultStop[directionNumbers[currentGreen]]
        for pedestrian in pedestrians[directionNumbers[currentGreen]][i]:
            pedestrian.stop = defaultStop2[directionNumbers[currentGreen]]
    while signals[currentGreen].yellow > 0:
        updateValues()
        time.sleep(1)
    currentYellow = 0
    minTime = randomGreenSignalTimerRange[0]
    maxTime = randomGreenSignalTimerRange[1]
    if randomGreenSignalTimer:
        signals[currentGreen].green = random.randint(minTime, maxTime)
    else:
        signals[currentGreen].green = defaultGreen[currentGreen]
    signals[currentGreen].yellow = defaultYellow
    signals[currentGreen].red = defaultRed
    currentGreen = nextGreen
    nextGreen = (currentGreen + 1) % noOfSignals
    signals[nextGreen].red = signals[currentGreen].yellow + signals[currentGreen].green
    repeat()


# Update values of the signal timers after every second
def updateValues():
    for i in range(0, noOfSignals):
        if i == currentGreen:
            if currentYellow == 0:
                signals[i].green -= 1
            else:
                signals[i].yellow -= 1
        else:
            signals[i].red -= 1


# Generating vehicles in the simulation
def generateVehicles():
    while True:
        vehicle_type = random.choice(allowedVehicleTypesList)
        lane_number = random.randint(1, 2)
        will_turn = 0
        if lane_number == 1:
            temp = random.randint(0, 99)
            if temp < 40:
                will_turn = 1
        elif lane_number == 2:
            temp = random.randint(0, 99)
            if temp < 40:
                will_turn = 1
        temp = random.randint(0, 99)
        direction_number = 0
        dist = [25, 50, 75, 100]
        if temp < dist[0]:
            direction_number = 0
        elif temp < dist[1]:
            direction_number = 1
        elif temp < dist[2]:
            direction_number = 2
        elif temp < dist[3]:
            direction_number = 3
        Vehicle(lane_number, vehicleTypes[vehicle_type], direction_number, directionNumbers[direction_number],
                will_turn)
        time.sleep(1)


# Generating pedestrians in the simulation
def generatepedestrians():
    while (True):
        pedestrian_Type = random.randint(0, 3)
        lane_number = random.randint(1, 2)
        temp = random.randint(0, 99)
        direction_number = 0
        dist = [10, 20, 30, 100]
        if temp < dist[0]:
            direction_number = 0
        elif temp < dist[1]:
            direction_number = 1
        elif temp < dist[2]:
            direction_number = 2
        elif temp < dist[3]:
            direction_number = 3
        Pedestrian(lane_number, pedestrianTypes[pedestrian_Type], direction_number, directionNumbers[direction_number])
        time.sleep(1)


def Viocount():
    global violations, positionPx, positionVx, positionPw, positionVy, positionPy, positionPh, positionVw, positionVh
    for pedestrian in simulation:
        for vehicle in simulation:
            pedestrian_rect = pedestrian.image.get_rect()
            vehicle_rect = vehicle.image.get_rect()
            positionPw = pedestrian_rect.width
            positionPx = pedestrian_rect.x
            positionPh = pedestrian_rect.height
            positionPy = pedestrian_rect.y
            positionVw = vehicle_rect.width
            positionVx = vehicle_rect.x
            positionVh = vehicle_rect.height
            positionVy = vehicle_rect.y
            #
            # col = pygame.sprite.collide_rect(pedestrian, vehicle)
            col = pedestrian_rect.colliderect(vehicle_rect)
            print(col)
            if col == True:
                violations += 1


        #
        # def collision():
        #     global violations
        #     if positionPx <= positionVx <= positionPx + positionPw:
        #         if positionPy <= positionVy <= positionPy + positionPh:
        #             violations += 1
        #             print(positionPy, positionPx, positionPh)
        #             print(violations, '1')
        #             return True
        #     if positionPx <= positionVx + positionVw <= positionVx + positionPw:
        #         if positionPy <= positionVy <= positionPy + positionPh:
        #             violations += 1
        #             print(violations, '2')
        #             return True
        #     if positionPx <= positionVx <= positionPx + positionPw:
        #         if positionPy <= positionVy + positionVh <= positionPy + positionPh:
        #             violations += 1
        #             print(violations, '3')
        #             return True
        #     if positionPx <= positionVx + positionVw <= positionPx + positionPw:
        #         if positionPy <= positionVy + positionVh <= positionPy + positionPh:
        #             violations += 1
        #             print(violations, '4')
        #             return True
        #     if positionVx <= positionPx <= positionVx + positionVw:
        #         if positionVy <= positionPy <= positionVy + positionVh:
        #             violations += 1
        #             print(violations, '5')
        #             return True
        #     if positionVx <= positionPx + positionPw <= positionVx + positionVw:
        #         if positionVy <= positionPy <= positionVy + positionVh:
        #             violations += 1
        #             print(violations, '6')
        #             return True
        #     if positionVx <= positionPx <= positionVx + positionVw:
        #         if positionVy <= positionPy + positionPh <= positionVy + positionVh:
        #             violations += 1
        #             print(violations, '7')
        #             return True
        #     if positionVx <= positionPx + positionPw <= positionVx + positionVw:
        #         if positionVy <= positionPy + positionPh <= positionVy + positionVh:
        #             violations += 1
        #             print(violations, '8')
        #             return True

        # collision()

def checkCollision(self, sprite1, sprite2):
    col = pygame.sprite.collide_rect(sprite1, sprite2)
    if col == True:
        sys.exit()

def simTime():
    global timeElapsed, simulationTime
    while (True):
        timeElapsed += 1
        time.sleep(1)
        if timeElapsed == simulationTime:
            sys.exit(1)


class Main:
    global allowedVehicleTypesList
    i = 0
    for vehicleType in allowedVehicleTypes:
        if allowedVehicleTypes[vehicleType]:
            allowedVehicleTypesList.append(i)
        i += 1
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
    redSignal = pygame.image.load('images/signals/red.png')
    yellowSignal = pygame.image.load('images/signals/yellow.png')
    greenSignal = pygame.image.load('images/signals/green.png')
    predSignal = pygame.image.load('images/signals/redh.png')
    pgreenSignal = pygame.image.load('images/signals/greenh.png')
    font = pygame.font.Font(None, 30)

    thread2 = threading.Thread(name="generateVehicles", target=generateVehicles, args=())  # Generating vehicles
    thread2.daemon = True
    thread2.start()

    thread3 = threading.Thread(name="generatepedestrians", target=generatepedestrians,
                               args=())  # Generating pedestrians
    thread3.daemon = True
    thread3.start()

    thread4 = threading.Thread(name="simTime", target=simTime, args=())
    thread4.daemon = True
    thread4.start()

    thread5 = threading.Thread(name="VioCount", target=Viocount, args=())
    thread5.daemon = True
    thread5.start()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        screen.blit(background, (-260, -50))  # display background in simulation
        for i in range(0,
                       noOfSignals):  # display signal and set timer according to current status: green, yello, or red
            if i == currentGreen:
                if currentYellow == 1:
                    signals[i].signalText = signals[i].yellow
                    screen.blit(yellowSignal, signalCoods[i])
                    screen.blit(predSignal, psignalCoods[i])

                else:
                    signals[i].signalText = signals[i].green
                    screen.blit(greenSignal, signalCoods[i])
                    screen.blit(predSignal, psignalCoods[i])


            else:
                if signals[i].red <= 10:
                    signals[i].signalText = signals[i].red
                    # signals[i].signalText = signals[i].redp
                    screen.blit(pgreenSignal, psignalCoods[i])

                else:
                    signals[i].signalText = "---"
                screen.blit(redSignal, signalCoods[i])
                screen.blit(pgreenSignal, psignalCoods[i])

        signalTexts = ["", "", "", ""]

        # display signal timer
        for i in range(0, noOfSignals):
            signalTexts[i] = font.render(str(signals[i].signalText), True, white, black)
            screen.blit(signalTexts[i], signalTimerCoods[i])

        # display time elapsed
        timeElapsedText = font.render(("Time Elapsed: " + str(timeElapsed)), True, black, white)
        screen.blit(timeElapsedText, timeElapsedCoods)

        # display time elapsed
        ViolationsText = font.render(("Number of violations: " + str(violations)), True, black, white)
        screen.blit(ViolationsText, violationsCoods)

        # display the pedestrians
        for pedestrian in simulation:
            screen.blit(pedestrian.image, [pedestrian.a, pedestrian.b])
            pedestrian.move()

        # display the vehicles
        for vehicle in simulation:
            screen.blit(vehicle.image, [vehicle.x, vehicle.y])
            vehicle.move()

        pygame.display.update()


Main()
