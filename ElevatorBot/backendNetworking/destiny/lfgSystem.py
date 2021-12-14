import dataclasses
from typing import Optional

from dis_snek.models import Guild, Member

from ElevatorBot.backendNetworking.http import BaseBackendConnection
from ElevatorBot.backendNetworking.routes import (
    destiny_lfg_create_route,
    destiny_lfg_delete_all_route,
    destiny_lfg_delete_route,
    destiny_lfg_get_all_route,
    destiny_lfg_get_route,
    destiny_lfg_update_route,
    destiny_lfg_user_get_all_route,
)
from ElevatorBot.core.destiny.lfg.scheduledEvents import delete_lfg_scheduled_events
from ElevatorBot.elevator import ElevatorSnake
from NetworkingSchemas.destiny.lfgSystem import (
    AllLfgDeleteOutputModel,
    AllLfgOutputModel,
    LfgCreateInputModel,
    LfgOutputModel,
    LfgUpdateInputModel,
    UserAllLfgOutputModel,
)


@dataclasses.dataclass
class DestinyLfgSystem(BaseBackendConnection):
    client: ElevatorSnake
    discord_guild: Optional[Guild]
    discord_member: Member = dataclasses.field(init=False, default=None)

    async def get_all(self) -> Optional[AllLfgOutputModel]:
        """Gets all the lfg events and info belonging to the guild"""

        result = await self._backend_request(
            method="GET",
            route=destiny_lfg_get_all_route.format(guild_id=self.discord_guild.id),
        )

        # convert to correct pydantic model
        return AllLfgOutputModel.parse_obj(result.result) if result else None

    async def get(self, lfg_id: int) -> Optional[LfgOutputModel]:
        """Gets the lfg info belonging to the lfg id and guild"""

        result = await self._backend_request(
            method="GET",
            route=destiny_lfg_get_route.format(guild_id=self.discord_guild.id, lfg_id=lfg_id),
        )

        # convert to correct pydantic model
        return LfgOutputModel.parse_obj(result.result) if result else None

    async def user_get_all(self, discord_member: Member) -> Optional[UserAllLfgOutputModel]:
        """Gets the lfg infos belonging to the discord_id"""

        result = await self._backend_request(
            method="GET",
            route=destiny_lfg_user_get_all_route.format(guild_id=self.discord_guild.id, discord_id=discord_member.id),
        )

        # convert to correct pydantic model
        return UserAllLfgOutputModel.parse_obj(result.result) if result else None

    async def update(
        self,
        lfg_id: int,
        discord_member_id: int,
        lfg_data: LfgUpdateInputModel,
    ) -> Optional[LfgOutputModel]:
        """Updates the lfg info belonging to the lfg id and guild"""

        result = await self._backend_request(
            method="POST",
            route=destiny_lfg_update_route.format(
                guild_id=self.discord_guild.id, discord_id=discord_member_id, lfg_id=lfg_id
            ),
            data=lfg_data.dict(),
        )

        # convert to correct pydantic model
        return LfgOutputModel.parse_obj(result.result) if result else None

    async def create(self, discord_member: Member, lfg_data: LfgCreateInputModel) -> Optional[LfgOutputModel]:
        """Inserts the lfg info and gives it a new id"""

        result = await self._backend_request(
            method="POST",
            route=destiny_lfg_create_route.format(guild_id=self.discord_guild.id, discord_id=discord_member.id),
            data=lfg_data.dict(),
        )

        # convert to correct pydantic model
        return LfgOutputModel.parse_obj(result.result) if result else None

    async def delete(self, discord_member_id: int, lfg_id: int) -> bool:
        """Delete the lfg info belonging to the lfg id and guild"""

        result = await self._backend_request(
            method="DELETE",
            route=destiny_lfg_delete_route.format(
                guild_id=self.discord_guild.id, discord_id=discord_member_id, lfg_id=lfg_id
            ),
        )

        # returns EmptyResponseModel
        return True if result else None

    async def delete_all(self, client: ElevatorSnake, guild_id: int) -> Optional[AllLfgDeleteOutputModel]:
        """Delete the lfg info belonging to the lfg id and guild"""

        result = await self._backend_request(
            method="DELETE",
            route=destiny_lfg_delete_all_route.format(guild_id=guild_id),
        )

        # convert to correct pydantic model
        model = AllLfgDeleteOutputModel.parse_obj(result.result) if result else None

        if model:
            delete_lfg_scheduled_events(event_scheduler=client.scheduler, event_ids=model.event_ids)

        return model
