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
)
from mod_loader import ModLoader
from systems.detection import perform_detection
from systems.movement import player_movement
import random

random.seed(47)

debug = "d" in sys.argv


def create_world(loader, tile_map):
    for x in range(tile_map.cols):
        tile_map.set_tile(x, 0, 1)
        tile_map.set_tile(x, tile_map.rows - 1, 1)
    for y in range(tile_map.rows):
        tile_map.set_tile(0, y, 1)
        tile_map.set_tile(tile_map.cols - 1, y, 1)

    tile_map.set_tile(54, 50, 1)
    loader.spawn_entity("goblin", 52, 50)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()

    loader = ModLoader()
    loader.load_mods()

    tile_map = TileMap(100, 100, tile_defs=loader.tile_defs)
    spatial_hash = {}
    ui = UIManager()
    ui.options_text = "Press WASD to move."

    render_sys = RenderSystem(screen, ui, tile_map)
    esper.add_processor(render_sys, priority=1)

    create_world(loader, tile_map)
    player = loader.spawn_entity("player", 50, 50)

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
            elif event.type == pygame.KEYDOWN and event.key in valid_keys:
                if event.key in pressed_keys:
                    pressed_keys.remove(event.key)
                pressed_keys.append(event.key)
            elif event.type == pygame.KEYUP and event.key in pressed_keys:
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
                render_sys.set_cell_size(render_sys.CELL_SIZE - 5)
            elif debug and key == pygame.K_k:
                render_sys.set_cell_size(render_sys.CELL_SIZE + 5)

            if dx != 0 or dy != 0:
                player_movement(tile_map, dy, dx, spatial_hash, ui)

            last_move = now
        if wait_time >= MOVE_DELAY:
            # TODO
            # world logic stuff ig
            # it might or might not work
            # but its for later to add
            pass

        esper.process()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
