from aiohttp import web
import aiofiles
import logging

from weather import get_weather_with_comments


async def handle_index_page(request):
    """Handle for index page."""
    async with aiofiles.open('index.html', mode='r', encoding="utf-8") as index_file:
        index_contents: str = await index_file.read()
    headers: dict = {"accept-charset": "utf-8"}
    return web.Response(text=index_contents, content_type='text/html', headers=headers)


if __name__ == '__main__':
    logging.basicConfig(filename="server.log", level=logging.INFO,
                        format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')

    logging.info("Starting server")

    app = web.Application()
    app.add_routes([
        web.get('/', handle_index_page),
        web.get('/weather', get_weather_with_comments)
    ])
    web.run_app(app)
