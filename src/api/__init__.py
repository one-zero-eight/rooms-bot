from src.api.methods import InNoHassleMusicRoomAPI
from src.bot.config import get_settings

client = InNoHassleMusicRoomAPI(get_settings().API_URL, get_settings().API_SECRET)

__all__ = ["client", "InNoHassleMusicRoomAPI"]
