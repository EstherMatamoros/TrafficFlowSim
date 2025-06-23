"""
Advanced Traffic Flow Simulation System
======================================

A comprehensive traffic simulation featuring:
- AI-driven adaptive traffic light control
- Real-time collision detection and prevention
- Statistical analysis and visualization
- Pedestrian safety modeling
- Performance optimization algorithms

Author: Esther Matamoros 
Created for: AI/ML and Software Development Portfolio
"""

import pygame
import random
import time
import threading
import sys
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from enum import Enum
import json
from collections import defaultdict
import numpy as np
from collision_class import CollisionDetector
from analytics import Analytics, AITrafficController
from vehicle_class import Vehicle
from traffic_lights_class import TrafficSignal
from pedestrian_class import Pedestrian
from config_classes import Config, Direction, VehicleType, PedestrianType

class TrafficSimulation:
    """Main simulation controller with enhanced features"""
    
    def __init__(self):
        self.config = Config()
        self.analytics = Analytics()
        self.ai_controller = AITrafficController(self.config)
        self.collision_detector = CollisionDetector(self.config)
        
        self.signal_images = {
            "green": pygame.image.load("signals/green.png"),
            "yellow": pygame.image.load("signals/yellow.png"),
            "red": pygame.image.load("signals/red.png"),
            "Pgreen": pygame.image.load("signals/Pgreen.png"),
            "Pred": pygame.image.load("signals/Pred.png")
        }

        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT))
        pygame.display.set_caption("Advanced Traffic Flow Simulation")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        
        # Simulation state
        self.running = True
        self.paused = False
        self.signals = []
        self.vehicles = []
        self.pedestrians = []
        self.current_green = 0
        
        self._initialize_signals()
        self._start_generators()
    
    def _initialize_signals(self):
        """Initialize traffic signals"""
        for i in range(4):
            signal = TrafficSignal(
                red=self.config.DEFAULT_RED_TIME,
                yellow=self.config.DEFAULT_YELLOW_TIME,
                green=self.config.DEFAULT_GREEN_TIME,
                signal_id=i
            )
            self.signals.append(signal)
    
    def _draw_signals(self):
        """Draw traffic signals on the screen"""
        signal_positions = [
            (500, 250),  # Signal 0
            (900, 250),  # Signal 1
            (500, 550),  # Signal 2
            (900, 550),  # Signal 3
        ]
        
        for i, signal in enumerate(self.signals):
            # Priority: emergency override > green > yellow > red
            if signal.emergency_override:
                color = "green"
            elif signal.green > 0:
                color = "green"
            elif signal.yellow > 0:
                color = "yellow"
            else:
                color = "red"
            
            position = signal_positions[i % len(signal_positions)]
            image = self.signal_images[color]
            self.screen.blit(image, position)

    def _start_generators(self):
        """Start vehicle and pedestrian generation threads"""
        vehicle_thread = threading.Thread(target=self._generate_vehicles, daemon=True)
        pedestrian_thread = threading.Thread(target=self._generate_pedestrians, daemon=True)
        
        vehicle_thread.start()
        pedestrian_thread.start()

    def _draw_signals(self):
        """Draw traffic and pedestrian signals"""
        signal_positions = [(500, 250), (900, 250), (500, 550), (900, 550)]

        for i, signal in enumerate(self.signals):
            color = signal.current_state if hasattr(signal, "current_state") else (
                "green" if signal.green > 0 else "yellow" if signal.yellow > 0 else "red"
            )
            self.screen.blit(self.signal_images[color], signal_positions[i])

        # Draw pedestrian signals
        ped_signal_state = self._get_pedestrian_signal_state()
        # These are arbitrary positions for demo
        self.screen.blit(self.signal_images[ped_signal_state['horizontal']], (660, 360))  # horizontal crossing
        self.screen.blit(self.signal_images[ped_signal_state['vertical']], (740, 360))    # vertical crossing


    
    def _generate_vehicles(self):
        """Generate vehicles at random intervals"""
        while self.running:
            if not self.paused and len(self.vehicles) < 50:  # Limit max vehicles
                vehicle_type = random.choice(list(VehicleType))
                direction = random.choice(list(Direction))
                lane = random.randint(0, 2)
                will_turn = random.random() < 0.3  # 30% chance to turn
                
                vehicle = Vehicle(lane, vehicle_type, direction, will_turn, self.config)
                self.vehicles.append(vehicle)
                self.analytics.vehicles_spawned += 1
            
            time.sleep(random.uniform(1, 3))
    
    def _generate_pedestrians(self):
        """Generate pedestrians at random intervals"""
        while self.running:
            if not self.paused and len(self.pedestrians) < 20:
                pedestrian_type = random.choice(list(PedestrianType)).value
                direction = random.choice(list(Direction))
                ped = Pedestrian(direction, self.config, pedestrian_type)
                self.pedestrians.append(ped)
                self.analytics.pedestrians_spawned += 1

            time.sleep(random.uniform(3, 6))

    
    def _update_ai_systems(self):
        """Update all AI systems"""
        # Update traffic controller
        vehicle_dict = {'right': {}, 'down': {}, 'left': {}, 'up': {}}
        density = self.ai_controller.analyze_traffic_flow(vehicle_dict, {})
        optimal_timings = self.ai_controller.calculate_optimal_timing(density)
        
        # Update collision detection
        risks = self.collision_detector.check_collision_risk(self.vehicles, self.pedestrians)
        
        # Handle high-risk situations
        for risk in risks:
            if risk['level'] >= 2:
                self.analytics.log_violation("Near Miss", risk['predicted_collision_point'])
    
    def _render_dashboard(self):
        """Render real-time analytics dashboard"""
        dashboard_y = 10
        stats = self.analytics.get_report()
        
        texts = [
            f"Vehicles: {stats['vehicles_spawned']} spawned, {stats['vehicles_crossed']} crossed",
            f"Safety Score: {stats['safety_score']:.1f}/100",
            f"Violations: {stats['violations']} | Near Misses: {stats['near_misses']}",
            f"Throughput: {stats['throughput_rate']:.2%}",
            f"FPS: {self.clock.get_fps():.1f}"
        ]
        
        for i, text in enumerate(texts):
            surface = self.font.render(text, True, (255, 255, 255))
            self.screen.blit(surface, (10, dashboard_y + i * 25))
    
    def run(self):
        """Main simulation loop"""
        while self.running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.paused = not self.paused
                    elif event.key == pygame.K_r:
                        self.analytics.reset_stats()
            
            if not self.paused:
                # Update AI systems
                self._update_ai_systems()
                
                # Update vehicles
                self.vehicles = [v for v in self.vehicles if self._update_vehicle(v)]
                
                # Update pedestrians
                # Update pedestrian movement
                ped_signal_state = self._get_pedestrian_signal_state()

                updated_pedestrians = []
                for ped in self.pedestrians:
                    # Map direction to pedestrian signal
                    if ped.direction in [Direction.UP, Direction.DOWN]:
                        ped_signal = ped_signal_state['vertical']
                    else:
                        ped_signal = ped_signal_state['horizontal']
                    
                    ped.move(ped_signal)

                    if not ped.is_off_screen(self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT):
                        updated_pedestrians.append(ped)
                    else:
                        self.analytics.pedestrians_crossed += 1

                self.pedestrians = updated_pedestrians
            # Update traffic signals
                
            
            # Render
            self.screen.fill((0, 0, 0))
            
            # Draw intersection background (simplified)
            pygame.draw.rect(self.screen, (128, 128, 128), (400, 300, 400, 200))
            pygame.draw.rect(self.screen, (64, 64, 64), (580, 0, 40, self.config.SCREEN_HEIGHT))
            pygame.draw.rect(self.screen, (64, 64, 64), (0, 380, self.config.SCREEN_WIDTH, 40))
            
            # Draw vehicles
            for vehicle in self.vehicles:
                self.screen.blit(vehicle.image, (int(vehicle.x), int(vehicle.y)))
            
            # Draw pedestrians
            for ped in self.pedestrians:
                self.screen.blit(ped.image, (int(ped.x), int(ped.y)))

            # Draw traffic lights
            self._draw_signals()

            # Draw dashboard
            self._render_dashboard()
            
            # Draw pause indicator
            if self.paused:
                pause_text = self.font.render("PAUSED - Press SPACE to resume", True, (255, 255, 0))
                self.screen.blit(pause_text, (self.config.SCREEN_WIDTH // 2 - 100, 50))
            
            pygame.display.flip()
            self.clock.tick(60)  # 60 FPS
        
        pygame.quit()
        sys.exit()
    
    def _update_vehicle(self, vehicle: Vehicle) -> bool:
        """Update vehicle and return True if it should remain in simulation"""
        vehicle.move({})
        
        # Remove vehicles that have left the screen
        if (vehicle.x < -100 or vehicle.x > self.config.SCREEN_WIDTH + 100 or
            vehicle.y < -100 or vehicle.y > self.config.SCREEN_HEIGHT + 100):
            if vehicle.crossed:
                self.analytics.vehicles_crossed += 1
            return False
        
        return True

    def _get_pedestrian_signal_state(self) -> Dict[str, str]:
        """
        Determine pedestrian signal (Pgreen or Pred) based on vehicle signals.
        Returns dict: {'vertical': 'Pgreen'/'Pred', 'horizontal': 'Pgreen'/'Pred'}
        """
        # Assume signal 0 controls horizontal (left-right), signal 1 controls vertical (up-down)
        signal_horizontal = self.signals[0]
        signal_vertical = self.signals[1]

        horizontal_is_green = signal_horizontal.green > 0 or signal_horizontal.emergency_override
        vertical_is_green = signal_vertical.green > 0 or signal_vertical.emergency_override

        return {
            'horizontal': 'Pred' if horizontal_is_green else 'Pgreen',
            'vertical': 'Pred' if vertical_is_green else 'Pgreen'
        }


def main():
    """Main entry point"""
    print("🚦 Advanced Traffic Flow Simulation")
    print("📊 Features: AI Traffic Control, Collision Detection, Real-time Analytics")
    print("🎮 Controls: SPACE = Pause/Resume, R = Reset Stats, ESC = Exit")
    print("-" * 60)
    
    try:
        simulation = TrafficSimulation()
        simulation.run()
    except Exception as e:
        print(f"❌ Simulation error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()