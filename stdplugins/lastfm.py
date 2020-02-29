"""
LastFM Module for Userbot
usage:- .current <userName> if no userName is provided in args. env LAST_FM_USERNAME will be used.
By:- TG:- @Zero_cool7870 Git:- jaskaranSM

"""
from pylast import LastFMNetwork
import asyncio
from uniborg.util import admin_cmd



@borg.on(admin_cmd(pattern="current ?(.*)", allow_sudo=True))
async def lastfm(event):
    if event.fwd_from:
        return
    username = event.pattern_match.group(1)
    if Config.LAST_FM_API_KEY is None:
        await event.edit("`Setup LAST_FM_API_KEY first.`")
        return 
    if username is None and Config.LAST_FM_USERNAME is None:
        await event.edit("`Setup LAST_FM_USERNAME or Provide username first.`")
        return
    if not username:
        username = Config.LAST_FM_USERNAME
    network = LastFMNetwork(api_key=Config.LAST_FM_API_KEY)
    user = network.get_user(username)
    current_track = user.get_now_playing()
    if current_track:
        try:
            track_cover = current_track.get_cover_image()
        except IndexError:
            track_cover = None
            pass
        msg = "**{}** is currently listening to:\n [🎧]({}) `{}`".format(user,track_cover,current_track)
    else:
        msg = "**{}** was listening to:\n".format(username)
        recent_tracks = user.get_recent_tracks(limit=3)
        for played_track in recent_tracks:
            msg += "🎧 `{}`\n".format(played_track.track)
    await event.delete()
    await borg.send_message(event.chat_id,msg,link_preview=True)
