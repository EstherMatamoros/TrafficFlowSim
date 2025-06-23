
class TrafficSignal:
    """Enhanced traffic signal with AI integration"""
    
    def __init__(self, red: int, yellow: int, green: int, signal_id: int):
        self.red = red
        self.yellow = yellow
        self.green = green
        self.signal_id = signal_id
        self.signalText = ""
        self.emergency_override = False
        self.efficiency_score = 0.0
    
    def update_timing(self, new_green: int):
        """Update signal timing based on AI recommendations"""
        self.green = new_green
    
    def emergency_mode(self, duration: int):
        """Activate emergency mode for emergency vehicles"""
        self.emergency_override = True
        self.green = duration

