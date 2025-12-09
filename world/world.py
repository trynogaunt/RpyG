from typing import List, Dict
from dataclasses import dataclass, field
import itertools
import random

@dataclass
class WorldGraph:
    rooms: Dict[str, 'RoomInstance'] = field(default_factory=dict)
    start_room_id : str | None = None
    pos_index : Dict['Vec2', str] = field(default_factory=dict)
    
    
    def add_room(self, room: 'RoomInstance'):
        if room.position in self.pos_index:
            raise ValueError(f"Position {room.position} already occupied by room {self.pos_index[room.position]}")
        self.rooms[room.instance_id] = room
        self.pos_index[room.position] = room.instance_id
        if self.start_room_id is None:
            self.start_room_id = room.instance_id
    
    def link_bidirectional(self, room_id_a: str, direction_a_to_b: str, room_id_b: str, direction_b_to_a: str):
        self.rooms[room_id_a].connect(direction_a_to_b, room_id_b)
        self.rooms[room_id_b].connect(direction_b_to_a, room_id_a)
        

class ProcGenerator:
    def __init__(self, room_templates: Dict[str, 'RoomTemplate'], world : WorldGraph):
        self.room_templates = room_templates
        self._counter = itertools.count()
        self.world = world
        self._used_unique_templates : Set[str] = set()
    
    def _new_instance_id(self) -> str:
        return f"room_{next(self._counter):04d}"
    
    def create_spawn(self, templates : Dict[str, 'RoomTemplate'], position: Vec2 = [0, 0]) -> str:
        tpl = self.room_templates[template_id]
        rid = self._new_instance_id()
        room = RoomInstance(rid, tpl, depth=0, position=position)
        self.world.add_room(room)
        return rid
    
    def eligible_templates(self) -> List['RoomTemplate']:
        eligible = []
        for tpl in self.room_templates.values():
            if tpl.generation_parameters.unique_per_run and tpl.id in self._used_unique_templates:
                continue
            eligible.append(tpl)
        return eligible
    
    def generate_neighbor(self, parent_id : str, direction : str, offset: Vec2) -> str | None: 
        parent = self.world.rooms[parent_id]
        new_depth = parent.depth + 1
        px, py = parent.position
        position = (px + offset[0], py + offset[1])
        reverse = {"North": "South", "South": "North", "East": "West", "West": "East"}
        candidates = self.eligible_templates(parent, new_depth)
        if not candidates:
            return None
        
        weights = [tpl.generation_parameters.weight for tpl in candidates]
        tpl = random.choices(candidates, weights=weights, k=1)[0]
        
        rid = self._new_instance_id()
        target_id = self.world.pos_index.get(position)
        if target_id is not None:
            self.world.link_bidirectional(parent_id, direction, target_id, reverse[direction])
            return target_id

        room = RoomInstance(rid, tpl, depth=new_depth, position=position)
        self.world.add_room(room)
        
        self.world.link_bidirectional(parent_id, direction, rid,reverse[direction])
        if tpl.generation_parameters.unique_per_run:
            self._used_unique_templates.add(tpl.id)
            
        neighbor_offsets = {"North": (0, 1), "South": (0, -1), "East": (1, 0), "West": (-1, 0)}
        for dir_name, (dx, dy) in neighbor_offsets.items():
            neighbors_pos = (position[0] + dx, position[1] + dy)
            neightbor_id = self.world.pos_index.get(neighbors_pos)
            if not neightbor_id:
                continue
            if dir_name in room.neighbors and room.neighbors[dir_name] == neightbor_id:
                continue
            self.world.link_bidirectional(rid, dir_name, neightbor_id, reverse[dir_name])
        return rid