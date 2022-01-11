import dataclasses

from ElevatorBot.backendNetworking.http import BaseBackendConnection
from ElevatorBot.backendNetworking.routes import (
    destiny_collectible_name_route,
    destiny_get_all_lore_route,
    destiny_triumph_name_route,
)
from Shared.NetworkingSchemas import NameModel
from Shared.NetworkingSchemas.destiny import DestinyAllLoreModel


@dataclasses.dataclass
class DestinyItems(BaseBackendConnection):
    async def get_triumph_name(self, triumph_id: int) -> NameModel:
        """Return the triumph name"""

        result = await self._backend_request(
            method="GET",
            route=destiny_triumph_name_route.format(triumph_id=triumph_id),
        )

        # convert to correct pydantic model
        return NameModel.parse_obj(result.result)

    async def get_collectible_name(self, collectible_id: int) -> NameModel:
        """Return the collectible name"""

        result = await self._backend_request(
            method="GET",
            route=destiny_collectible_name_route.format(collectible_id=collectible_id),
        )

        # convert to correct pydantic model
        return NameModel.parse_obj(result.result)

    async def get_all_lore(self) -> DestinyAllLoreModel:
        """Return all lore"""

        result = await self._backend_request(
            method="GET",
            route=destiny_get_all_lore_route,
        )

        # convert to correct pydantic model
        return DestinyAllLoreModel.parse_obj(result.result)
