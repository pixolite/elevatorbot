from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice

from functions.formating import embed_message
from functions.persistentMessages import make_persistent_message, steamJoinCodeMessage
from static.config import GUILD_IDS
from static.globals import among_us_emoji_id, barotrauma_emoji_id, gta_emoji_id, valorant_emoji_id, lol_emoji_id, \
    eft_emoji_id, destiny_emoji_id, other_game_roles, clan_join_request


class AdminCommands(commands.Cog):
    def __init__(self, client):
        self.client = client


class PersistentMessagesCommands(commands.Cog):
    def __init__(self, client):
        self.client = client

    # todo permissions
    @cog_ext.cog_slash(
        name="channel",
        description="[Admin] Make new / replace old persistent messages",
        options=[
            create_option(
                name="channel_type",
                description="The type of the channel",
                option_type=3,
                required=True,
                choices=[
                    create_choice(
                        name="Clan Join Request",
                        value="clanjoinrequest"
                    ),
                    create_choice(
                        name="Other Game Roles",
                        value="othergameroles"
                    ),
                    create_choice(
                        name="Steam Join Codes",
                        value="steamjoincodes"
                    ),
                    create_choice(
                        name="Tournament",
                        value="tournament"
                    ),
                    create_choice(
                        name="Member Count",
                        value="membercount"
                    ),
                    create_choice(
                        name="Booster Count",
                        value="boostercount"
                    ),
                ],
            ),
             create_option(
                 name="channel",
                 description="Which channel to the message should be in",
                 option_type=7,
                 required=True
             )
         ],
    )
    async def _channel(self, ctx: SlashContext, channel_type, channel):
        if channel_type == "othergameroles":
            embed = embed_message(
                f'Other Game Roles',
                f'React to add / remove other game roles'
            )

            # react with those please thanks
            emoji_id_list = []
            for emoji_id, _ in other_game_roles:
                emoji_id_list.append(emoji_id)

            await make_persistent_message(self.client, "otherGameRoles", ctx.guild.id, channel.id, reaction_id_list=emoji_id_list, message_embed=embed)

            await ctx.send(hidden=True, embed=embed_message(
                f"Success",
                f"I've done as you asked"
            ))


        elif channel_type == "clanjoinrequest":
            embed = embed_message(
                f'Clan Application',
                f'React if you want to join the clan'
            )

            await make_persistent_message(self.client, "clanJoinRequest", ctx.guild.id, channel.id,
                                          reaction_id_list=clan_join_request, message_embed=embed)

            await ctx.send(hidden=True, embed=embed_message(
                f"Success",
                f"I've done as you asked"
            ))


        elif channel_type == "steamjoincodes":
            await make_persistent_message(self.client, "steamJoinCodes", ctx.guild.id, channel.id, message_text="...")

            # fill the empty message
            await steamJoinCodeMessage(self.client, ctx.guild)

            await ctx.send(hidden=True, embed=embed_message(
                f"Success",
                f"I've done as you asked"
            ))


        elif channel_type == "tournament":
            text = """
<:desc_title_left_b:768906489309822987><:desc_title_right_b:768906489729122344> **Welcome to the Tournament Channel!** <:desc_title_left_b:768906489309822987><:desc_title_mid_b:768906489103384657><:desc_title_mid_b:768906489103384657><:desc_title_right_b:768906489729122344>
⁣
On your command, I can start a private PvP tournament for all the masochist in the clan. You decide on details, such as rules, maps classes or anything else.
⁣
⁣
<:desc_title_left_b:768906489309822987><:desc_title_right_b:768906489729122344> **Tutorial** <:desc_title_left_b:768906489309822987> <:desc_title_mid_b:768906489103384657><:desc_title_mid_b:768906489103384657><:desc_title_right_b:768906489729122344>
:desc_circle_b: Create the tournament by using `/tournament create`. This will make a new message appear in this channel, to join the tournament, simply react to it.
:desc_circle_b: Once everyone has signed up use `/tournament start` to start the tournament. I will generate a random bracket and assign player to games.
:desc_circle_b: Now you need to start a custom game with only the two chosen players in it and **finish it**. I will automatically detect the winner. Last man standing wins it all!
⁣
⁣"""

            await make_persistent_message(self.client, "tournamentChannel", ctx.guild.id, channel.id, message_text=text)

            await ctx.send(hidden=True, embed=embed_message(
                f"Success",
                f"I've done as you asked"
            ))


        elif channel_type == "membercount":
            await make_persistent_message(self.client, "memberCount", ctx.guild.id, channel.id, no_message=True)
            await ctx.send(hidden=True, embed=embed_message(
                f"Success",
                f"I've done as you asked"
            ))


        elif channel_type == "boostercount":
            await make_persistent_message(self.client, "boosterCount", ctx.guild.id, channel.id, no_message=True)
            await ctx.send(hidden=True, embed=embed_message(
                f"Success",
                f"I've done as you asked"
            ))


def setup(client):
    client.add_cog(AdminCommands(client))
    # todo enable when persmissions are implemented
    # client.add_cog(PersistentMessagesCommands(client))
