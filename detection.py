import esper

from ecs import (
    Name,
    Renderable,
    NonDetectable,
)


def perform_detection(x, y, my_entity_id, spatial_hash, tile_map, ui):
    detected = []

    my_layer = 0
    if esper.has_component(my_entity_id, Renderable):
        my_layer = esper.component_for_entity(my_entity_id, Renderable).layer

    directions = [("Right", 1, 0), ("Left", -1, 0), ("Down", 0, 1), ("Up", 0, -1)]

    for dir_name, dx, dy in directions:
        nx, ny = x + dx, y + dy

        for ent in spatial_hash.get((nx, ny), []):
            if esper.has_component(ent, NonDetectable) and esper.component_for_entity(
                ent, NonDetectable
            ).WHAT in ["all", "horizontal"]:
                continue

            if esper.has_component(ent, Name):
                name = esper.component_for_entity(ent, Name).text
                detected.append(f"++{name}++ ({dir_name})")

        tile_def = tile_map.get_tile_def(nx, ny)
        if tile_def and tile_def.get("detect_horizontal", False):
            t_name = tile_def.get("name", "Tile")
            detected.append(f"++{t_name}++ ({dir_name})")

    current_tile = tile_map.get_tile_def(x, y)
    if current_tile and current_tile.get("detect_below", False):
        t_name = current_tile.get("name", "Ground")
        detected.append(f"--{t_name}-- (Below)")

    for ent in spatial_hash.get((x, y), []):
        if ent == my_entity_id:
            continue

        if esper.has_component(ent, Name) and esper.has_component(ent, Renderable):
            if esper.has_component(ent, NonDetectable) and esper.component_for_entity(
                ent, NonDetectable
            ).WHAT in ["all", "vertical"]:
                continue

            name = esper.component_for_entity(ent, Name).text
            obj_layer = esper.component_for_entity(ent, Renderable).layer
            if obj_layer < my_layer:
                detected.append(f"--{name}-- (Below)")
            elif obj_layer > my_layer:
                detected.append(f"--{name}-- (Above)")

    if detected:
        ui.log(f"**Player**: {', '.join(detected)}")
