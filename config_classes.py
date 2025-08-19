from dataclasses import dataclass
from enum import Enum
from typing import Dict

class Direction(Enum):
    """Traffic direction enumeration"""
    RIGHT = 0
    DOWN = 1
    LEFT = 2
    UP = 3


class VehicleType(Enum):
    """Vehicle type enumeration"""
    CAR = 'car'
    BUS = 'bus'
    TRUCK = 'truck' 
    BIKE = 'bike'


class PedestrianType(Enum):
    """Pedestrian type enumeration"""
    PERSON1 = 'person1'
    PERSON2 = 'person2'
    PERSON3 = 'person3'
    PERSON4 = 'person4'


@dataclass
class Config:
    """Configuration class for simulation parameters"""
    # Screen settings
    SCREEN_WIDTH: int = 1400
    SCREEN_HEIGHT: int = 800
    
    # Signal timings
    DEFAULT_GREEN_TIME: int = 10
    DEFAULT_YELLOW_TIME: int = 5
    DEFAULT_RED_TIME: int = 150
    
    # Speed settings (pixels per frame)
    VEHICLE_SPEEDS: Dict[str, float] = None
    PEDESTRIAN_SPEEDS: Dict[str, float] = None
    
    # Gaps
    STOPPING_GAP: int = 20
    MOVING_GAP: int = 20
    PEDESTRIAN_GAP: int = 7
    
    # AI Settings
    ADAPTIVE_SIGNALS: bool = True
    COLLISION_PREDICTION: bool = True
    EMERGENCY_RESPONSE: bool = True
    
    def __post_init__(self):
        if self.VEHICLE_SPEEDS is None:
            self.VEHICLE_SPEEDS = {
                'car': 2.25, 'bus': 1.8, 'truck': 1.8, 'bike': 2.6
            }
        if self.PEDESTRIAN_SPEEDS is None:
            self.PEDESTRIAN_SPEEDS = {
                'person1': 0.2, 'person2': 0.2, 'person3': 0.2, 'person4': 0.2
            }