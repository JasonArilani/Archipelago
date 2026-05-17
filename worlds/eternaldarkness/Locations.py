from BaseClasses import Location


LOCATION_BASE_ID = 990000


LOCATION_TABLE = {
    "Anthony - 3 Point Circle": LOCATION_BASE_ID + 0,
    "Anthony - Weak Alignment Rune": LOCATION_BASE_ID + 1,
    "Anthony - Antorbok Rune": LOCATION_BASE_ID + 2,
    "Anthony - Magormor Rune": LOCATION_BASE_ID + 3,
    "Anthony - Weak Alignment Codex": LOCATION_BASE_ID + 4,
    "Anthony - Antorbok Codex": LOCATION_BASE_ID + 5,
    "Anthony - Magormor Codex": LOCATION_BASE_ID + 6,
    "Anthony - Enchant Item Scroll": LOCATION_BASE_ID + 7,
}


class EternalDarknessLocation(Location):
    game = "Eternal Darkness"