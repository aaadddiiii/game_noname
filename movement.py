import esper
from ecs import Blocker, Position, PlayerInput
from detection import perform_detection


def player_movement(tile_map, dy, dx, spatial_hash, ui):
    for ent, (pos, _) in esper.get_components(Position, PlayerInput):
        tx, ty = pos.x + dx, pos.y + dy

        terrain_blocked = tile_map.is_blocked(tx, ty)
        entity_blocked = any(
            esper.has_component(t_ent, Blocker)
            for t_ent in spatial_hash.get((tx, ty), [])
        )

        if not terrain_blocked and not entity_blocked:
            spatial_hash[(pos.x, pos.y)].remove(ent)
            pos.x, pos.y = tx, ty
            spatial_hash.setdefault((tx, ty), []).append(ent)

            perform_detection(pos.x, pos.y, ent, spatial_hash, tile_map, ui)
