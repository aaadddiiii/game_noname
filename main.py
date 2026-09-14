import pygame
import sys
import esper
from config import *
import config
from ecs import (
    RenderSystem,
    Position,
    Name,
    UIManager,
    TileMap,
    ChunkManager,
)

from systems.interaction import interact 
from mod_loader import ModLoader
from systems.detection import perform_detection
from systems.movement import player_movement
import random

random.seed(47)

debug = "d" in sys.argv


def create_world(loader, tile_map, chunk_manager):
    for x in range(tile_map.cols):
        tile_map.set_tile(x, 0, 1)
        tile_map.set_tile(x, tile_map.rows - 1, 1)
    for y in range(tile_map.rows):
        tile_map.set_tile(0, y, 1)
        tile_map.set_tile(tile_map.cols - 1, y, 1)

    tile_map.set_tile(54, 50, 1)
    goblin_id = loader.spawn_entity("goblin", 52, 50)
    chunk_manager.add_entity(goblin_id, 52, 50)




def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()

    loader = ModLoader()
    loader.load_mods()

    tile_map = TileMap(100, 100, tile_defs=loader.tile_defs)
    chunk_manager = ChunkManager(chunk_size=16)
    spatial_hash = {}
    ui = UIManager()
    ui.options_text = "Press WASD to move."

    render_sys = RenderSystem(screen, ui, tile_map)
    esper.add_processor(render_sys, priority=1)

    create_world(loader, tile_map, chunk_manager)
    player = loader.spawn_entity("player", 50, 50)
    interaction_mode = False
    # interaction_mode = InteractionMode()

    for ent, pos in esper.get_component(Position):
        spatial_hash.setdefault((pos.x, pos.y), []).append(ent)

    perform_detection(50, 50, player, spatial_hash, tile_map, ui)

    running = True
    MOVE_DELAY = 150
    last_move = 0
    pressed_keys = []

    valid_keys = (pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d)
    if debug:
        valid_keys += (pygame.K_j, pygame.K_k)

    while running:
        dx, dy = 0, 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_i:
                interaction_mode = not interaction_mode
                if interaction_mode:
                    ui.options_text = "Interaction Mode: W/A/S/D to interact. I to exit."
                    ui.log("Entered interaction mode")
                else:
                    ui.options_text = "Press WASD to move."
                    ui.log("Exited interaction mode")
            elif event.type == pygame.KEYDOWN and event.key in valid_keys:
                if event.key not in pressed_keys:
                    pressed_keys.append(event.key)
            elif event.type == pygame.KEYUP:
                if event.key in pressed_keys:
                    pressed_keys.remove(event.key)

        now = pygame.time.get_ticks()
        wait_time = now - last_move

        if pressed_keys and wait_time >= MOVE_DELAY:
            key = pressed_keys[-1]
            # other stuff

            if key == pygame.K_w:
                dy = -1
            elif key == pygame.K_s:
                dy = 1
            elif key == pygame.K_a:
                dx = -1
            elif key == pygame.K_d:
                dx = 1

            # debug stuff
            elif debug and key == pygame.K_j:
                render_sys.set_cell_size(render_sys.CELL_SIZE - 1)
            elif debug and key == pygame.K_k:
                render_sys.set_cell_size(render_sys.CELL_SIZE + 1)

        if dx != 0 or dy != 0:
            if interaction_mode:
                interact(player, dx, dy, spatial_hash, ui)
            else:
                player_movement(tile_map, dy, dx, spatial_hash, ui)

            last_move = now
        if wait_time >= MOVE_DELAY:
            # TODO
            # world logic stuff ig
            # it might or might not work
            # but its for later to add

            if player is not None:
                player_pos = esper.component_for_entity(player, Position)

                to_load, to_unload = chunk_manager.update_loaded_area(
                    player_pos.x, player_pos.y, radius=1
                )

                # UNLOAD
                for cx, cy in to_unload:
                    if (cx, cy) in chunk_manager.chunk_entities:
                        for ent_id in list(chunk_manager.chunk_entities[(cx, cy)]):
                            if ent_id != player:
                                if esper.has_component(ent_id, Position):
                                    pos = esper.component_for_entity(ent_id, Position)
                                    if (
                                        pos.x,
                                        pos.y,
                                    ) in spatial_hash and ent_id in spatial_hash[
                                        (pos.x, pos.y)
                                    ]:
                                        spatial_hash[(pos.x, pos.y)].remove(ent_id)

                                esper.delete_entity(ent_id)

                        del chunk_manager.chunk_entities[(cx, cy)]

                # LOAD
                for cx, cy in to_load:
                    chunk_manager.chunk_entities[(cx, cy)] = set()

                    if random.random() < 0.10:
                        spawn_x = (cx * chunk_manager.chunk_size) + 8
                        spawn_y = (cy * chunk_manager.chunk_size) + 8
                        new_gob = loader.spawn_entity("goblin", spawn_x, spawn_y)
                        chunk_manager.add_entity(new_gob, spawn_x, spawn_y)
                        spatial_hash.setdefault((spawn_x, spawn_y), []).append(new_gob)

        esper.process()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
