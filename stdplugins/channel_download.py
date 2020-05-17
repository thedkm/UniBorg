"""
Telegram Channel Media Downloader Plugin for userbot.
usage: .geta channel_username [will  get all media from channel, tho there is limit of 3000 there to prevent API limits.]
By: @Zero_cool7870
"""
from telethon import events, errors
import asyncio
import os
from uniborg.util import admin_cmd

directory= "./temp/"
             
@borg.on(admin_cmd(pattern="geta ?(.*)", allow_sudo=True))
async def get_media(event):
    if event.fwd_from:
        return
    count = 0
    os.makedirs(directory,exist_ok=True)
    channel = event.pattern_match.group(1)
    try:
        channel = int(channel)
    except ValueError:
        pass
    await event.edit("Downloading All Media From this Channel.")
    msgs = await borg.get_messages(channel,limit=3000)
    for msg in msgs:
       if msg.media is not None:
            try:
               await borg.download_media(msg,directory)     
               count += 1     
            except errors.FloodWaitError as e:
                await asyncio.sleep(e.seconds)
    await event.edit(f"Downloaded {count} files.")
             
             
             
