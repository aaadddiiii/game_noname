# ecs.py
import esper
import pygame
import os
import re
from config import *
import random

class Position:
    def __init__(self, x=0, y=0):
        self.x, self.y = x, y


class Renderable:
    def __init__(self, char="?", color=(255, 255, 255), layer=0, image=None):
        self.char, self.color, self.layer, self.image = char, color, layer, image


class Blocker:
    pass


class NonDetectable:
    def __init__(self, WHAT) -> None:
        self.WHAT = WHAT


class PlayerInput:
    pass


class Name:
    def __init__(self, text="Unknown"):
        self.text = text


class UIManager:
    def __init__(self):
        self.logs = []
        self.options_text = ""

    def log(self, msg):
        self.logs.insert(0, msg)
        if len(self.logs) > 40:
            self.logs.pop()


class TileMap:
    def __init__(self, cols=100, rows=100, tile_defs=None):
        self.cols = cols
        self.rows = rows
        self.tile_defs = tile_defs or {}
        self.grid = [[0 for _ in range(cols)] for _ in range(rows)]
        self.variants = [[self._choose_variant(0) for _ in range(cols)] for _ in range(rows)]

    def _choose_variant(self, tile_type):
        tile_def = self.tile_defs.get(tile_type, {})
        variants = tile_def.get("variants", [])
        if not variants:
            return None
        weights = [variant.get("weight", 1) for variant in variants]
        return random.choices(range(len(variants)), weights=weights, k=1)[0]

    def get_tile_id(self, x, y):
        if 0 <= x < self.cols and 0 <= y < self.rows:
            return self.grid[y][x]
        return None

    def get_tile_variant(self, x, y):
        if 0 <= x < self.cols and 0 <= y < self.rows:
            return self.variants[y][x]
        return None

    def get_tile_def(self, x, y):
        tid = self.get_tile_id(x, y)
        if tid is not None:
            return self.tile_defs.get(tid)
        return None

    def set_tile(self, x, y, tile_type):
        if 0 <= x < self.cols and 0 <= y < self.rows:
            self.grid[y][x] = tile_type
            self.variants[y][x] = self._choose_variant(tile_type)

    def is_blocked(self, x, y):
        if not (0 <= x < self.cols and 0 <= y < self.rows):
            return True
        t_def = self.get_tile_def(x, y)
        if t_def is not None:
            return t_def.get("blocked", False)
        return False


class RenderSystem(esper.Processor):
    def __init__(self, screen, ui_manager, tile_map):
        self.screen = screen
        self.ui = ui_manager
        self.tile_map = tile_map
        self.font = pygame.font.SysFont("segoeuiemoji", 16)
        self.font_bold = pygame.font.SysFont("segoeuiemoji", 16, bold=True)
        self.image_cache = {}
        self.tileset_cache = {}

        self.sorted_tags = sorted(TEXT_STYLES.keys(), key=len, reverse=True)
        regex_parts = [
            f"{re.escape(tag)}.*?{re.escape(tag)}" for tag in self.sorted_tags
        ]
        self.rich_text_regex = re.compile(f"({'|'.join(regex_parts)})")

    def get_image(self, img_path):
        if not img_path:
            return None
        if img_path not in self.image_cache:
            if os.path.exists(img_path):
                img = pygame.image.load(img_path).convert_alpha()
                self.image_cache[img_path] = pygame.transform.scale(
                    img, (CELL_SIZE, CELL_SIZE)
                )
            else:
                self.image_cache[img_path] = None
        return self.image_cache[img_path]

    def get_tileset(self, path):
        if not path:
            return None
        if path not in self.tileset_cache:
            if os.path.exists(path):
                self.tileset_cache[path] = pygame.image.load(path).convert_alpha()
            else:
                self.tileset_cache[path] = None
        return self.tileset_cache[path]

    def get_tile_image(self, tile_def, variant_index):
        variants = tile_def.get("variants", [])
        if variant_index is None or variant_index >= len(variants):
            return None
        sheet = self.get_tileset(tile_def.get("tileset"))
        if not sheet:
            return None
        variant = variants[variant_index]
        tile_size = tile_def.get("tile_size", CELL_SIZE)
        rect = pygame.Rect(variant["x"] * tile_size, variant["y"] * tile_size, tile_size, tile_size)
        return sheet.subsurface(rect)

    def process(self):
        self.screen.fill(BG_MAIN)
        self.draw_map()
        self.draw_ui()
        pygame.display.flip()

    def draw_map(self):
        map_rect = pygame.Rect(0, 0, MAP_WIDTH, MAP_HEIGHT)
        self.screen.set_clip(map_rect)

        cam_x, cam_y = 0, 0
        for ent, (pos, _) in esper.get_components(Position, PlayerInput):
            cam_x = pos.x - (MAP_WIDTH // CELL_SIZE // 2)
            cam_y = pos.y - (MAP_HEIGHT // CELL_SIZE // 2)

        tiles_w = (MAP_WIDTH // CELL_SIZE) + 1
        tiles_h = (MAP_HEIGHT // CELL_SIZE) + 1

        for sy in range(tiles_h):
            for sx in range(tiles_w):
                tx, ty = cam_x + sx, cam_y + sy
                t_def = self.tile_map.get_tile_def(tx, ty)

                rect = pygame.Rect(sx * CELL_SIZE, sy * CELL_SIZE, CELL_SIZE, CELL_SIZE)

                if t_def:
                    if t_def.get("tileset"):
                        img = self.get_tile_image(t_def, self.tile_map.get_tile_variant(tx, ty))
                    else:
                        img = self.get_image(t_def.get("image"))
                    if img:
                        self.screen.blit(img, rect)
                    else:
                        is_blocked = t_def.get("blocked", False)
                        fallback_color = (60, 60, 60) if is_blocked else (34, 70, 34)
                        pygame.draw.rect(self.screen, fallback_color, rect)
                        char = "#" if is_blocked else "."
                        txt = self.font.render(char, True, (120, 120, 120))
                        self.screen.blit(txt, txt.get_rect(center=rect.center))
                else:
                    pygame.draw.rect(self.screen, (0, 0, 0), rect)

        renderables = [
            (pos, rend)
            for ent, (pos, rend) in esper.get_components(Position, Renderable)
        ]
        renderables.sort(key=lambda item: item[1].layer)

        for pos, rend in renderables:
            draw_x = (pos.x - cam_x) * CELL_SIZE
            draw_y = (pos.y - cam_y) * CELL_SIZE

            if 0 <= draw_x <= MAP_WIDTH and 0 <= draw_y <= MAP_HEIGHT:
                rect = pygame.Rect(draw_x, draw_y, CELL_SIZE, CELL_SIZE)
                img = self.get_image(rend.image) if rend.image else None
                if img:
                    self.screen.blit(img, rect)
                else:
                    text_surf = self.font.render(rend.char, True, rend.color)
                    self.screen.blit(text_surf, text_surf.get_rect(center=rect.center))

        self.screen.set_clip(None)

    def draw_ui(self):
        pygame.draw.rect(
            self.screen, BG_LOGS, (LOG_PANEL_X, 0, LOG_PANEL_WIDTH, LOG_PANEL_HEIGHT)
        )
        pygame.draw.line(
            self.screen, C_WHITE, (LOG_PANEL_X, 0), (LOG_PANEL_X, LOG_PANEL_HEIGHT), 2
        )
        self.screen.blit(
            self.font_bold.render("WORLD EVENTS", True, C_BLUE), (LOG_PANEL_X + 10, 10)
        )

        curr_y = 40
        for msg in self.ui.logs:
            curr_y = (
                self.render_rich_text(
                    msg, LOG_PANEL_X + 10, curr_y, LOG_PANEL_WIDTH - 20
                )
                + 10
            )
            if curr_y > LOG_PANEL_HEIGHT:
                break

        pygame.draw.rect(
            self.screen, BG_OPTS, (0, OPT_PANEL_Y, OPT_PANEL_WIDTH, OPT_PANEL_HEIGHT)
        )
        pygame.draw.line(
            self.screen, C_WHITE, (0, OPT_PANEL_Y), (OPT_PANEL_WIDTH, OPT_PANEL_Y), 2
        )
        self.screen.blit(
            self.font_bold.render("ACTIONS / INFO", True, C_BLUE),
            (10, OPT_PANEL_Y + 10),
        )
        if self.ui.options_text:
            self.render_rich_text(
                self.ui.options_text, 10, OPT_PANEL_Y + 40, OPT_PANEL_WIDTH - 20
            )

    def render_rich_text(self, text, start_x, start_y, max_width):
        tokens = []
        parts = self.rich_text_regex.split(text)

        for part in parts:
            if not part:
                continue
            color, font, clean_part = C_WHITE, self.font, part

            for tag in self.sorted_tags:
                if (
                    part.startswith(tag)
                    and part.endswith(tag)
                    and len(part) >= len(tag) * 2
                ):
                    style = TEXT_STYLES[tag]
                    color = style["color"]
                    font = self.font_bold if style.get("bold") else self.font
                    clean_part = part[len(tag) : -len(tag)]
                    break

            for w in clean_part.split(" "):
                tokens.append((w + " ", font, color))

        curr_x, curr_y = start_x, start_y
        for word, font, color in tokens:
            surf = font.render(word, True, color)
            if curr_x + surf.get_width() > start_x + max_width and curr_x != start_x:
                curr_x = start_x
                curr_y += 20
            if curr_y < WINDOW_HEIGHT:
                self.screen.blit(surf, (curr_x, curr_y))
            curr_x += surf.get_width()

        return curr_y + 20
