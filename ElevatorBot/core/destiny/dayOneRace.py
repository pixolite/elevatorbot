import asyncio
import copy
import datetime
import logging
import pickle
from io import BytesIO
from typing import Optional

import aiohttp
from anyio import create_task_group
from naff import File, GuildText, Member, Message, Timestamp, TimestampStyles

from ElevatorBot.commandHelpers.responseTemplates import something_went_wrong
from ElevatorBot.discordEvents.customInteractions import ElevatorInteractionContext
from ElevatorBot.misc.formatting import embed_message, format_timedelta
from ElevatorBot.networking.destiny.account import DestinyAccount
from ElevatorBot.networking.destiny.activities import DestinyActivities
from ElevatorBot.networking.destiny.clan import DestinyClan
from ElevatorBot.networking.errors import BackendException
from ElevatorBot.static.descendOnlyIds import descend_channels
from ElevatorBot.static.emojis import custom_emojis
from Shared.functions.helperFunctions import get_now_with_tz
from Shared.networkingSchemas.destiny import DestinyActivityInputModel, DestinyActivityOutputModel
from Shared.networkingSchemas.destiny.clan import DestinyClanMemberModel, DestinyClanMembersModel


class DayOneRace:
    # >>> CHANGE HERE FOR DIFFERENT DAY 1 HASHES <<<
    # see data.destinysets.com

    # here updates get posted
    leaderboard_channel: int | GuildText = 837622568152203304

    # the main triumph with encounter objectives
    activity_triumph_encounters: dict[int, dict[int, str]] = {
        3114569402: {
            4240665: "First Raid Run",
            4240664: "Conflux Challenge",
            4240667: "Oracle Challenge",
            4240666: "Templar Challenge",
            4240669: "Gatekeeper Challenge",
            4240668: "Atheon Challenge",
        }
    }

    # alternative things to look at if the main triumph fails
    alternative_activity_triumphs: list[int] = [384429092]
    activity_metrics: list[int] = [2506886274]
    emblem_hashes: list[int] = [2172413746]

    # the activity ids of the raid
    activity_hashes: list[int] = [1485585878, 3711931140, 3881495763]

    # when the raid race ends
    cutoff_time: datetime.datetime = datetime.datetime(2021, 5, 23, 17, 0, tzinfo=datetime.timezone.utc)

    # cosmetic data for the raid
    image_url: str = (
        "https://static.wikia.nocookie.net/destinypedia/images/6/62/Vault.jpg/revision/latest/scale-to-width-down/1000?cb=20150330170833"
    )
    raid_name: str = "Vault of Glass"
    location_name: str = "Ishtar Sink, Venus"

    # vars needed for the command
    def __init__(self, ctx: ElevatorInteractionContext):
        self.ctx = ctx
        self.channel = ctx.channel

        self.leaderboard_msg: Optional[Message] = None
        self.activity_triumph: int = list(self.activity_triumph_encounters.keys())[0]

        # {triumph_id: T/F}
        self.finished_encounters_blueprint: dict[int, bool] = {}
        # {destiny_id: finished_encounters_blueprint}
        self.finished_encounters: dict[int, dict[int, bool]] = {}
        # {destiny_id: datetime.datetime}
        self.finished_raid: dict[int, datetime.datetime] = {}

        self.clan_members: Optional[DestinyClanMembersModel] = None
        # {destiny_id: @member | bungie_name#1234}
        self.destiny_id_translation: dict[int, Member] = {}

    async def start(self):
        """Start the racer"""

        # printing the raid image. Taken from data.destinysets.com
        activity_name = f"{self.location_name} - {self.raid_name}"
        async with aiohttp.ClientSession() as session:
            async with session.get(self.image_url) as resp:
                if resp.status == 200:
                    data = BytesIO(await resp.read())
                    await self.channel.send(
                        f"__**{activity_name}**__\nMy day one mode is now activated and I will (hopefully) inform about completions. \nGood luck to everyone competing, will see you on the other side."
                    )
                    await self.channel.send(file=File(file=data, file_name="raid_image.png"))

        self.leaderboard_channel = await self.ctx.bot.fetch_channel(self.leaderboard_channel)
        if not self.leaderboard_channel:
            await something_went_wrong(ctx=self.ctx)
            return

        # blueprint how completed encounters are stored for each user
        self.finished_encounters_blueprint = {}
        for encounter in self.activity_triumph_encounters[self.activity_triumph]:
            self.finished_encounters_blueprint[encounter] = False

        # get clan members
        clan = DestinyClan(discord_guild=self.ctx.guild, ctx=self.ctx)
        self.clan_members = await clan.get_clan_members()

        for member in self.clan_members.members:
            discord_member = await self.ctx.guild.fetch_member(member.discord_id) if member.discord_id else None
            if not discord_member:
                await self.ctx.send(f"Don't know discord_id for {member.name}", ephemeral=True)
                return
            self.destiny_id_translation.update({member.destiny_id: discord_member})

        await self.ctx.send("Done", ephemeral=True)

        # open the old data if that exists
        try:
            with open(f"{self.raid_name}_finished_encounters.pickle", "rb") as handle:
                self.finished_encounters = pickle.load(handle)
            with open(f"{self.raid_name}_finished_raid.pickle", "rb") as handle:
                self.finished_raid = pickle.load(handle)
        except FileNotFoundError:
            self.finished_raid = {}
            self.finished_encounters = {}
            for member in self.clan_members.members:
                destiny_id = member.destiny_id
                self.finished_encounters[destiny_id] = copy.copy(self.finished_encounters_blueprint)

        # loop until raid race is done. big try except to catch errors
        now = get_now_with_tz()
        while self.cutoff_time > now:
            try:
                # gets all online users. Returns list with tuples (name, destinyID)
                try:
                    clan_members = await clan.get_clan_members()
                except BackendException:
                    await asyncio.sleep(120)
                    continue

                online: list[DestinyClanMemberModel] = []
                for member in clan_members.members:
                    if member.is_online:
                        online.append(member)

                # loops through all online users and check for completions
                async with create_task_group() as tg:
                    for member in online:
                        tg.start_soon(self._look_for_completion, member)

                # update leaderboard message
                await self._update_leaderboard()

                # save data as pickle
                with open(f"{self.raid_name}_finished_encounters.pickle", "wb") as handle:
                    pickle.dump(self.finished_encounters, handle)
                with open(f"{self.raid_name}_finished_raid.pickle", "wb") as handle:
                    pickle.dump(self.finished_raid, handle)

                # wait 1 min before checking again
                await asyncio.sleep(60)

                # set new now
                now = get_now_with_tz()
                self.ctx.bot.logger_exceptions.debug(f"Done with loop at {str(now)}")

            except Exception as e:
                logger = logging.getLogger("generalExceptions")
                logger.error("An error occurred while I was doing Day1 Stuff", exc_info=e)
                await descend_channels.bot_dev_channel.send(f"An error occurred while I was doing Day1 Stuff: {e}")

                await asyncio.sleep(120)
                continue

        # wait 5 minutes to give last second finishes time to get to the api
        await asyncio.sleep(5 * 60)

        # write the completion message
        embed = embed_message(f"{self.raid_name} - Raid Race Summary", "The raid race is over :(")
        if self.finished_raid:
            embed.description += f"\nBut some clan members managed a completion\n⁣\n{custom_emojis.descend_logo} __**Completions**__ {custom_emojis.descend_logo}"

            # get stats for the raid
            completions: list[tuple[int, DestinyActivityOutputModel]] = []
            failed = []
            for destiny_id, finished_date in self.finished_raid.items():
                backend_activities = DestinyActivities(
                    ctx=None,
                    discord_member=self.destiny_id_translation[destiny_id],
                    discord_guild=self.ctx.guild,
                )

                # get the stats. Check 15min in the future from the finish date, since you can get the triumph while will being in the activity
                try:
                    user_stats = await backend_activities.get_activity_stats(
                        input_model=DestinyActivityInputModel(
                            activity_ids=self.activity_hashes,
                            end_time=finished_date + datetime.timedelta(minutes=15),
                        )
                    )
                    completions.append((destiny_id, user_stats))

                except BackendException:
                    failed.append(destiny_id)

            sorted_completions = sorted(completions, key=lambda completion: completion[1].time_spend, reverse=False)

            # write the fancy text
            for destiny_id, entry in sorted_completions:
                percent = (entry.precision_kills / entry.kills) * 100 if entry.kills else 0
                text = [
                    f"{custom_emojis.enter} Time: **{format_timedelta(seconds=entry.time_spend)}**",
                    f"{custom_emojis.enter} Kills: **{entry.kills}** _({round(percent, 2)}% prec)_",
                    f"{custom_emojis.enter} Assists: **{entry.assists}**",
                    f"{custom_emojis.enter} Deaths: **{entry.deaths}**",
                ]
                embed.add_field(
                    name=self.destiny_id_translation[destiny_id].display_name, value="\n".join(text), inline=True
                )

            for destiny_id in failed:
                embed.add_field(
                    name=self.destiny_id_translation[destiny_id].display_name,
                    value="Sadly there is no information in the api yet",
                    inline=True,
                )

        else:
            embed.description += "\nSadly nobody here finished the raid in time, good luck next time!"

        stats = await self.channel.send(embeds=embed)
        await stats.pin()

    async def _look_for_completion(self, member: DestinyClanMemberModel):
        """Gather all members since it is faster"""

        if member.destiny_id not in self.finished_raid:
            account = DestinyAccount(
                ctx=None,
                discord_member=self.destiny_id_translation[member.destiny_id],
                discord_guild=self.channel.guild,
            )
            completion = await account.has_triumph(triumph_id=self.activity_triumph)

            # check if triumph is earned
            if completion:
                await self._raid_finished(member=member)
            else:
                # loop through the objectives
                for objective in completion.objectives:
                    # abort if user has already completed that encounter
                    if not self.finished_encounters[member.destiny_id][objective.objective_id]:
                        self.finished_encounters[member.destiny_id][objective.objective_id] = True
                        await self.channel.send(
                            f"{custom_emojis.descend_logo} **{self.destiny_id_translation[member.destiny_id].mention}** finished `{self.activity_triumph_encounters[self.activity_triumph][objective.objective_id]}` {custom_emojis.zoom}"
                        )

                        # check if that was the last missing one
                        if all(self.finished_encounters[member.destiny_id].values()):
                            await self._raid_finished(member=member)

            # triumphs are sometimes hidden and not reported in the api. As a fallback, also check fallback triumphs / metrics / emblem
            # check fallback completion triumphs
            if member.destiny_id not in self.finished_raid:
                for triumph_id in self.alternative_activity_triumphs:
                    completion = await account.has_triumph(triumph_id=triumph_id)
                    if completion:
                        await self._raid_finished(member=member)

            # check fallback completion metric
            if member.destiny_id not in self.finished_raid:
                for metric_id in self.activity_metrics:
                    completion = await account.get_metric(metric_id=metric_id)
                    if completion.value > 0:
                        await self._raid_finished(member=member)

            # check fallback completion emblems
            if member.destiny_id not in self.finished_raid:
                for collectible_id in self.emblem_hashes:
                    completion = await account.has_collectible(collectible_id=collectible_id)
                    if completion:
                        await self._raid_finished(member=member)

    async def _raid_finished(self, member: DestinyClanMemberModel | str):
        """Save that the member finished their raid and send a message"""

        # make sure the encounters are marked as completed
        for encounter in self.finished_encounters[member.destiny_id]:
            self.finished_encounters[member.destiny_id][encounter] = True

        self.finished_raid.update({member.destiny_id: get_now_with_tz()})
        await self.channel.send(
            f"{custom_emojis.descend_logo} **{self.destiny_id_translation[member.destiny_id].mention}** finished the raid. Congratulations {custom_emojis.zoom}"
        )

    async def _update_leaderboard(self):
        """Update the leaderboard message"""

        # saving the info by encounter here:
        # {encounter_name: [destiny_id1, ...]}
        running_raid: dict[str, list[int]] = {
            encounter: [] for encounter in self.activity_triumph_encounters[self.activity_triumph].values()
        }

        # loop through clan members
        for member in self.clan_members.members:
            # only check if member did not finish the raid. loop through their encounter completion
            if member.destiny_id not in self.finished_raid:
                for encounter, complete in self.finished_encounters[member.destiny_id].items():
                    if complete:
                        encounter_name = self.activity_triumph_encounters[self.activity_triumph][encounter]
                        running_raid[encounter_name].append(member.destiny_id)

        embed = embed_message(
            "Race for Worlds First",
            "First results are in! These are the current result:",
            "Note: If progress does not show up, the API might not show the info. Nothing I can do :(",
        )
        embed.timestamp = get_now_with_tz()

        if self.finished_raid:
            sorted_finished_members = {
                k: v for k, v in sorted(self.finished_raid.items(), key=lambda item: item[1], reverse=False)
            }

            embed.add_field(
                name=f"{custom_emojis.descend_logo} Finished {custom_emojis.descend_logo}",
                value=", ".join(
                    [
                        f"{name}: {Timestamp.fromdatetime(date).format(style=TimestampStyles.ShortTime)}"
                        for name, date in sorted_finished_members.items()
                    ]
                )
                + f"\n{custom_emojis.tile_left}{custom_emojis.tile_mid}{custom_emojis.tile_mid}{custom_emojis.tile_mid}{custom_emojis.tile_mid}{custom_emojis.tile_mid}{custom_emojis.tile_right}",
                inline=False,
            )

        # add the encounter completion thingy
        for encounter, destiny_ids in running_raid.items():
            if destiny_ids:
                embed.add_field(
                    name=encounter,
                    value=", ".join([self.destiny_id_translation[destiny_id].mention for destiny_id in destiny_ids]),
                    inline=False,
                )

        # only send this if we added fields to the embed
        if len(embed.fields) > 0:
            if not self.leaderboard_msg:
                self.leaderboard_msg = await self.leaderboard_channel.send(embeds=embed)
            else:
                await self.leaderboard_msg.edit(embeds=embed)
