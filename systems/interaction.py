import esper
from ecs import Position, Name, Interaction

def interact(player, dx, dy, spatial_hash, ui):
    pos = esper.component_for_entity(player, Position)
    target_pos = (pos.x + dx, pos.y + dy)
    entities = spatial_hash.get(target_pos, [])
    if not entities:
        ui.log("Hello, I'm Air, I can blow you")
        return
    target = entities[0]
    name = esper.component_for_entity(target, Name).text if esper.has_component(target, Name) else "Unknown Entity"
    interaction = get_interaction(target)
    if interaction is None:
        ui.log("Nothing happens")
        return
    if interaction.type == "dialogue":
        ui.log(f"Interacting with {name}")
        ui.log(f'{name} said: {interaction.message}')

def get_interaction(entity):
    if not esper.has_component(entity, Interaction):
        return None
    return esper.component_for_entity(entity, Interaction)
