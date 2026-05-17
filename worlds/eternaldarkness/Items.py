from BaseClasses import Item, ItemClassification


ITEM_BASE_ID = 990100


ITEM_TABLE = {
    "3 Point Circle": ITEM_BASE_ID + 0,
    "Weak Alignment Rune": ITEM_BASE_ID + 1,
    "Antorbok Rune": ITEM_BASE_ID + 2,
    "Magormor Rune": ITEM_BASE_ID + 3,
    "Weak Alignment Codex": ITEM_BASE_ID + 4,
    "Antorbok Codex": ITEM_BASE_ID + 5,
    "Magormor Codex": ITEM_BASE_ID + 6,
    "Enchant Item Scroll": ITEM_BASE_ID + 7,
}


PROGRESSION_ITEMS = {
    "3 Point Circle",
    "Weak Alignment Rune",
    "Antorbok Rune",
    "Magormor Rune",
}


USEFUL_ITEMS = {
    "Weak Alignment Codex",
    "Antorbok Codex",
    "Magormor Codex",
    "Enchant Item Scroll",
}


class EternalDarknessItem(Item):
    game = "Eternal Darkness"


def get_item_classification(item_name: str) -> ItemClassification:
    if item_name in PROGRESSION_ITEMS:
        return ItemClassification.progression

    if item_name in USEFUL_ITEMS:
        return ItemClassification.useful

    return ItemClassification.filler