import pygame
import time
import random
from config_classes import Config, VehicleType, Direction
from typing import Dict, List, Tuple, Optional


class Vehicle(pygame.sprite.Sprite):
    """Enhanced vehicle class with improved AI features"""
    
    def __init__(self, lane: int, vehicle_type: VehicleType, direction: Direction, 
                 will_turn: bool, config: Config):
        pygame.sprite.Sprite.__init__(self)
        self.lane = lane
        self.vehicle_type = vehicle_type
        self.speed = config.VEHICLE_SPEEDS[vehicle_type.value]
        self.base_speed = self.speed
        self.direction = direction
        self.will_turn = will_turn
        self.turned = False
        self.crossed = False
        self.spawn_time = time.time()
        self.config = config
        
        # AI behavior parameters
        self.aggressive_factor = random.uniform(0.8, 1.2)
        self.reaction_time = random.uniform(0.5, 1.5)
        self.following_distance = config.STOPPING_GAP * random.uniform(0.8, 1.2)
        
        self._initialize_position()
        self._load_image()
    
    def _initialize_position(self):
        """Initialize vehicle position based on direction and lane"""
        # Simplified position initialization
        direction_positions = {
            Direction.RIGHT: {'x': [1, 0, 1], 'y': [446, 517, 476]},
            Direction.DOWN: {'x': [615, 635, 576], 'y': [1, 0, 1]},
            Direction.LEFT: {'x': [1400, 1400, 1400], 'y': [323, 358, 399]},
            Direction.UP: {'x': [790, 750, 709], 'y': [801, 803, 802]}
        }
        
        pos = direction_positions[self.direction]
        self.x = pos['x'][self.lane]
        self.y = pos['y'][self.lane]
    
    def _load_image(self):
        """Load vehicle image"""
        direction_map = {
            Direction.RIGHT: 'right',
            Direction.DOWN: 'down',
            Direction.LEFT: 'left',
            Direction.UP: 'up'
        }
        
        try:
            path = f"images/{direction_map[self.direction]}/{self.vehicle_type.value}.png"
            self.image = pygame.image.load(path)
            self.originalImage = self.image.copy()
        except pygame.error:
            # Fallback: create a colored rectangle
            self.image = pygame.Surface((30, 20))
            colors = {'car': (255, 0, 0), 'bus': (0, 255, 0), 'truck': (0, 0, 255), 'bike': (255, 255, 0)}
            self.image.fill(colors.get(self.vehicle_type.value, (128, 128, 128)))
            self.originalImage = self.image.copy()
    
    def update_ai_behavior(self, nearby_vehicles: List, traffic_density: float):
        """Update AI-driven behavior based on surrounding conditions"""
        # Adaptive speed based on traffic density
        density_factor = max(0.5, 1.0 - (traffic_density * 0.1))
        self.speed = self.base_speed * density_factor * self.aggressive_factor
        
        # Collision avoidance
        if nearby_vehicles:
            min_distance = min(self._calculate_distance(v) for v in nearby_vehicles)
            if min_distance < self.following_distance:
                self.speed *= 0.5  # Slow down
    
    def _calculate_distance(self, other_vehicle) -> float:
        """Calculate distance to another vehicle"""
        return ((self.x - other_vehicle.x) ** 2 + (self.y - other_vehicle.y) ** 2) ** 0.5
    
    def move(self, current_signal_state: Dict):
        """Enhanced movement with AI decision making"""
        # Simplified movement logic - can be expanded
        if self.direction == Direction.RIGHT:
            self.x += self.speed
        elif self.direction == Direction.LEFT:
            self.x -= self.speed
        elif self.direction == Direction.DOWN:
            self.y += self.speed
        elif self.direction == Direction.UP:
            self.y -= self.speed
        
        # Check if crossed intersection
        if not self.crossed:
            if ((self.direction == Direction.RIGHT and self.x > 700) or
                (self.direction == Direction.LEFT and self.x < 600) or
                (self.direction == Direction.DOWN and self.y > 500) or
                (self.direction == Direction.UP and self.y < 400)):
                self.crossed = True
        
        return self.x, self.y
