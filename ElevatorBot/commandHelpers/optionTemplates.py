import copy
from typing import Any

from bungio.models import DamageType
from naff import OptionTypes, SlashCommandChoice, slash_option

import ElevatorBot.core.destiny.stat as stats
from ElevatorBot.misc.formatting import capitalize_string
from ElevatorBot.static.destinyDates import expansion_dates, season_and_expansion_dates
from ElevatorBot.static.timezones import timezones_dict
from Shared.enums.destiny import DestinyWeaponTypeEnum, UsableDestinyActivityModeTypeEnum


def get_timezone_choices() -> list[SlashCommandChoice]:
    return [
        SlashCommandChoice(
            name=timezone_name,
            value=timezone_value,
        )
        for timezone_name, timezone_value in timezones_dict.items()
    ]


# ===================================================================================
# Decorators


def default_user_option(
    description: str = "The user you want to look up",
    required: bool = False,
) -> Any:
    """
    Decorator that replaces @slash_option()

    Call with `@default_user_option()`
    """

    def wrapper(func):
        return slash_option(name="user", description=description, opt_type=OptionTypes.USER, required=required)(func)

    return wrapper


def lfg_event_id() -> Any:
    """
    Decorator that replaces @slash_option()

    Call with `@lfg_event_id()`
    """

    def wrapper(func):
        return slash_option(
            name="lfg_id", description="The lfg event ID", opt_type=OptionTypes.INTEGER, required=True, min_value=0
        )(func)

    return wrapper


def default_class_option(description: str = "Restrict the class. Default: All classes") -> Any:
    """
    Decorator that replaces @slash_option()

    Call with `@default_class_option()`
    """

    def wrapper(func):
        return slash_option(
            name="destiny_class",
            description=description,
            opt_type=OptionTypes.STRING,
            required=False,
            choices=[
                SlashCommandChoice(name="Warlock", value="Warlock"),
                SlashCommandChoice(name="Hunter", value="Hunter"),
                SlashCommandChoice(name="Titan", value="Titan"),
            ],
        )(func)

    return wrapper


def default_mode_option(description: str = "Restrict the game mode. Default: All modes", required: bool = False) -> Any:
    """
    Decorator that replaces @slash_option()

    Call with `@default_mode_option()`
    """

    def wrapper(func):
        return slash_option(
            name="mode",
            description=description,
            opt_type=OptionTypes.STRING,
            required=required,
            choices=[
                SlashCommandChoice(
                    name=capitalize_string(activity_type.name),
                    value=str(activity_type.value),
                )
                for activity_type in UsableDestinyActivityModeTypeEnum
            ],
        )(func)

    return wrapper


def default_stat_option(pvp: bool = False) -> Any:
    """
    Decorator that replaces @slash_option()

    Call with `@default_stat_option()`
    """

    def wrapper(func):
        if pvp:
            options = copy.deepcopy(stats.stat_translation)
            options.pop("Activities Cleared")
            options.pop("Public Events Completed")
            options.pop("Heroic Public Events Completed")

        else:
            options = stats.stat_translation

        return slash_option(
            name="name",
            description="The name of the leaderboard you want to see",
            opt_type=OptionTypes.STRING,
            required=True,
            choices=[SlashCommandChoice(name=name, value=name) for name in options],
        )(func)

    return wrapper


def default_time_option(
    name: str, description: str = "Format: `HH:MM DD/MM` - Restrict the time", required: bool = False
) -> Any:
    """
    Decorator that replaces @slash_option()

    Call with `@default_time_option()`
    """

    def wrapper(func):
        return slash_option(
            name=name,
            description=description,
            opt_type=OptionTypes.STRING,
            required=required,
        )(func)

    return wrapper


def default_expansion_option(
    description: str = "Restrict the expansion. Default: All expansions", required: bool = False
) -> Any:
    """
    Decorator that replaces @slash_option()

    Call with `@default_expansion_option()`

    The value is formatted:
    "name: str|start_time_timestamp: int|end_time_timestamp: int"
    """

    def wrapper(func):
        return slash_option(
            name="expansion",
            description=description,
            opt_type=OptionTypes.STRING,
            required=required,
            choices=[
                SlashCommandChoice(
                    name=expansion.name,
                    value=(
                        f"{expansion.name}|{int(expansion.start.timestamp())}|{int(expansion_dates[(expansion_dates.index(expansion) + 1)].start.timestamp())}"
                        if expansion_dates.index(expansion) + 1 < len(expansion_dates)
                        else f"{expansion.name}|{int(expansion.start.timestamp())}|9999999999"
                    ),
                )
                for expansion in expansion_dates
            ],
        )(func)

    return wrapper


def default_season_option(
    description: str = "Restrict the season. Default: All seasons", required: bool = False
) -> Any:
    """
    Decorator that replaces @slash_option()

    Call with `@default_season_option()`

    The value is formatted:
    "name|start_time_timestamp|end_time_timestamp"
    """

    def wrapper(func):
        return slash_option(
            name="season",
            description=description,
            opt_type=OptionTypes.STRING,
            required=required,
            choices=[
                SlashCommandChoice(
                    name=season.name,
                    value=(
                        f"{season.name}|{int(season.start.timestamp())}|{int(season_and_expansion_dates[(season_and_expansion_dates.index(season) + 1)].start.timestamp())}"
                        if season_and_expansion_dates.index(season) + 1 < len(season_and_expansion_dates)
                        else f"{season.name}|{int(season.start.timestamp())}|9999999999"
                    ),
                )
                for season in season_and_expansion_dates
            ],
        )(func)

    return wrapper


def default_weapon_type_option(
    description: str = "Restrict the weapon type. Default: All types", required: bool = False
) -> Any:
    """
    Decorator that replaces @slash_option()

    Call with `@default_weapon_type_option()`
    """

    def wrapper(func):
        return slash_option(
            name="weapon_type",
            description=description,
            opt_type=OptionTypes.INTEGER,
            required=required,
            choices=[
                SlashCommandChoice(
                    name=capitalize_string(weapon_type.name),
                    value=weapon_type.value,
                )
                for weapon_type in DestinyWeaponTypeEnum
            ],
        )(func)

    return wrapper


def default_damage_type_option(
    description: str = "Restrict the damage type. Default: All types", required: bool = False
) -> Any:
    """
    Decorator that replaces @slash_option()

    Call with `@default_damage_type_option()`
    """

    def wrapper(func):
        return slash_option(
            name="damage_type",
            description=description,
            opt_type=OptionTypes.INTEGER,
            required=required,
            choices=[
                SlashCommandChoice(
                    name=capitalize_string(damage_type.name),
                    value=damage_type.value,
                )
                for damage_type in DamageType
            ],
        )(func)

    return wrapper


def autocomplete_activity_option(
    description: str = "Restrict the activity. Overwrites `mode`. Default: All activities", required: bool = False
) -> Any:
    """
    Decorator that replaces @slash_option()

    Call with `@autocomplete_activity_option()`
    And register the autocomplete callback in setup()
    """

    def wrapper(func):
        name = "activity"

        option = slash_option(
            name=name, description=description, opt_type=OptionTypes.STRING, required=required, autocomplete=True
        )(func)

        return option

    return wrapper


def autocomplete_weapon_option(description: str, required: bool = False) -> Any:
    """
    Decorator that replaces @slash_option()

    Call with `@autocomplete_weapon_option()`
    And register the autocomplete callback in setup()
    """

    def wrapper(func):
        name = "weapon"

        option = slash_option(
            name=name, description=description, opt_type=OptionTypes.STRING, required=required, autocomplete=True
        )(func)

        return option

    return wrapper


def autocomplete_lore_option(
    description: str = "The name of item / card having the lore", required: bool = True
) -> Any:
    """
    Decorator that replaces @slash_option()

    Call with `@autocomplete_lore_option()`
    And register the autocomplete callback in setup()
    """

    def wrapper(func):
        name = "name"

        option = slash_option(
            name=name, description=description, opt_type=OptionTypes.STRING, required=required, autocomplete=True
        )(func)

        return option

    return wrapper
