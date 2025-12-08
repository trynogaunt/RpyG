from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Set
from pathlib import Path
import json


Vec2 = Tuple[int, int]

@dataclass
class GenerationParameters:
    weight: int
    min_depth : int
    max_depth : int
    max_neighbors : int
    allowed_biome_neighbors : List[str]
    required_prev_tags_any : List[str]
    forbidden_prev_tags_all : List[str]
    unique_per_run : bool

@dataclass
class ContentParameters:
    encounter_table: Optional[Dict[str, int]] = None
    fixed_npc: List[str] = field(default_factory=list)
    shop_id: Optional[str] = None
    rest_point: bool = False
    story_flag_set: List[str] = field(default_factory=list)

@dataclass
class RoomTemplate:
    id: str
    label: str
    tags: List[str]
    biome: str
    generation_parameters: GenerationParameters
    content: ContentParameters
    
class RoomInstance():
    def __init__(self,instance_id: str, template: RoomTemplate, depth: int, position: Vec2):
        self.instance_id = instance_id #Unique identifier for this room instance per run
        self.template = template
        self.depth = depth
        self.position = position
        self.neighbors : Dict[str, str] = {} # Direction (North, South, East, West) to RoomInstance ID mapping
        self.visited : bool = False # Has the player visited this room yet? Story flags and encounters may depend on this.
        self.cleared : bool = False # Has the player cleared this room of encounters?
        self.state_flags: Set[str] = set() # Custom state flags for this room instance
        
    def __repr__(self):
        return f"<RoomInstance id={self.instance_id} template={self.template.id} depth={self.depth} pos={self.position}>"
    
    @property
    def biome(self) -> str:
        return self.template.biome

    def connect(self, direction: str, other_room_id: str):
        self.neighbors[direction] = other_room_id
    
    def marked_visited(self):
        self.visited = True
        for f in self.template.content.story_flag_set:
            self.state_flags.add(f)
          
    
    
def load_room_templates(path: Path) -> Dict[str, RoomTemplate]:
    raw = json.loads(path.read_text(encoding='utf-8'))
    templates: Dict[str, RoomTemplate] = {}
    for r in raw:
        gen = r["generation"]
        content = r["content"]
        
        tpl = RoomTemplate(
            id=r["id"],
            label=r["label"],
            tags=r["tags"],
            biome=r["biome"],
            generation_parameters=GenerationParameters(
                weight=gen["weight"],
                min_depth=gen["min_depth"],
                max_depth=gen["max_depth"],
                max_neighbors=gen["max_neighbors"],
                allowed_biome_neighbors=gen["allowed_biome_neighbors"],
                required_prev_tags_any=gen["required_prev_tags_any"],
                forbidden_prev_tags_all=gen["forbidden_prev_tags_all"],
                unique_per_run=gen["unique_per_run"]
            ),
            content=ContentParameters(
                encounter_table=content["encounter_table"] if "encounter_table" in content else None,
                fixed_npc=content["fixed_npc"] if "fixed_npc" in content else [],
                shop_id=content["shop_id"] if "shop_id" in content else None,
                rest_point=content["rest_point"] if "rest_point" in content else False,
                story_flag_set=content["story_flag_set"] if "story_flag_set" in content else []
            )
        )
        templates[tpl.id] = tpl
    return templates