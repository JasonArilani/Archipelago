"""MTIAA: conditional ending rewards, ending goals, and Period 20 access."""
from BaseClasses import Item, ItemClassification, Location, Region
from dataclasses import dataclass
from Options import Choice, PerGameCommonOptions, StartInventoryPool, Toggle
from worlds.AutoWorld import World, WebWorld
from worlds.generic.Rules import set_rule

GAME = "My Teacher Is an Alien"

LOCATIONS = {
    "Girls Locker Room - Susan's Cassette Recorder": 1001,
    "Mr. Daniels' Classroom - Magnet": 1002,
    "Boys Locker Room - Peter's Radio": 1003,
    "Mr. Tucker's Classroom - Tuning Fork": 1004,
    "Computer - Learned Disrupt Speech Test Recipe": 1005,
    "Maintenance Room - Dust Bunnies": 1006,
    "Maintenance Room - Moth Balls": 1007,
    "Kitchen - Blunder Bread": 1008,
    "Computer - Learned Taste Test Recipe": 1009,
    "Computer - Downloaded Awful Sound": 1010,
    "Computer - Learned Awful Sound Test Recipe": 1011,
    "Office - Thermos": 1012,
    "Computer - Learned Water Test": 1013,
    "Office - Maintenance Key": 1014,
    "Library - Obtained Computer Password": 1015,
    "Teacher's Lounge - Kidnapping List": 1016,
    "Hall - Susan Obtained Business Card": 1017,
    "Spaceship - Ray Gun and Glasses": 1018,
    "Spaceship - Alien Translator": 1019,
    "Hall - Found Alien Device": 1020,
    "Computer - Unlocked Alien Hunter Website": 1021,
    "Ducts - Enter the Duct System": 1022,
    "Spaceship - Enter the Spaceship": 1023,
    "Ducts - Removed Teacher's Lounge Vent": 1024,
    "Ducts - Cleared Rats": 1025,
    "Spaceship - Completed Left Bridge Puzzle": 1026,
    "Spaceship - Completed Right Bridge Puzzle": 1027,
    "Spaceship - Defeated Slime Boss": 1028,
    "Alien Device - Viewed Spaceship Maps": 1029,
    "Computer - Viewed Artifacts Page": 1030,
    "Spaceship - Discovered Hidden Nook": 1031,
    "Police Station - Spoke to Police Officer": 1032,
    "School - Identified Alien Teacher": 1033,
    "School - Ruled Out Mr. Tucker": 1034,
    "School - Ruled Out Ms. Marsh": 1035,
    "School - Ruled Out Mr. Daniels": 1036,
    "Ducts - Susan Witnessed Alien Mask Removal": 1037,
    "Boys Locker Room - Witnessed Mike's Kidnapping": 1038,
    "Rescued Linsey Carter": 1039,
    "Rescued Mike Foran": 1040,
    "Rescued Wendy Sanders": 1041,
    "Rescued Jack McCall": 1042,
    "Rescued Stacy Benoit": 1043,
    "Rescued Orville Plumber": 1044,
    "Complete Peter's Ending": 1045,
    "Complete Duncan's Ending": 1046,
    "Complete Susan's Ending": 1047,
    "Monday - Started Period 1": 1048,
    "Monday - Started Period 2": 1049,
    "Monday - Started Period 3": 1050,
    "Monday - Started Period 4": 1051,
    "Monday - Started Period 5": 1052,
    "Tuesday - Started Period 1": 1053,
    "Tuesday - Started Period 2": 1054,
    "Tuesday - Started Period 3": 1055,
    "Tuesday - Started Period 4": 1056,
    "Tuesday - Started Period 5": 1057,
    "Wednesday - Started Period 1": 1058,
    "Wednesday - Started Period 2": 1059,
    "Wednesday - Started Period 3": 1060,
    "Wednesday - Started Period 4": 1061,
    "Wednesday - Started Period 5": 1062,
    "Thursday - Started Period 1": 1063,
    "Thursday - Started Period 2": 1064,
    "Thursday - Started Period 3": 1065,
    "Thursday - Started Period 4": 1066,
    "Thursday - Started Period 5": 1067,
    "Mr. Daniels' Classroom - Peter Completed Roach Experiment": 1068,
    "Ms. Marsh's Classroom - Duncan Set Off Fire Alarm": 1069,
    "Mr. Tucker's Classroom - Susan Completed Investigation": 1070,
    "Hall - Survived Orville's Stink Bombs": 1071,
    "School - Performed Disrupt Speech Test": 1072,
    "School - Performed Taste Test": 1073,
    "School - Performed Awful Sound Test": 1074,
    "School - Performed Water Test": 1075,
    "Spaceship - Solved Left Forcefield": 1076,
    "Spaceship - Solved Middle Forcefield": 1077,
    "Spaceship - Solved Right Forcefield": 1078,
    "Complete Any Ending": 1079,
    "Complete Peter's Full Ending": 1080,
    "Complete Duncan's Full Ending": 1081,
    "Complete Susan's Full Ending": 1082,
    "Complete Any Full Ending": 1083,
}

REGULAR_ENDINGS = {
    "Peter": "Complete Peter's Ending",
    "Duncan": "Complete Duncan's Ending",
    "Susan": "Complete Susan's Ending",
}
FULL_ENDINGS = {
    "Peter": "Complete Peter's Full Ending",
    "Duncan": "Complete Duncan's Full Ending",
    "Susan": "Complete Susan's Full Ending",
}
ALL_ENDING_LOCATIONS = set(REGULAR_ENDINGS.values()) | set(FULL_ENDINGS.values()) | {
    "Complete Any Ending", "Complete Any Full Ending"
}
RESCUE_LOCATIONS = (
    "Rescued Linsey Carter", "Rescued Mike Foran", "Rescued Wendy Sanders",
    "Rescued Jack McCall", "Rescued Stacy Benoit", "Rescued Orville Plumber"
)

ITEMS = {
    "Magnet": 2001,
    "Cassette Recorder": 2002,
    "Radio": 2004,
    "Tuning Fork": 2005,
    "Disrupt Speech Test Recipe": 2006,
    "Dust Bunnies": 2007,
    "Moth Balls": 2008,
    "Blunder Bread": 2009,
    "Taste Test Recipe": 2010,
    "Awful Sound Download": 2011,
    "Awful Sound Test Recipe": 2012,
    "Thermos": 2013,
    "Water Test Knowledge": 2014,
    "Maintenance Key": 2015,
    "Computer Password": 2016,
    "Kidnapping List": 2017,
    "Business Card": 2018,
    "Ray Gun and Glasses": 2019,
    "Alien Translator": 2020,
    "Alien Device": 2025,
    "Susan Unlock": 2021,
    "Duncan Unlock": 2022,
    "Peter Unlock": 2024,
    "Progressive Period": 2023,
    "Nothing": 2003,
}


class StartingCharacter(Choice):
    """Pick a starting character, or unlock the entire cast immediately.

    `random_start` is the YAML spelling of Random because AP reserves the
    literal YAML value `random` for randomizing the option itself.
    """
    display_name = "Starting Character"
    option_peter = 0
    option_susan = 1
    option_duncan = 2
    option_random_start = 3
    option_all_three = 4
    default = 0


class Goal(Choice):
    display_name = "Goal"
    option_any_ending = 0
    option_peter_ending = 1
    option_susan_ending = 2
    option_duncan_ending = 3
    option_all_endings = 4
    default = 0


class FullEnding(Toggle):
    display_name = "Require Full Ending"
    default = 0


@dataclass
class MTIAAOptions(PerGameCommonOptions):
    starting_character: StartingCharacter
    goal: Goal
    full_ending: FullEnding
    start_inventory_from_pool: StartInventoryPool


class MTIAAItem(Item):
    game = GAME


class MTIAALocation(Location):
    game = GAME


class MTIAAWebWorld(WebWorld):
    theme = "partyTime"


class MTIAAWorld(World):
    """Archipelago world for My Teacher Is an Alien."""

    game = GAME
    web = MTIAAWebWorld()
    item_name_to_id = ITEMS
    location_name_to_id = LOCATIONS
    options_dataclass = MTIAAOptions

    def generate_early(self) -> None:
        option = self.options.starting_character.value
        # Select exactly once during generation, not each time a user opens
        # the game. Resolved character is shared with the bridge as slot data.
        self.resolved_start = self.random.randrange(3) if option == 3 else option
        self.starting_mask = 7 if self.resolved_start == 4 else 1 << self.resolved_start

    def fill_slot_data(self) -> dict:
        return {"starting_character": self.resolved_start,
                "starting_mask": self.starting_mask,
                "goal": self.options.goal.value,
                "full_ending": bool(self.options.full_ending.value)}

    def _starting_characters(self) -> set:
        return ({"Peter", "Susan", "Duncan"} if self.starting_mask == 7
                else {("Peter", "Susan", "Duncan")[self.resolved_start]})

    def _character_access(self, character: str):
        if character in self._starting_characters():
            return lambda state: True
        return lambda state: state.has(character + " Unlock", self.player)

    def _active_ending_locations(self):
        goal = self.options.goal.value
        if goal == Goal.option_any_ending:
            regular = ["Complete Any Ending"]
            full = ["Complete Any Full Ending"]
        elif goal == Goal.option_all_endings:
            regular = list(REGULAR_ENDINGS.values())
            full = list(FULL_ENDINGS.values())
        else:
            character = {
                Goal.option_peter_ending: "Peter",
                Goal.option_susan_ending: "Susan",
                Goal.option_duncan_ending: "Duncan",
            }[goal]
            regular = [REGULAR_ENDINGS[character]]
            full = [FULL_ENDINGS[character]]
        return regular + (full if self.options.full_ending.value else [])

    def _required_ending_locations(self):
        active = self._active_ending_locations()
        if self.options.full_ending.value:
            return [name for name in active if name in FULL_ENDINGS.values()
                    or name == "Complete Any Full Ending"]
        return active

    def create_regions(self) -> None:
        menu = Region("Menu", self.player, self.multiworld)
        active = set(self._active_ending_locations())
        for name, address in LOCATIONS.items():
            if name not in ALL_ENDING_LOCATIONS or name in active:
                menu.locations.append(MTIAALocation(self.player, name, address, menu))
        victory = MTIAALocation(self.player, "Victory", None, menu)
        victory.place_locked_item(MTIAAItem("Victory", ItemClassification.progression, None, self.player))
        menu.locations.append(victory)
        self.multiworld.regions.append(menu)

    def create_item(self, name: str) -> MTIAAItem:
        if name == "Nothing":
            classification = ItemClassification.filler
        elif name in ("Business Card", "Alien Translator"):
            classification = ItemClassification.useful
        else:
            classification = ItemClassification.progression
        return MTIAAItem(name, classification, ITEMS[name], self.player)

    def create_items(self) -> None:
        unlocked = self._starting_characters()
        pool = [self.create_item(name) for name in ITEMS
                if name != "Nothing" and
                not (name.endswith(" Unlock") and name[:-7] in unlocked)]
        pool.extend(self.create_item("Progressive Period") for _ in range(18))
        active_location_count = len(LOCATIONS) - len(ALL_ENDING_LOCATIONS) + len(self._active_ending_locations())
        if len(pool) > active_location_count:
            raise RuntimeError("More AP items than active locations")
        pool.extend(self.create_item("Nothing") for _ in range(active_location_count - len(pool)))
        self.multiworld.itempool.extend(pool)

    def set_rules(self) -> None:
        def has(state, item):
            return state.has(item, self.player)

        def character_available(state, character):
            return self._character_access(character)(state)

        def period_unlocked(state, period):
            return period <= 1 or state.has("Progressive Period", self.player, period - 1)

        def can_access_maintenance(state):
            return (
                (has(state, "Maintenance Key") and period_unlocked(state, 6))
                or period_unlocked(state, 11)
            )

        def can_use_computer(state, period):
            return period_unlocked(state, period) and (
                period >= 5
                or (has(state, "Computer Password") and period_unlocked(state, 4))
            )

        def can_access_spaceship(state):
            return has(state, "Alien Device") and can_reach_period(state, 6)

        def can_explore_spaceship(state):
            return can_access_spaceship(state) or can_reach_period(state, 20)

        def can_perform_speech(state):
            return all(has(state, item) for item in (
                "Disrupt Speech Test Recipe", "Radio", "Magnet", "Tuning Fork"
            ))

        def can_perform_taste(state):
            return all(has(state, item) for item in (
                "Taste Test Recipe", "Dust Bunnies", "Moth Balls", "Blunder Bread"
            ))

        def can_perform_sound(state):
            return (
                all(has(state, item) for item in (
                    "Awful Sound Test Recipe", "Cassette Recorder", "Awful Sound Download"
                ))
                and period_unlocked(state, 3)
            )

        def can_perform_water(state, pool_period=8):
            return has(state, "Water Test Knowledge") and (
                (has(state, "Thermos") and period_unlocked(state, 2))
                or period_unlocked(state, pool_period)
            )

        def can_identify_alien(state):
            return (
                can_perform_speech(state)
                or can_perform_taste(state)
                or can_perform_sound(state)
                or can_perform_water(state)
            )

        def can_continue_after_identification(state):
            available = sum(character_available(state, character) for character in (
                "Peter", "Susan", "Duncan"
            ))
            return (
                can_perform_speech(state)
                or can_perform_taste(state)
                or can_perform_water(state)
                or (can_perform_sound(state) and available >= 2)
            )

        def can_rule_out_teacher(state, teacher):
            pool_periods = {"Ms. Marsh": 8, "Mr. Daniels": 9, "Mr. Tucker": 12}
            return (
                can_perform_speech(state)
                or can_perform_taste(state)
                or can_perform_water(state, pool_periods[teacher])
            )

        def can_prevent_kidnapping(state):
            if not has(state, "Ray Gun and Glasses"):
                return False
            return (
                (
                    character_available(state, "Susan")
                    and (can_reach_period(state, 7) or can_reach_period(state, 14))
                )
                or (
                    (character_available(state, "Peter") or character_available(state, "Duncan"))
                    and (can_reach_period(state, 11) or can_reach_period(state, 16))
                )
            )

        def can_survive_captures(state):
            return can_access_spaceship(state) or can_prevent_kidnapping(state)

        def can_reach_period(state, period):
            return (
                period_unlocked(state, period)
                and (period <= 11 or can_continue_after_identification(state))
                and (period <= 16 or can_survive_captures(state))
            )

        def can_witness_mask(state):
            return (
                character_available(state, "Susan")
                and can_continue_after_identification(state)
                and (
                    (has(state, "Maintenance Key") and can_reach_period(state, 9))
                    or can_reach_period(state, 14)
                )
            )

        for period in range(1, 21):
            day = ("Monday", "Tuesday", "Wednesday", "Thursday")[(period - 1) // 5]
            name = f"{day} - Started Period {(period - 1) % 5 + 1}"
            set_rule(
                self.multiworld.get_location(name, self.player),
                lambda state, target=period: can_reach_period(state, target)
            )

        for name, period in (
            ("Mr. Tucker's Classroom - Tuning Fork", 3),
            ("Mr. Daniels' Classroom - Magnet", 4),
            ("Office - Thermos", 3),
            ("Office - Maintenance Key", 6),
            ("Library - Obtained Computer Password", 4),
            ("Kitchen - Blunder Bread", 6),
            ("Police Station - Spoke to Police Officer", 5),
            ("Hall - Survived Orville's Stink Bombs", 4),
            ("Hall - Found Alien Device", 1),
        ):
            set_rule(
                self.multiworld.get_location(name, self.player),
                lambda state, target=period: can_reach_period(state, target)
            )

        set_rule(
            self.multiworld.get_location("Alien Device - Viewed Spaceship Maps", self.player),
            lambda state: has(state, "Alien Device") and can_reach_period(state, 2)
        )

        for name in (
            "Maintenance Room - Dust Bunnies",
            "Maintenance Room - Moth Balls",
            "Ducts - Enter the Duct System",
            "Ducts - Removed Teacher's Lounge Vent",
            "Ducts - Cleared Rats",
        ):
            set_rule(
                self.multiworld.get_location(name, self.player),
                lambda state: can_access_maintenance(state)
            )

        for name, character in (
            ("Mr. Daniels' Classroom - Peter Completed Roach Experiment", "Peter"),
            ("Ms. Marsh's Classroom - Duncan Set Off Fire Alarm", "Duncan"),
            ("Mr. Tucker's Classroom - Susan Completed Investigation", "Susan"),
        ):
            set_rule(
                self.multiworld.get_location(name, self.player),
                self._character_access(character)
            )

        for name, character, period in (
            ("Girls Locker Room - Susan's Cassette Recorder", "Susan", 2),
            ("Boys Locker Room - Peter's Radio", "Peter", 3),
        ):
            set_rule(
                self.multiworld.get_location(name, self.player),
                lambda state, who=character, target=period: (
                    character_available(state, who) and can_reach_period(state, target)
                )
            )

        set_rule(
            self.multiworld.get_location("Boys Locker Room - Witnessed Mike's Kidnapping", self.player),
            lambda state: (
                (character_available(state, "Peter") or character_available(state, "Duncan"))
                and can_reach_period(state, 2)
            )
        )

        for name, period in (
            ("Computer - Unlocked Alien Hunter Website", 4),
            ("Computer - Learned Disrupt Speech Test Recipe", 4),
            ("Computer - Viewed Artifacts Page", 4),
            ("Computer - Learned Taste Test Recipe", 5),
            ("Computer - Learned Water Test", 6),
            ("Computer - Learned Awful Sound Test Recipe", 10),
            ("Computer - Downloaded Awful Sound", 10),
        ):
            set_rule(
                self.multiworld.get_location(name, self.player),
                lambda state, target=period: can_use_computer(state, target)
            )

        for name, predicate in (
            ("School - Performed Disrupt Speech Test", can_perform_speech),
            ("School - Performed Taste Test", can_perform_taste),
            ("School - Performed Awful Sound Test", can_perform_sound),
            ("School - Performed Water Test", can_perform_water),
            ("School - Identified Alien Teacher", can_identify_alien),
        ):
            set_rule(self.multiworld.get_location(name, self.player), predicate)

        for name, teacher in (
            ("School - Ruled Out Mr. Tucker", "Mr. Tucker"),
            ("School - Ruled Out Ms. Marsh", "Ms. Marsh"),
            ("School - Ruled Out Mr. Daniels", "Mr. Daniels"),
        ):
            set_rule(
                self.multiworld.get_location(name, self.player),
                lambda state, target=teacher: can_rule_out_teacher(state, target)
            )

        set_rule(
            self.multiworld.get_location("Teacher's Lounge - Kidnapping List", self.player),
            lambda state: can_access_maintenance(state) and can_continue_after_identification(state)
        )

        set_rule(
            self.multiworld.get_location("Ducts - Susan Witnessed Alien Mask Removal", self.player),
            can_witness_mask
        )

        set_rule(
            self.multiworld.get_location("Hall - Susan Obtained Business Card", self.player),
            lambda state: (
                character_available(state, "Susan")
                and has(state, "Kidnapping List")
                and can_witness_mask(state)
                and can_access_spaceship(state)
                and can_reach_period(state, 11)
            )
        )

        for name in (
            "Spaceship - Enter the Spaceship",
            "Spaceship - Ray Gun and Glasses",
            "Spaceship - Alien Translator",
            "Spaceship - Completed Left Bridge Puzzle",
            "Spaceship - Completed Right Bridge Puzzle",
            "Spaceship - Discovered Hidden Nook",
            "Spaceship - Solved Left Forcefield",
            "Spaceship - Solved Middle Forcefield",
            "Spaceship - Solved Right Forcefield",
        ):
            set_rule(
                self.multiworld.get_location(name, self.player),
                can_explore_spaceship
            )

        set_rule(
            self.multiworld.get_location("Spaceship - Defeated Slime Boss", self.player),
            can_access_spaceship
        )

        for name in ("Rescued Linsey Carter", "Rescued Mike Foran"):
            set_rule(
                self.multiworld.get_location(name, self.player),
                can_explore_spaceship
            )

        for name, ship_period, locker_period, locker_character in (
            ("Rescued Wendy Sanders", 8, 7, "Susan"),
            ("Rescued Jack McCall", 12, 11, None),
            ("Rescued Stacy Benoit", 16, 14, "Susan"),
            ("Rescued Orville Plumber", 17, 16, None),
        ):
            def rescue_rule(state, ship=ship_period, locker=locker_period, who=locker_character):
                can_shoot = (
                    has(state, "Ray Gun and Glasses")
                    and can_reach_period(state, locker)
                    and (
                        character_available(state, who) if who else
                        (character_available(state, "Peter") or character_available(state, "Duncan"))
                    )
                )
                return can_shoot or (
                    can_explore_spaceship(state) and can_reach_period(state, ship)
                )

            set_rule(self.multiworld.get_location(name, self.player), rescue_rule)

        active = set(self._active_ending_locations())
        for character, name in REGULAR_ENDINGS.items():
            if name in active:
                set_rule(
                    self.multiworld.get_location(name, self.player),
                    lambda state, who=character: (
                        character_available(state, who) and can_reach_period(state, 20)
                    )
                )

        if "Complete Any Ending" in active:
            set_rule(
                self.multiworld.get_location("Complete Any Ending", self.player),
                lambda state: can_reach_period(state, 20)
            )

        def all_students_rescuable(state):
            return all(state.can_reach(name, "Location", self.player) for name in RESCUE_LOCATIONS)

        for character, name in FULL_ENDINGS.items():
            if name in active:
                set_rule(
                    self.multiworld.get_location(name, self.player),
                    lambda state, who=character: (
                        character_available(state, who)
                        and can_reach_period(state, 20)
                        and all_students_rescuable(state)
                    )
                )

        if "Complete Any Full Ending" in active:
            set_rule(
                self.multiworld.get_location("Complete Any Full Ending", self.player),
                lambda state: can_reach_period(state, 20) and all_students_rescuable(state)
            )

        required = tuple(self._required_ending_locations())
        set_rule(
            self.multiworld.get_location("Victory", self.player),
            lambda state: all(state.can_reach(name, "Location", self.player) for name in required)
        )
        self.multiworld.completion_condition[self.player] = (
            lambda state: state.has("Victory", self.player)
        )

    def get_filler_item_name(self) -> str:
        return "Nothing"
