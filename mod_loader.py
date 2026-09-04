import json
import os
import esper
import ecs


class ModLoader:
    def __init__(self):
        self.blueprints = {}
        self.tile_defs = {}

    def load_mods(self, mod_folder="mods"):
        if not os.path.exists(mod_folder):
            print(f"Warning: {mod_folder} directory not found")
            return

        for root, _, files in os.walk(mod_folder):
            for file in files:
                if not file.endswith(".json"):
                    continue

                full_path = os.path.join(root, file)

                if file == "tiles.json":
                    with open(full_path, "r") as f:
                        raw_tiles = json.load(f)
                        for k, v in raw_tiles.items():
                            self.tile_defs[int(k)] = v
                    print(f"Loaded tiles from: {full_path}")

                else:
                    with open(full_path, "r") as f:
                        data = json.load(f)
                        self.blueprints.update(data)
                    print(f"Loaded entities from: {full_path}")

    def spawn_entity(self, entity_id_name, x, y):
        if entity_id_name not in self.blueprints:
            print(f"Error: Entity '{entity_id_name}' not found in mods")
            return None

        blueprint = self.blueprints[entity_id_name]
        entity = esper.create_entity()
        esper.add_component(entity, ecs.Position(x, y))

        for comp_name, kwargs in blueprint.items():
            if hasattr(ecs, comp_name):
                ComponentClass = getattr(ecs, comp_name)
                esper.add_component(entity, ComponentClass(**kwargs))

        return entity
