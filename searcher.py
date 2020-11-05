from .. import loader, utils  # pylint: disable=relative-beyond-top-level
from telethon.tl.types import DocumentAttributeFilename
import logging

from youtube_search import YoutubeSearch
from search_engine_parser import GoogleSearch
import json
import io
import requests
logger = logging.getLogger(__name__)
import os
import time
import asyncio
import shutil
from bs4 import BeautifulSoup
import re
from html import unescape
from googleapiclient.discovery import build
from requests import get

from youtube_dl import YoutubeDL
from youtube_dl.utils import (DownloadError, ContentTooShortError,
                              ExtractorError, GeoRestrictedError,
                              MaxDownloadsReached, PostProcessingError,
                              UnavailableVideoError, XAttrMetadataError)
from asyncio import sleep
from userbot import CMD_HELP, BOTLOG, BOTLOG_CHATID, YOUTUBE_API_KEY, CHROME_DRIVER, GOOGLE_CHROME_BIN
from userbot.events import register
from telethon.tl.types import DocumentAttributeAudio
from uniborg.util import progress, humanbytes, time_formatter



@loader.tds
class YTsearchMod(loader.Module):
    strings = {
        "name": "Searcher",
        "search": "⚪⚪⚪\n⚪❓⚪\n⚪⚪⚪",
        "no_reply": "<b>Reply to image or sticker!</b>",
        "result": '<a href="{}"><b>🔴⚪🔴|See</b>\n<b>⚪🔴⚪|Search</b>\n<b>⚪🔴⚪|Results</b></a>',
        "error": '<b>Something went wrong...</b>',
        "no_term": "<b>I can't Google nothing</b>",
        "no_results": "<b>Could not find anything about</b> <code>{}</code> <b>on Google</b>",
        "results": "<b>These came back from a Google search for</b> <code>{}</code>:\n\n",
        "result": "<a href='{}'>{}</a>\n\n<code>{}</code>\n",
    }

    async def client_ready(self, client, db):
        self.client = client

    @loader.unrestricted
    @loader.ratelimit
    async def googlecmd(self, message):
        text = utils.get_args_raw(message.message)
        if not text:
            text = (await message.get_reply_message()).message
        if not text:
            await utils.answer(message, self.strings("no_term", message))
            return
        gsearch = GoogleSearch()
        gresults = await gsearch.async_search(text, 1)
        if not gresults:
            await utils.answer(message, self.strings("no_results", message).format(text))
            return
        msg = ""
        results = zip(gresults["titles"], gresults["links"], gresults["descriptions"])
        for result in results:
            msg += self.strings("result", message).format(utils.escape_html(result[0]), utils.escape_html(result[1]),
                                                          utils.escape_html(result[2]))
        await utils.answer(message, self.strings("results", message).format(utils.escape_html(text)) + msg)

    async def yarscmd(self, message):
        reply = await message.get_reply_message()
        data = await check_media(message, reply)
        if not data:
            await utils.answer(message, self.strings("no_reply", message))
            return
        await utils.answer(message, self.strings("search", message))
        searchUrl = 'https://yandex.ru/images/search'
        files = {'upfile': ('blob', data, 'image/jpeg')}
        params = {'rpt': 'imageview', 'format': 'json',
                  'request': '{"blocks":[{"block":"b-page_type_search-by-image__link"}]}'}
        response = requests.post(searchUrl, params=params, files=files)
        if response.ok:
            query_string = json.loads(response.content)['blocks'][0]['params']['url']
            link = searchUrl + '?' + query_string
            text = self.strings("result", message).format(link)
            await utils.answer(message, text)
        else:
            await utils.answer(message, self.strings("error", message))

async def check_media(message, reply):
    if reply and reply.media:
        if reply.photo:
            data = reply.photo
        elif reply.document:
            if reply.gif or reply.video or reply.audio or reply.voice:
                return None
            data = reply.media.document
        else:
            return None
    else:
        return None
    if not data or data is None:
        return None
    else:
        data = await message.client.download_file(data, bytes)
        img = io.BytesIO(data)
        return img