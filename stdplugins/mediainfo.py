import os
import shlex
import asyncio
from typing import Tuple, List, Optional
from uniborg.util import yaml_format, humanbytes, admin_cmd
from telethon import events
from html_telegraph_poster import TelegraphPoster


async def runcmd(cmd: str) -> Tuple[str, str, int, int]:
    args = shlex.split(cmd)
    process = await asyncio.create_subprocess_exec(
        *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return (
        stdout.decode("utf-8", "replace").strip(),
        stderr.decode("utf-8", "replace").strip(),
        process.returncode,
        process.pid,
    )

async def post_to_telegraph(page_title, html_format_content):
    post_client = TelegraphPoster(use_api=True)
    auth_name = "@UniBorg"
    post_client.create_api_token(auth_name)
    post_page = post_client.post(
        title=page_title,
        author=auth_name,
        author_url="https://t.me/UniBorg",
        text=html_format_content
    )
    return post_page['url']

async def file_data(reply):
    hmm = ""
    if reply.file.name:
        hmm += f"Name  :  {reply.file.name}<br>"
    if reply.file.mime_type:
        hmm += f"Mime type  :  {reply.file.mime_type}<br>"
    if reply.file.size:
        hmm += f"Size  :  {humanbytes(reply.file.size)}<br>"
    if reply.date:
        hmm += f"Date  :  {yaml_format(reply.date)}<br>"
    if reply.file.id:
        hmm += f"Id  :  {reply.file.id}<br>"
    if reply.file.ext:
        hmm += f"Extension  :  '{reply.file.ext}'<br>"
    if reply.file.emoji:
        hmm += f"Emoji  :  {reply.file.emoji}<br>"
    if reply.file.title:
        hmm += f"Title  :  {reply.file.title}<br>"
    if reply.file.performer:
        hmm += f"Performer  :  {reply.file.performer}<br>"
    if reply.file.duration:
        hmm += f"Duration  :  {reply.file.duration} seconds<br>"
    if reply.file.height:
        hmm += f"Height :  {reply.file.height}<br>"
    if reply.file.width:
        hmm += f"Width  :  {reply.file.width}<br>"
    if reply.file.sticker_set:
        hmm += f"Sticker set  :\
            \n {yaml_format(reply.file.sticker_set)}<br>"
    try:
        if reply.media.document.thumbs:
            hmm += f"Thumb  :\
                \n {yaml_format(reply.media.document.thumbs[-1])}<br>"
    except:
        pass
    return hmm

@borg.on(admin_cmd(pattern="mediainfo", allow_sudo=True))
async def _(event):
    X_MEDIA = None
    reply = await event.get_reply_message()
    if not reply.media:
        await event.edit("reply to media first")
        return
    await event.edit("`Processing ...`")
    X_MEDIA = reply.file.mime_type
    if not X_MEDIA:
        return await event.edit("Reply To a Vaild Media Format")
    if X_MEDIA.startswith(("text")):
        return await event.edit("Reply To a Vaild Media Format")
    hmm = await file_data(reply)
    file_path = await reply.download_media(Config.TMP_DOWNLOAD_DIRECTORY)
    out, err, ret, pid = await runcmd(f"mediainfo '{file_path}'")
    if not out:
        out = "Not Supported"
    body_text = f"""
<h2>JSON</h2>
<code>
{hmm}
</code>
<h2>DETAILS</h2>
<code>
{out} 
</code>"""
    link = await post_to_telegraph(f"{X_MEDIA}", body_text)
    await event.edit(f"ℹ️  <b>MEDIA INFO:  <a href ='{link}' > {X_MEDIA}</a></b>", parse_mode="HTML",link_preview=True)
    os.remove(file_path)
