class World:
    def __init__(self):
        self.zones = []
        
    def add_zone(self, zone : 'Zone'):
        self.zones.append(zone)
    
    def remove_zone(self, zone : 'Zone'):
        self.zones.remove(zone)