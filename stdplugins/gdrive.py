"""
GDrive Client Module for Userbot

Usage:- .drivesearch search_query
        .drivedl drive_link
        .gdrive filePath/replyToMessage

Author:- Git: github.com/jaskaranSM | Tg:  https://t.me/Zero_cool7870
"""


import asyncio
import aiohttp
from gaggle import Client
from oauth2client.client import OAuth2WebServerFlow
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from telethon import events
from urllib.parse import parse_qs
from uniborg.util import humanbytes, admin_cmd, progress
from datetime import datetime
import time
import urllib.parse as urlparse
import pickle
import mimetypes
import os
import re


db = mongo_client["test"]
G_DRIVE_TOKEN_FILE = "token.pickle"
driveDB = db.GDRIVE 

def getAccessTokenDB():
    cursor = driveDB.find()
    for c in cursor:
        return c.get("access_token")
    return {"access_token":b""}

def saveAccessTokenDB(token): #bytes
    print("Updating Access Token in Database")
    previousToken = getAccessTokenDB()
    driveDB.update_one(previousToken,{'$set':{"access_token":token}},upsert=True)

def InitGDrive():
    if not os.path.exists(G_DRIVE_TOKEN_FILE):
        print("Fetching Access Token from Database")
        token = getAccessTokenDB()
        if len(token) == 0:
            return
        with open(G_DRIVE_TOKEN_FILE,"wb") as f:
            f.write(token)
InitGDrive()

class GDriveHelper:
    def __init__(self):
        self.service = None
        self.session = aiohttp.ClientSession()
        self.SCOPES = ['https://www.googleapis.com/auth/drive']
        self.G_DRIVE_DIR_MIME_TYPE = "application/vnd.google-apps.folder"
        self.__REDIRECT_URI = "urn:ietf:wg:oauth:2.0:oob"
        self.__G_DRIVE_BASE_DOWNLOAD_URL = "https://drive.google.com/uc?id={}&export=download"
        self.__G_DRIVE_DIR_BASE_DOWNLOAD_URL = "https://drive.google.com/drive/folders/{}"
        self.chunksize = 50*1024*1024

    async def getCreds(self,event=None):
        credentials = None
        if os.path.exists(G_DRIVE_TOKEN_FILE):
            with open(G_DRIVE_TOKEN_FILE, 'rb') as f:
                credentials = pickle.load(f)
        if credentials is None or credentials.invalid:
            if credentials and credentials.access_token_expired and credentials.refresh_token:
                credentials.refresh(Request())
                with open(G_DRIVE_TOKEN_FILE,"rb") as token:
                    saveAccessTokenDB(token.read())
            else:
                flow = OAuth2WebServerFlow(
                    Config.G_DRIVE_CLIENT_ID,
                    Config.G_DRIVE_CLIENT_SECRET,
                    self.SCOPES,
                    redirect_uri=self.__REDIRECT_URI
                )
                authorize_url = flow.step1_get_authorize_url()
                code = ""
                print(authorize_url)
                if event:
                    async with event.client.conversation(Config.PRIVATE_GROUP_BOT_API_ID) as conv:
                        await conv.send_message(f"Go to the following link in your browser: {authorize_url} and reply the code")
                        response = conv.wait_event(events.NewMessage(
                            outgoing=True,
                            chats=Config.PRIVATE_GROUP_BOT_API_ID
                        ))
                        response = await response
                        code = response.message.message.strip()
                else:
                    code = input("Enter CODE: ")
                credentials = flow.step2_exchange(code)
                credentials.token = credentials.access_token
                with open(G_DRIVE_TOKEN_FILE, 'wb') as token:
                    pickle.dump(credentials, token)
                with open(G_DRIVE_TOKEN_FILE,"rb") as token:
                    saveAccessTokenDB(token.read())
        return credentials

    async def authorize(self,event=None):
        creds = await self.getCreds(event)
        self.service = Client(session=self.session,token=creds.access_token,refresh_token=creds.refresh_token,id_token=creds.id_token,token_uri=creds.token_uri,client_id=creds.client_id,client_secret=creds.client_secret).drive("v3")

    def getFileOps(self,file_path):
        mime_type = mimetypes.guess_type(file_path)[0]
        mime_type = mime_type if mime_type else "text/plain"
        file_name = file_path.rsplit("/",1)[-1]
        return file_name,mime_type

    async def setPermissions(self,file_id):
        permissions = {
            'role': 'reader',
            'type': 'anyone',
            'value': None,
            'withLink': True
        }
        return await self.service.permissions.create(supportsTeamDrives=True, fileId=file_id, body=permissions)

    async def uploadFile(self,file_path,parent_id=None):
        file_name, mime_type = self.getFileOps(file_path)
        file_metadata = {
            'name': file_name,
            'description': 'userbot',
            'mimeType': mime_type,
        }
        if parent_id is not None:
            file_metadata['parents'] = [parent_id]

        media_body = MediaFileUpload(file_path,
                                     mimetype=mime_type,
                                     chunksize=self.chunksize)
        response = await self.service.files.create(supportsTeamDrives=True,
                                                   body=file_metadata, media_body=media_body)
        
        resJson = await response.json()
        if not Config.IS_TEAM_DRIVE:
            await self.setPermissions(resJson.get('id')) 
        return resJson.get("id")

    async def createDirectory(self,directory_name,parent_id=None):
        file_metadata = {
            "name": directory_name,
            "mimeType": self.G_DRIVE_DIR_MIME_TYPE
        }
        if parent_id is not None:
            file_metadata["parents"] = [parent_id]
        response = await self.service.files.create(supportsTeamDrives=True,
                                                   body=file_metadata)
        
        resJson = await response.json()
        if not Config.IS_TEAM_DRIVE:
            await self.setPermissions(resJson.get('id')) 
        return resJson.get("id")

    async def uploadFolder(self,input_directory,folder_id=None):
        files = os.listdir(input_directory)
        if len(files) == 0:
            return None
        for file in files:
            absPath = os.path.join(input_directory,file)
            if os.path.isdir(absPath):
                newDir = await self.createDirectory(file,folder_id)
                await self.uploadFolder(absPath,newDir)
            else:
                await self.uploadFile(absPath,folder_id)

    def formatLink(self,id,folder=True):
        if folder:
            return self.__G_DRIVE_DIR_BASE_DOWNLOAD_URL.format(id)
        return self.__G_DRIVE_BASE_DOWNLOAD_URL.format(id)

    def parseLink(self,link):
        if "folders" in link or "file" in link:
            regex = r"https://drive\.google\.com/(drive)?/?u?/?\d?/?(mobile)?/?(file)?(folders)?/?d?/([-\w]+)[?+]?/?(w+)?"
            res = re.search(regex,link)
            if res is None:
                raise IndexError("GDrive ID not found.")
            return res.group(5)
        parsed = urlparse.urlparse(link)
        return parse_qs(parsed.query)['id'][0]

    async def downloadFolder(self,folder_id,local_path):
        files = await self.getFilesByParentId(folder_id)
        for file in files:
            newPath = os.path.join(local_path,file.get("name"))
            if file.get("mimeType") == self.G_DRIVE_DIR_MIME_TYPE:
                os.makedirs(newPath,exist_ok=True)
                await self.downloadFolder(file.get("id"),newPath)
            else:
                await self.downloadFile(file.get("id"),newPath)

    async def getAccessToken(self):
        return (await self.getCreds()).access_token

    def getFileName(self,file_path):
        return file_path.rsplit("/",1)[-1]

    async def getMetadata(self,file_id):
        file_metadata = await self.service.files.get(supportsAllDrives=True,fileId=file_id,fields="*")
        return await file_metadata.json()

    async def downloadFile(self,file_id,file_path):
        uri = f"https://www.googleapis.com/drive/v3/files/{file_id}"
        access_token = await self.getAccessToken()
        queryString = {
            "includeItemsFromAllDrives": "true",
            "supportsAllDrives": "true",
            "alt": 'media',
            "includeTeamDriveItems":"true"
        }
        headers = {"accept-encoding":'gzip;q=0,deflate,sdch','authorization': f'Bearer {access_token}'}
        response = await self.session.get(uri,params=queryString,headers=headers)
        with open(file_path,"wb") as file_writer:
            async for chunk, _ in response.content.iter_chunks():
                file_writer.write(chunk)
                file_writer.flush()

    async def getFilesByParentId(self,folder_id,name=None,limit=None):
        files = []
        page_token = None
        if name:
            query =f"'{folder_id}' in parents and (name contains '{name}')"
        else:
            query =f"'{folder_id}' in parents"
        while True:
            response = await self.service.files.list(supportsAllDrives=True,
                                                   includeTeamDriveItems=True,
                                                   q=query,
                                                   fields='nextPageToken, files(id, name, mimeType, size, iconLink)',
                                                   pageToken=page_token,
                                                   pageSize=500,
                                                   orderBy='folder,name,modifiedTime desc')
            response = await response.json()
            for file in response.get('files', []):
                if limit and len(files) == limit:
                    return files
                files.append(file)
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break
        return files

@borg.on(admin_cmd(pattern="drivesearch ?(.*)", allow_sudo=True))
async def drivesch(event):
    if event.fwd_from:
        return
    input_str = event.pattern_match.group(1).strip()
    drive = GDriveHelper()
    await drive.authorize(event)
    files = await drive.getFilesByParentId(Config.GDRIVE_FOLDER_ID,input_str,20)
    msg = f"**G-Drive Search Query**\n`{input_str}`\n**Results**\n"
    for file in files:
        if file.get("mimeType") == drive.G_DRIVE_DIR_MIME_TYPE:
            msg +="⁍ [{}]({}) (folder)".format(file.get('name'),drive.formatLink(file.get('id')))+"\n"
        else:
            msg += "⁍ [{}]({}) ({})".format(file.get('name'),drive.formatLink(file.get('id'),folder=False),humanbytes(int(file.get('size'))))+"\n"
    await event.edit(msg)


@borg.on(admin_cmd(pattern="drivedl ?(.*)", allow_sudo=True))
async def gdriveupload(event):
    if event.fwd_from:
        return
    input_link = event.pattern_match.group(1)
    if not input_link:
        await event.edit("Provide Link kek.")
        return
    mone = await event.reply("Processing...")
    drive = GDriveHelper()
    await drive.authorize(event)
    file_id = drive.parseLink(input_link)
    meta = await drive.getMetadata(file_id)
    if meta.get("mimeType") == drive.G_DRIVE_DIR_MIME_TYPE:
        os.makedirs(meta.get("name"),exist_ok=True)
        await drive.downloadFolder(meta.get("id"),meta.get("name"))
    else:
        await drive.downloadFile(meta.get('id'),meta.get('name'))
    await mone.edit(f"Downloaded: `{meta.get('name')}`")

@borg.on(admin_cmd(pattern="gdrive ?(.*)", allow_sudo=True))
async def gdriveupload(event):
    if event.fwd_from:
        return
    mone = await event.reply("Processing ...")
    if Config.G_DRIVE_CLIENT_ID is None or Config.G_DRIVE_CLIENT_SECRET is None:
        await mone.edit("This module requires credentials from https://da.gd/so63O. Aborting!")
        return False
    input_str = event.pattern_match.group(1)
    if not os.path.isdir(Config.TMP_DOWNLOAD_DIRECTORY):
        os.makedirs(Config.TMP_DOWNLOAD_DIRECTORY)
    required_file_name = None
    start = datetime.now()
    if event.reply_to_msg_id and not input_str:
        reply_message = await event.get_reply_message()
        try:
            c_time = time.time()
            downloaded_file_name = await borg.download_media(
                reply_message,
                Config.TMP_DOWNLOAD_DIRECTORY,
                progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                    progress(d, t, mone, c_time, "trying to download")
                )
            )
        except Exception as e:  # pylint:disable=C0103,W0703
            await mone.edit(str(e))
            return False
        else:
            end = datetime.now()
            ms = (end - start).seconds
            required_file_name = downloaded_file_name
            await mone.edit("Downloaded to `{}` in {} seconds.".format(downloaded_file_name, ms))
    elif input_str:
        input_str = input_str.strip()
        if os.path.exists(input_str):
            end = datetime.now()
            ms = (end - start).seconds
            required_file_name = input_str
            await mone.edit("Found `{}` in {} seconds.".format(input_str, ms))
        else:
            await mone.edit("File Not found in local server. Give me a file path :((")
            return False
    if required_file_name:
        link = ""
        drive = GDriveHelper()
        await drive.authorize(event)
        if os.path.isdir(required_file_name):
            dir_id = await drive.createDirectory(drive.getFileName(required_file_name),Config.GDRIVE_FOLDER_ID)
            await drive.uploadFolder(required_file_name,dir_id)
            link = drive.formatLink(dir_id)
        else:
            file_id = await drive.uploadFile(required_file_name,Config.GDRIVE_FOLDER_ID)
            link = drive.formatLink(file_id,folder=False)
        await mone.edit(f"Uploaded To GDrive: [{required_file_name}]({link})")
    else:
        await mone.edit("File Not found in local server. Give me a file path :((")
