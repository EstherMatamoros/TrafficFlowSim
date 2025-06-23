from typing import Dict, List, Tuple, Optional
from collections import defaultdict
import time
from config_classes import Config, Direction


class Analytics:
    """Real-time analytics and reporting system"""
    
    def __init__(self):
        self.reset_stats()
    
    def reset_stats(self):
        """Reset all statistics"""
        self.vehicles_spawned = 0
        self.vehicles_crossed = 0
        self.pedestrians_spawned = 0
        self.pedestrians_crossed = 0
        self.violations = 0
        self.near_misses = 0
        self.average_wait_time = 0
        self.traffic_density = defaultdict(int)
        self.collision_events = []
        self.signal_efficiency = {}
    
    def log_violation(self, violation_type: str, location: Tuple[int, int]):
        """Log a traffic violation"""
        self.violations += 1
        self.collision_events.append({
            'type': violation_type,
            'location': location,
            'timestamp': time.time()
        })
    
    def get_report(self) -> Dict:
        """Generate comprehensive analytics report"""
        return {
            'vehicles_spawned': self.vehicles_spawned,
            'vehicles_crossed': self.vehicles_crossed,
            'pedestrians_spawned': self.pedestrians_spawned,
            'pedestrians_crossed': self.pedestrians_crossed,
            'violations': self.violations,
            'near_misses': self.near_misses,
            'throughput_rate': self.vehicles_crossed / max(1, self.vehicles_spawned),
            'safety_score': max(0, 100 - (self.violations * 10 + self.near_misses * 5)),
            'collision_events': self.collision_events
        }


class AITrafficController:
    """AI-powered adaptive traffic light controller"""
    
    def __init__(self, config: Config):
        self.config = config
        self.traffic_density = defaultdict(int)
        self.wait_times = defaultdict(list)
        self.adaptive_enabled = config.ADAPTIVE_SIGNALS
    
    def analyze_traffic_flow(self, vehicles: Dict, pedestrians: Dict) -> Dict[Direction, int]:
        """Analyze current traffic density for each direction"""
        density = defaultdict(int)
        
        for direction, lanes in vehicles.items():
            if isinstance(direction, str):
                for lane_id, vehicle_list in lanes.items():
                    if isinstance(lane_id, int):
                        density[direction] += len(vehicle_list)
        
        return density
    
    def calculate_optimal_timing(self, density: Dict) -> Dict[Direction, int]:
        """Calculate optimal signal timing based on traffic density"""
        if not self.adaptive_enabled:
            return {Direction.RIGHT: self.config.DEFAULT_GREEN_TIME,
                   Direction.DOWN: self.config.DEFAULT_GREEN_TIME,
                   Direction.LEFT: self.config.DEFAULT_GREEN_TIME,
                   Direction.UP: self.config.DEFAULT_GREEN_TIME}
        
        total_density = max(1, sum(density.values()))
        optimal_times = {}
        
        for direction in Direction:
            dir_name = direction.name.lower()
            if dir_name == 'right':
                dir_key = 'right'
            elif dir_name == 'down':
                dir_key = 'down'
            elif dir_name == 'left':
                dir_key = 'left'
            else:
                dir_key = 'up'
            
            ratio = density.get(dir_key, 0) / total_density
            optimal_times[direction] = max(5, min(30, int(self.config.DEFAULT_GREEN_TIME * (1 + ratio))))
        
        return optimal_times
