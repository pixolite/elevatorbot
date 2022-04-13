from dis_snek import InteractionContext, Member, Timestamp, TimestampStyles, slash_command

from ElevatorBot.commandHelpers.autocomplete import activities, autocomplete_send_activity_name
from ElevatorBot.commandHelpers.optionTemplates import (
    autocomplete_activity_option,
    default_class_option,
    default_expansion_option,
    default_season_option,
    default_time_option,
    default_user_option,
)
from ElevatorBot.commands.base import BaseScale
from ElevatorBot.core.destiny.activity import format_and_send_activity_data
from ElevatorBot.misc.formatting import add_filler_field, embed_message, format_timedelta
from ElevatorBot.misc.helperFunctions import parse_datetime_options
from ElevatorBot.networking.destiny.activities import DestinyActivities
from Shared.networkingSchemas.destiny import DestinyActivityInputModel


class DestinyActivity(BaseScale):
    @slash_command(name="activity", description="Display stats for Destiny 2 activities")
    @autocomplete_activity_option(description="Chose the activity you want to see the stats for", required=True)
    @default_class_option()
    @default_expansion_option()
    @default_season_option()
    @default_time_option(
        name="start_time",
        description="Format: `DD/MM/YY` - Input the **earliest** date you want the weapon stats for. Default: Big Bang",
    )
    @default_time_option(
        name="end_time",
        description="Format: `DD/MM/YY` - Input the **latest** date you want the weapon stats for. Default: Now",
    )
    @default_user_option()
    async def activity(
        self,
        ctx: InteractionContext,
        activity: str,
        destiny_class: str = None,
        expansion: str = None,
        season: str = None,
        start_time: str = None,
        end_time: str = None,
        user: Member = None,
    ):
        # parse start and end time
        start_time, end_time = await parse_datetime_options(
            ctx=ctx, expansion=expansion, season=season, start_time=start_time, end_time=end_time
        )
        if not start_time:
            return

        # get the actual activity
        if activity:
            activity = activities[activity.lower()]

        member = user or ctx.author
        backend_activities = DestinyActivities(ctx=ctx, discord_member=member, discord_guild=ctx.guild)

        # get the stats
        stats = await backend_activities.get_activity_stats(
            input_model=DestinyActivityInputModel(
                activity_ids=activity.activity_ids,
                character_class=destiny_class,
                start_time=start_time,
                end_time=end_time,
            )
        )

        await format_and_send_activity_data(
            ctx=ctx,
            member=member,
            stats=stats,
            name="Activity Stats",
            activity_name=activity.name,
            start_time=start_time,
            end_time=end_time,
            destiny_class=destiny_class,
        )


def setup(client):
    command = DestinyActivity(client)

    # register the autocomplete callback
    command.activity.autocomplete("activity")(autocomplete_send_activity_name)
