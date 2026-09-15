import esper
from ecs import Position, Name, Talkable, Openable, Pushable


class InteractionManager:
    @staticmethod
    def get_target(player, dx, dy, spatial_hash, ui):
        """Finds the entity you are trying to interact with."""
        pos = esper.component_for_entity(player, Position)
        target_pos = (pos.x + dx, pos.y + dy)

        entities = spatial_hash.get(target_pos, [])
        if not entities:
            ui.log("Hello, I'm Air, I can blow you")
            return None

        return entities[-1]

    @staticmethod
    def get_available_actions(entity):
        """Looks at the entity's components and returns a dictionary of valid actions."""
        actions = {}

        if esper.has_component(entity, Talkable):
            actions["a"] = "Talk"

        if esper.has_component(entity, Openable):
            open_data = esper.component_for_entity(entity, Openable)
            actions["b"] = "Close" if open_data.is_open else "Open"

        if esper.has_component(entity, Pushable):
            actions["c"] = "Push"

        return actions

    @staticmethod
    def execute_action(action_key, target, ui):
        """Runs the specific action the player chose."""
        name = (
            esper.component_for_entity(target, Name).text
            if esper.has_component(target, Name)
            else "Unknown Entity"
        )

        # we track if we actually did anything
        interacted = False

        # talking
        if action_key == "a" and esper.has_component(target, Talkable):
            talk_data = esper.component_for_entity(target, Talkable)
            ui.log(f"Interacting with {name}")
            ui.log(f"{name} said: {talk_data.message}")
            interacted = True

        # open it (chest things)
        elif action_key == "b" and esper.has_component(target, Openable):
            open_data = esper.component_for_entity(target, Openable)
            if open_data.locked:
                ui.log(f"The {name} is locked!")
            elif open_data.is_open:
                ui.log(f"You close the {name}.")
                open_data.is_open = False
            else:
                ui.log(f"You open the {name}.")
                open_data.is_open = True
            interacted = True

        # pushing
        elif action_key == "c" and esper.has_component(target, Pushable):
            push_data = esper.component_for_entity(target, Pushable)
            ui.log(f"You push {name}. It weighs {push_data.weight}kg.")
            interacted = True

        # for no interaction components
        if not interacted:
            ui.log("Nothing happens")
