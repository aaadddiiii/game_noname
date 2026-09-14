import pygame
import sys
import esper
from config import *
from ecs import (
    RenderSystem,
    Position,
    Name,
    UIManager,
    TileMap,
)
from mod_loader import ModLoader
from detection import perform_detection
from movement import player_movement


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

    esper.add_processor(RenderSystem(screen, ui, tile_map), priority=1)

    create_world(loader, tile_map)
    player = loader.spawn_entity("player", 50, 50)

    for ent, pos in esper.get_component(Position):
        spatial_hash.setdefault((pos.x, pos.y), []).append(ent)

    perform_detection(50, 50, player, spatial_hash, tile_map, ui)

    running = True
    move_delay = 150
    last_move = 0
    pressed_keys = []

    while running:
        dx, dy = 0, 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key in (pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d):
                if event.key in pressed_keys:
                    pressed_keys.remove(event.key)
                pressed_keys.append(event.key)
            elif event.type == pygame.KEYUP and event.key in pressed_keys:
                pressed_keys.remove(event.key)

        now = pygame.time.get_ticks()

        if pressed_keys and now - last_move >= move_delay:
            key = pressed_keys[-1]
            if key == pygame.K_w:
                dy = -1
            elif key == pygame.K_s:
                dy = 1
            elif key == pygame.K_a:
                dx = -1
            elif key == pygame.K_d:
                dx = 1

            player_movement(tile_map, dy, dx, spatial_hash, ui)
            last_move = now

        esper.process()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
