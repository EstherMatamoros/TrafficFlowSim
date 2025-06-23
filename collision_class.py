from typing import Dict, List, Tuple, Optional
from config_classes import Config

class CollisionDetector:
    """Advanced collision detection and prevention system"""
    
    def __init__(self, config: Config):
        self.config = config
        self.collision_zones = self._define_collision_zones()
        self.prediction_enabled = config.COLLISION_PREDICTION
    
    def _define_collision_zones(self) -> List[Dict]:
        """Define critical collision zones in the intersection"""
        return [
            {'x_range': (600, 800), 'y_range': (400, 600), 'type': 'intersection_center'},
            {'x_range': (450, 550), 'y_range': (200, 300), 'type': 'pedestrian_crossing'},
            {'x_range': (850, 950), 'y_range': (500, 600), 'type': 'pedestrian_crossing'},
        ]
    
    def check_collision_risk(self, vehicles: List, pedestrians: List) -> List[Dict]:
        """Check for potential collisions and return risk assessments"""
        risks = []
        
        # Vehicle-Pedestrian collision detection
        for vehicle in vehicles:
            for pedestrian in pedestrians:
                risk = self._calculate_collision_risk(vehicle, pedestrian)
                if risk['level'] > 0:
                    risks.append(risk)
        
        return risks
    
    def _calculate_collision_risk(self, vehicle, pedestrian) -> Dict:
        """Calculate collision risk between vehicle and pedestrian"""
        # Simplified collision prediction algorithm
        v_future_x = vehicle.x + vehicle.speed * 10  # Predict 10 frames ahead
        v_future_y = vehicle.y + (vehicle.speed * 10 if vehicle.direction in ['down', 'up'] else 0)
        
        p_future_x = pedestrian.x + pedestrian.speed * 10
        p_future_y = pedestrian.y + (pedestrian.speed * 10 if pedestrian.direction in ['p_down', 'p_up'] else 0)
        
        distance = ((v_future_x - p_future_x) ** 2 + (v_future_y - p_future_y) ** 2) ** 0.5
        
        risk_level = 0
        if distance < 50:
            risk_level = 3  # High risk
        elif distance < 100:
            risk_level = 2  # Medium risk
        elif distance < 150:
            risk_level = 1  # Low risk
        
        return {
            'level': risk_level,
            'vehicle': vehicle,
            'pedestrian': pedestrian,
            'predicted_collision_point': (v_future_x, v_future_y),
            'time_to_collision': distance / max(vehicle.speed, 0.1)
        }
