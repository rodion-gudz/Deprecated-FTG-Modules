# -*- coding: utf-8 -*-

# Module author: Official Repo, @GovnoCodules

# requires: search-engine-parser>=0.6.2 youtube_search

from .. import loader, utils
import json
import io
import requests
from PIL import Image
import random
import string
from youtube_search import YoutubeSearch
import logging
from search_engine_parser import GoogleSearch

logger = logging.getLogger(__name__)


@loader.tds
class SearchMod(loader.Module):
    """Reverse image search via Yandex Images"""
    strings = {"name": "Search",
               "search": "⚪⚪⚪\n⚪❓⚪\n⚪⚪⚪",
               "no_reply": "<b>Reply to image or sticker!</b>",
               "ya_result": '<a href="{}"><b>🔴⚪🔴|See</b>\n<b>⚪🔴⚪|Search</b>\n<b>⚪🔴⚪|Results</b></a>',
               "error": '<b>Something went wrong...</b>',
               "no_term": "<b>I can't Google nothing</b>",
               "no_results": "<b>Could not find anything about</b> <code>{}</code> <b>on Google</b>",
               "results": "<b>These came back from a Google search for</b> <code>{}</code>:\n\n",
               "result": "<a href='{}'>{}</a>\n\n<code>{}</code>\n"
               }

    @loader.owner
    async def yarscmd(self, message):
        """.yars <repy to image>"""
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
            text = self.strings("ya_result", message).format(link)
            await utils.answer(message, text)
        else:
            await utils.answer(message, self.strings("error", message))

    async def googlecmd(self, message):
        """Shows Google search results."""
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

    async def ytscmd(self, message):
        """Youtube Searcher"""
        text = utils.get_args_raw(message)
        if not text:
            reply = await message.get_reply_message()
            if not reply:
                await message.delete()
                return
            text = reply.raw_text
        results = YoutubeSearch(text, max_results=10).to_dict()
        out = f'Найдено по запросу: {text}'
        for r in results:
            out += f'\n\n<a href="https://www.youtube.com/{r["link"]}">{r["title"]}</a>'

        await message.edit(out)


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

