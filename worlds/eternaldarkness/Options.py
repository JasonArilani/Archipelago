from dataclasses import dataclass

from Options import Choice, PerGameCommonOptions


class AnthonyAlignment(Choice):
    """
    Which alignment route Anthony is being played on.

    This determines which weak alignment rune/codex the client grants.
    """
    display_name = "Anthony Alignment"

    option_chatturgha = 0
    option_ulyaoth = 1
    option_xelotath = 2

    default = 0


@dataclass
class EternalDarknessOptions(PerGameCommonOptions):
    anthony_alignment: AnthonyAlignment