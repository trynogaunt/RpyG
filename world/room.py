from dataclasses import dataclass, field
from typing import List, Dict, Optional
from pathlib import Path
import json

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
    pass

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