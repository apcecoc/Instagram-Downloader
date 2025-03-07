import aiohttp
import hashlib
import os
from telethon.tl.types import Message
from .. import loader, utils

__version__ = (1, 0, 2)

#       █████  ██████   ██████ ███████  ██████  ██████   ██████ 
#       ██   ██ ██   ██ ██      ██      ██      ██    ██ ██      
#       ███████ ██████  ██      █████   ██      ██    ██ ██      
#       ██   ██ ██      ██      ██      ██      ██    ██ ██      
#       ██   ██ ██       ██████ ███████  ██████  ██████   ██████
#
#              © Copyright 2025
#           https://t.me/apcecoc
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta developer: @apcecoc
# scope: hikka_only
# scope: hikka_min 1.2.10

@loader.tds
class InstagramDownloaderMod(loader.Module):
    """Instagram Downloader for downloading multiple videos"""

    strings = {
        "name": "InstagramDownloader",
        "processing": "🔄 <b>Processing your request...</b>",
        "invalid_url": "🚫 <b>Invalid Instagram URL. Please check the link and try again.</b>",
        "error": "❌ <b>An error occurred while fetching the content. Try again later.</b>",
        "success": "✅ <b>Content downloaded successfully:</b>",
    }

    strings_ru = {
        "processing": "🔄 <b>Обработка вашего запроса...</b>",
        "invalid_url": "🚫 <b>Неверная ссылка Instagram. Проверьте и попробуйте снова.</b>",
        "error": "❌ <b>Произошла ошибка при получении контента. Повторите попытку позже.</b>",
        "success": "✅ <b>Контент успешно загружен:</b>",
        "_cls_doc": "Скачивание видео с Instagram",
    }

    @loader.command(ru_doc="<Ссылка> Скачать видео с Instagram")
    async def igdl(self, message: Message):
        """<URL> Download Instagram content"""
        url = utils.get_args_raw(message)
        if not url or not url.startswith("http"):
            await utils.answer(message, self.strings("invalid_url"))
            return

        await utils.answer(message, self.strings("processing"))

        api_url = "https://api.paxsenix.biz.id/dl/ig"
        params = {"url": url}
        headers = {"accept": "*/*"}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, params=params, headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if not data.get("ok", False):
                            await utils.answer(message, self.strings("error"))
                            return

                        video_urls = [item.get("url") for item in data.get("url", []) if item.get("type") in ["mp4", "video"]]

                        if video_urls:
                            for download_url in video_urls:
                                file_name = hashlib.md5(download_url.encode("utf-8")).hexdigest() + ".mp4"
                                file_path = f"/tmp/{file_name}"

                                async with session.get(download_url) as file_resp:
                                    if file_resp.status == 200:
                                        with open(file_path, "wb") as file:
                                            file.write(await file_resp.read())

                                        await message.client.send_file(
                                            message.peer_id,
                                            file_path,
                                            caption=self.strings("success"),
                                        )

                                        if os.path.exists(file_path):
                                            os.remove(file_path)

                                        await message.delete()
                                    else:
                                        await utils.answer(message, self.strings("error"))
                        else:
                            await utils.answer(message, self.strings("error"))
                    else:
                        await utils.answer(message, self.strings("error"))
        except Exception as e:
            await utils.answer(message, f"❌ <b>Error:</b> {str(e)}")
            raise e
