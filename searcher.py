from .. import loader, utils  # pylint: disable=relative-beyond-top-level
from telethon.tl.types import DocumentAttributeFilename
import logging

from search_engine_parser import GoogleSearch
import json
import io
import requests
logger = logging.getLogger(__name__)
import asyncurban
from .. import loader, utils

import logging
import lyricsgenius



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
        "provide_word": "<b>Provide a word(s) to define.</b>",
        "def_error": "<b>Couldn't find definition for that.</b>",
        "resulta": "<b>Text</b>: <code>{}</code>\n<b>Meaning</b>: <code>{}\n<b>Example</b>: <code>{}</code>",
        "genius_api_token_doc": "The LyricsGenius API token from http://genius.com/api-clients",
        "invalid_syntax": "<b>Please specify song and artist.</b>",
        "song_not_found": "<b>Song not found</b>",
        "missing_token": "<b>API Token missing</b>"
    }

    async def client_ready(self, client, db):
        self.client = client

    def __init__(self):
        self.urban = asyncurban.UrbanDictionary()
        self.config = loader.ModuleConfig("GENIUS_API_TOKEN", None, lambda m: self.strings("genius_api_token_doc", m))

    def config_complete(self):
        if self.config["GENIUS_API_TOKEN"]:
            self.genius = lyricsgenius.Genius(self.config["GENIUS_API_TOKEN"])
        else:
            self.genius = None

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

    async def urbancmd(self, message):
        args = utils.get_args_raw(message)

        if not args:
            return await utils.answer(message, self.strings("provide_word", message))

        try:
            definition = await self.urban.get_word(args)
        except asyncurban.WordNotFoundError:
            return await utils.answer(message, self.strings("def_error", message))
        result = self.strings("resulta", message).format(definition.word, definition.definition, definition.example)
        await utils.answer(message, result)

    @loader.unrestricted
    @loader.ratelimit
    async def lyricscmd(self, message):
        if self.genius is None:
            await utils.answer(message, self.strings("missing_token", message))
        args = utils.get_args_split_by(message, ",")
        if len(args) != 2:
            logger.debug(args)
            await utils.answer(message, self.strings("invalid_syntax", message))
            return
        logger.debug("getting song lyrics for " + args[0] + ", " + args[1])
        try:
            song = await utils.run_sync(self.genius.search_song, args[0], args[1])
        except TypeError:
            # Song not found causes internal library error
            song = None
        if song is None:
            await utils.answer(message, self.strings("song_not_found", message))
            return
        logger.debug(song)
        logger.debug(song.lyrics)
        await utils.answer(message, utils.escape_html(song.lyrics))


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