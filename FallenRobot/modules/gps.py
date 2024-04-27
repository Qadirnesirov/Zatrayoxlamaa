from geopy.geocoders import Nominatim
from telethon import *
from telethon.tl import *

from FallenRobot import *
from FallenRobot import telethn as tbot
from FallenRobot.events import register

GMAPS_LOC = "https://maps.googleapis.com/maps/api/geocode/json"


@register(pattern="^/gps (.*)")
async def _(event):
    args = event.pattern_match.group(1)

    try:
        geolocator = Nominatim(user_agent="Zatrabot")
        geoloc = geolocator.geocode(args)
        gm = f"https://www.google.com/maps/search/{geoloc.latitude},{geoloc.longitude}"
        await tbot.send_file(
            event.chat_id,
            file=types.InputMediaGeoPoint(
                types.InputGeoPoint(float(geoloc.latitude), float(geoloc.longitude))
            ),
        )
        await event.reply(
            f"İlə aç : [🌏Google xəritələri]({gm})",
            link_preview=False,
        )
    except:
        await event.reply("Mən bunu tapa bilmirəm")


__help__ = """
Sizə verilən sorğunun GPS yerini göndərir...

 ❍ /gps <location> *:* GPS məkanını əldə edin.
"""

__mod_name__ = "Gᴘs"
