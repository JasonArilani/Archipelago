from BaseClasses import ItemClassification, Region
from worlds.AutoWorld import WebWorld, World
from worlds.generic.Rules import set_rule
from worlds.LauncherComponents import Component, Type, components, launch

from .Items import EternalDarknessItem, ITEM_TABLE, get_item_classification
from .Locations import EternalDarknessLocation, LOCATION_TABLE
from .Options import EternalDarknessOptions



class EternalDarknessWeb(WebWorld):
    tutorials = []


class EternalDarknessWorld(World):
    """
    Eternal Darkness: Sanity's Requiem AP prototype.

    This initial world is an Anthony chapter pre-alpha with 8 Magick checks,
    8 Magick items, and Bishop defeat as the goal.
    """

    game = "Eternal Darkness"
    web = EternalDarknessWeb()

    options_dataclass = EternalDarknessOptions
    options: EternalDarknessOptions

    item_name_to_id = ITEM_TABLE
    location_name_to_id = LOCATION_TABLE

    item_name_groups = {
        "Runes": {
            "Weak Alignment Rune",
            "Antorbok Rune",
            "Magormor Rune",
        },
        "Codices": {
            "Weak Alignment Codex",
            "Antorbok Codex",
            "Magormor Codex",
        },
        "Circles": {
            "3 Point Circle",
        },
        "Scrolls": {
            "Enchant Item Scroll",
        },
    }

    def create_item(self, name: str) -> EternalDarknessItem:
        return EternalDarknessItem(
            name,
            get_item_classification(name),
            ITEM_TABLE[name],
            self.player,
        )

    def create_event(self, name: str) -> EternalDarknessItem:
        return EternalDarknessItem(
            name,
            ItemClassification.progression,
            None,
            self.player,
        )

    def create_regions(self) -> None:
        menu_region = Region("Menu", self.player, self.multiworld)
        anthony_region = Region("Anthony Chapter", self.player, self.multiworld)

        for location_name, location_id in LOCATION_TABLE.items():
            anthony_region.locations.append(
                EternalDarknessLocation(
                    self.player,
                    location_name,
                    location_id,
                    anthony_region,
                )
            )

        victory_location = EternalDarknessLocation(
            self.player,
            "Anthony - Bishop Defeated",
            None,
            anthony_region,
        )
        victory_location.place_locked_item(self.create_event("Victory"))
        anthony_region.locations.append(victory_location)

        menu_region.connect(anthony_region)

        self.multiworld.regions += [
            menu_region,
            anthony_region,
        ]

    def create_items(self) -> None:
        for item_name in ITEM_TABLE:
            self.multiworld.itempool.append(self.create_item(item_name))

    def fill_slot_data(self) -> dict:
        alignment_by_value = {
            0: "chatturgha",
            1: "ulyaoth",
            2: "xelotath",
        }

        return {
            "anthony_alignment": alignment_by_value[int(self.options.anthony_alignment.value)]
        }

    def set_rules(self) -> None:
        victory_location = self.multiworld.get_location(
            "Anthony - Bishop Defeated",
            self.player,
        )

        set_rule(
            victory_location,
            lambda state: state.has_all(
                {
                    "3 Point Circle",
                    "Weak Alignment Rune",
                    "Antorbok Rune",
                    "Magormor Rune",
                },
                self.player,
            ),
        )

        self.multiworld.completion_condition[self.player] = (
            lambda state: state.has("Victory", self.player)
        )
        
    def launch_eternal_darkness_client(*args: str):
        from .Client import run_client
        launch(run_client, name="Eternal Darkness Client", args=args)


    components.append(
        Component(
            "Eternal Darkness Client",
            func=launch_eternal_darkness_client,
            component_type=Type.CLIENT,
            game_name="Eternal Darkness",
            supports_uri=True,
            description="Connect Eternal Darkness: Sanity's Requiem to an Archipelago multiworld.",
        )
    )