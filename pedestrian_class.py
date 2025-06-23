import pygame 
from config_classes import Config, Direction
from typing import Tuple

class Pedestrian:
    def __init__(self, direction: Direction, config: Config, pedestrian_type='person1'):
        self.direction = direction
        self.speed = config.PEDESTRIAN_SPEEDS.get(pedestrian_type, 0.2)
        self.image = pygame.image.load(f"images/Pdirection/p_{direction.name.lower()}/{pedestrian_type}.png")
        self.x, self.y = self._starting_position()
        self.crossed = False

    def _starting_position(self) -> Tuple[int, int]:
        if self.direction == Direction.UP:
            return (720, 820)
        elif self.direction == Direction.DOWN:
            return (680, -20)
        elif self.direction == Direction.LEFT:
            return (1440, 420)
        elif self.direction == Direction.RIGHT:
            return (-20, 460)

    def move(self, signal_state: str):
        if signal_state == 'Pgreen':
            if self.direction == Direction.UP:
                self.y -= self.speed
            elif self.direction == Direction.DOWN:
                self.y += self.speed
            elif self.direction == Direction.LEFT:
                self.x -= self.speed
            elif self.direction == Direction.RIGHT:
                self.x += self.speed

    def is_off_screen(self, width: int, height: int) -> bool:
        return self.x < -50 or self.x > width + 50 or self.y < -50 or self.y > height + 50
