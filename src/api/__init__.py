import os

from src.api.methods import InNoHassleMusicRoomAPI


client = InNoHassleMusicRoomAPI(os.getenv("API_URL"), os.getenv("API_SECRET"))

__all__ = ["client", "InNoHassleMusicRoomAPI"]
