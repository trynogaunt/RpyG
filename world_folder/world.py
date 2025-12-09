from __future__ import annotations
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass, field
import itertools
import random
import hashlib
from world_folder.room import RoomInstance

Vec2 = Tuple[int, int]


@dataclass
class WorldGraph:
    seed : int | None = None
    rng : random.Random = field(init=False, repr=False)
    rooms: Dict[str, "RoomInstance"] = field(default_factory=dict)
    start_room_id: str | None = None
    pos_index: Dict[Vec2, str] = field(default_factory=dict) # position to RoomInstance ID mapping (grid layout)
    
    def __post_init__(self):
        """
        Initialize the random number generator with the provided seed or a random seed.
        """
        if self.seed is None:
            self.seed = random.randint(0, 2**32 - 1)
        self.rng = random.Random(self.seed)

    def seed_from_string(text: str) -> int:
        """
        Generate a consistent integer seed from a given string using SHA-256 hashing.
        Args:
            text (str): The input string to generate the seed from.
        Returns:
            int: A consistent integer seed derived from the input string.
        """
        
        h = hashlib.sha256(text.encode("utf-8")).digest()
        return int.from_bytes(h[:8], "big")

    def add_room(self, room: "RoomInstance") -> None:
        """
        Add a room instance to the world graph.
        Args:
            room (RoomInstance): The room instance to add.
        Raises:
            ValueError: If the room's position is already occupied.
        """
        
        if room.position in self.pos_index: # Ensure no two rooms occupy the same position
            raise ValueError(
                f"Position {room.position} already occupied by room "
                f"{self.pos_index[room.position]}"
            )
        self.rooms[room.instance_id] = room # Add room to the world
        self.pos_index[room.position] = room.instance_id # Index room by position
        if self.start_room_id is None: # Set start room if not already set
            self.start_room_id = room.instance_id

    def link_bidirectional(self,room_id_a: str,direction_a_to_b: str,room_id_b: str,direction_b_to_a: str,) -> None:
        """
        Link two rooms bidirectionally in the world graph.
        Args:
            room_id_a (str): The ID of the first room.
            direction_a_to_b (str): The direction from the first room to the second room.
            room_id_b (str): The ID of the second room.
            direction_b_to_a (str): The direction from the second room to the first room.
        Raises:
            KeyError: If either room ID does not exist in the world graph.

        """
        self.rooms[room_id_a].connect(direction_a_to_b, room_id_b)
        self.rooms[room_id_b].connect(direction_b_to_a, room_id_a)


class ProcGenerator:
    """
    Procedural world generator for creating room instances and linking them in a world graph.   
    """
    def __init__(self, room_templates: Dict[str, "RoomTemplate"], world: WorldGraph):
        self.room_templates = room_templates
        self.world = world
        self._counter = itertools.count()
        self._used_unique_templates: Set[str] = set()

    def _new_instance_id(self) -> str:
        """
        Generate a new unique room instance ID.
        Returns:
            str: A unique room instance ID.
        """
        return f"room_{next(self._counter):04d}"

    def create_spawn(self, template_id: str, position: Vec2 = (0, 0)) -> str:
        """
        Create the spawn room instance at the specified position.
        Args:
            template_id (str): The ID of the room template to use for the spawn room.
            position (Vec2, optional): The position to place the spawn room. Defaults to (0, 0).
        Returns:
            str: The instance ID of the created spawn room.
        """
        tpl = self.room_templates[template_id]
        rid = self._new_instance_id()
        room = RoomInstance(rid, tpl, depth=0, position=position)
        self.world.add_room(room)
        return rid

    def eligible_templates(self, parent: "RoomInstance", new_depth: int) -> List["RoomTemplate"]:
        """
        Determine eligible room templates for generating a neighbor room.
        Args:
            parent (RoomInstance): The parent room instance from which the neighbor is being generated.
            new_depth (int): The depth of the new neighbor room.
        Returns:
            List[RoomTemplate]: A list of eligible room templates.
        """
        eligible: List[RoomTemplate] = []
        for tpl in self.room_templates.values():
            g = tpl.generation_parameters 
    
            if not (g.min_depth <= new_depth <= g.max_depth):
                print(f"Template {tpl.id} depth {new_depth} not in range {g.min_depth}-{g.max_depth}.")
                continue

          
            if g.unique_per_run and tpl.id in self._used_unique_templates:
                print(f"Skipping unique template {tpl.id} already used.")
                continue

            
            if len(parent.neighbors) >= parent.template.generation_parameters.max_neighbors:
                print(f"Parent room {parent.instance_id} has reached max neighbors.")
                continue
            
            if g.allowed_biome_neighbors and parent.biome not in g.allowed_biome_neighbors:
                print(f"Template {tpl.id} not allowed next to biome {parent.biome}.")
                continue
            
            if g.required_prev_tags_any and not any(tag in parent.tags for tag in g.required_prev_tags_any):
                print(f"Template {tpl.id} requires tags {g.required_prev_tags_any} not found in parent tags {parent.tags}.")
                continue
            
            if g.forbidden_prev_tags_all and any(tag in parent.tags for tag in g.forbidden_prev_tags_all):
                print(f"Template {tpl.id} has forbidden tags {g.forbidden_prev_tags_all} found in parent tags {parent.tags}.")
                continue
            
            eligible.append(tpl)
        return eligible

    def generate_neighbor(self, parent_id: str, direction: str, offset: Vec2) -> str | None:
        """
        Generate a neighbor room instance in the specified direction from the parent room.
        Args:
            parent_id (str): The ID of the parent room instance.
            direction (str): The direction to generate the neighbor room (e.g., "North", "South", "East", "West").
            offset (Vec2): The positional offset to apply for the new room.
        Logic:
            Check if a room already exists at the target position; if so, link to it.
            - Determine eligible room templates based on generation parameters.
            - Randomly select a template weighted by its generation weight.
            - Create the new room instance and add it to the world graph.
            - Link the new room bidirectionally with the parent room.
        Returns:
            str | None: The instance ID of the created neighbor room, or None if no eligible templates were found.
        """
        parent = self.world.rooms[parent_id]
        new_depth = parent.depth + 1
        px, py = parent.position
        position: Vec2 = (px + offset[0], py + offset[1])

        reverse = {
            "North": "South",
            "South": "North",
            "East": "West",
            "West": "East",
        }

        existing_id = self.world.pos_index.get(position) # Check for existing room at target position
        if existing_id is not None: # If room exists, link and return
            self.world.link_bidirectional(parent_id, direction, existing_id, reverse[direction])
            return existing_id

       
        candidates = self.eligible_templates(parent, new_depth) # Get eligible templates
        if not candidates: # No eligible templates found
            return None

        # Select a template based on weights
        weights = [tpl.generation_parameters.weight for tpl in candidates]
        tpl = self.world.rng.choices(candidates, weights=weights, k=1)[0]

        # Create the new room instance
        rid = self._new_instance_id()
        room = RoomInstance(rid, tpl, depth=new_depth, position=position)
        self.world.add_room(room)

        # Link the new room with the parent
        self.world.link_bidirectional(parent_id, direction, rid, reverse[direction])

        # Mark unique templates as used
        if tpl.generation_parameters.unique_per_run:
            self._used_unique_templates.add(tpl.id)

        
        neighbor_offsets = { # direction name to (dx, dy) to compute neighbor positions (grid layout)
            "North": (0, 1),
            "South": (0, -1),
            "East": (1, 0),
            "West": (-1, 0),
        } 

        for dir_name, (dx, dy) in neighbor_offsets.items():
            neighbor_pos: Vec2 = (position[0] + dx, position[1] + dy)
            neighbor_id = self.world.pos_index.get(neighbor_pos)
            if not neighbor_id:
                continue
            neighbor = self.world.rooms[neighbor_id]
            
            # Avoid linking back to parent
            if dir_name in room.neighbors and room.neighbors[dir_name] == neighbor_id:
                continue
            
            # Check max neighbors constraints for both rooms
            if len(room.neighbors) >= room.template.generation_parameters.max_neighbors:
                continue
            
            if len(neighbor.neighbors) >= neighbor.template.generation_parameters.max_neighbors:
                continue
            

            self.world.link_bidirectional(rid, dir_name, neighbor_id, reverse[dir_name])

        return rid


if __name__ == "__main__":
    import json
    from pathlib import Path
    from world_folder.room import RoomTemplate, GenerationParameters, ContentParameters, load_room_templates
    
    DIRECTIONS = {
        "North": (0, 1),
        "South": (0, -1),
        "East": (1, 0),
        "West": (-1, 0),
    }
    

    room_templates = load_room_templates(Path("world_folder/datas/room_templates.json"))

    world = WorldGraph() # Create a new world graph with a random seed
    gen = ProcGenerator(room_templates, world)
    
    spawn_id = gen.create_spawn("village_square")
    
    
    frontier = [spawn_id]
    successful_generations = 0
    failed_generations = 0
    for _ in range(1000): # Generate 10 neighbor rooms
        parent_id = world.rng.choice(frontier)
        dir_name, offset = world.rng.choice(list(DIRECTIONS.items()))
        nid = gen.generate_neighbor(parent_id, dir_name, offset)
        if nid and nid not in frontier:
            successful_generations += 1
            frontier.append(nid)
        else:
            failed_generations += 1
    print(f"Generated {successful_generations} rooms, {failed_generations} failed attempts.")
    for room in sorted(world.rooms.values(), key=lambda r: r.position):
        print(room)