def creation_header(ui: "UIController") -> list[str]:
    title = "Character Creation"
    return ui.header(title)

def resume_creation_section(attributes : list[dict]) -> list[str]:
    lines = []
    lines.append("Character Summary:")
    lines.append("")
    for attr in attributes:
        lines.append(f"{attr['label'].capitalize()}: {attr['value']}")
    return lines

def build_creation_menu(ui: "UIController", response : "GameResponse") -> list[str]:
    step = response.payload.get("step")
    attributes = response.payload.get("attributes", [])
    error = response.payload.get("error", "")
    msg = response.message
    lines = []
    lines += creation_header(ui)
    if error:
        lines.append(f"Error: {error}")
    if msg:
        lines.append(msg)
    lines.append("")
    lines.append(f"Name: {response.payload.get('name', '')}")
    lines += resume_creation_section(attributes)
    lines.append("")
    
    return lines