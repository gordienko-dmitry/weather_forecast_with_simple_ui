from aiohttp import web, ClientSession, ClientTimeout
from typing import Optional
import logging
import re

from advice import get_advices


WEATHER_URL: str = 'http://wttr.in'
TIMEOUT: int = 3
ERROR_COUNT_FOR_GET: int = 5


def get_weather_block_from_html(html: str) -> str:
    """Getting block with weather from wttr response."""
    result: list = re.findall(r'<pre.*?>(.*)</pre>', html, re.DOTALL)
    return result[0]


def get_country_name(place_info: dict) -> Optional[str]:
    """Getting country name from place dict."""
    country: Optional[str]
    try:
        country = place_info['country'][0]['value']
    except Exception as ex:
        country = None
        logging.error(f"Error in country reading {ex}")
    return country


def get_region_name(place_info: dict) -> Optional[str]:
    """Getting region name from place dict."""
    region: Optional[str]
    try:
        region = place_info['region'][0]['value']
    except Exception as ex:
        region = None
        logging.error(f"Error in region reading {ex}")
    return region


def get_place_name(weather_response: dict) -> Optional[str]:
    """Getting name of country and area."""
    if weather_response["nearest_area"]:
        place_info: dict = weather_response["nearest_area"][0]
        country: Optional[str] = get_country_name(place_info)
        region: Optional[str] = get_region_name(place_info)

        place: Optional[str] = None
        if region and country:
            place = f"Страна: {country}, регион: {region}"
        elif region:
            place = f"Регион: {region}"
        elif country:
            place = f"Страна: {country}"

        return place


def get_wttr_params(json=False) -> dict:
    """Params for weather server."""
    params: dict = {
        "q": "",
        "m": '',
        "lang": "ru",
        "M": "",
        "Q": ""
    }
    if json:
        params["format"] = "j1"
    return params


def get_wttr_headers_for_html_response() -> dict:
    """Adding header for correct html response."""
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/84.0.4147.105 Safari/537.36"
    }


async def _get(session: ClientSession, url: str, json: bool = False, **kwargs):
    """Run GET method."""
    async with session.get(url, **kwargs) as response:
        response.raise_for_status()
        if json:
            return await response.json(content_type=None)
        return await response.text()


async def _get_from_server(session: ClientSession, url: str, json: bool = False, **kwargs):
    """Run GET method few times."""
    timeout: ClientTimeout = ClientTimeout(total=TIMEOUT)
    error_count: int = ERROR_COUNT_FOR_GET
    while True:
        try:
            return await _get(session, url, json, timeout=timeout, **kwargs)
        except Exception as ex:
            logging.error(f"Error in get method (url:{url}, json={json}): {ex}")
            if error_count == 0:
                raise
            error_count -= 1


async def fetch(session: ClientSession, url: str, **kwargs) -> str:
    """Fetching text (html) from server."""
    headers: dict = get_wttr_headers_for_html_response()
    return await _get_from_server(session, url, headers=headers, **kwargs)


async def fetch_json(session: ClientSession, url: str, **kwargs) -> dict:
    """Fetching json in dict from server."""
    return await _get_from_server(session, url, json=True, **kwargs)


async def get_top_of_weather_block(session: ClientSession, url: str, place: str) -> str:
    """"""
    weather_response: dict = await fetch_json(session, url, params=get_wttr_params(True))
    place_info: str = get_place_name(weather_response)
    html_place: str
    if place_info:
        html_place = f"<h3 class='mb-4'>{place}: ({place_info})</h3>"
    else:
        html_place = f"<h3 class='mb-4'>{place}</h3>"

    return html_place + get_advices(weather_response)


async def get_visualisation_weather(session: ClientSession, url: str) -> str:
    """Getting html views of weather."""
    full_html: str = await fetch(session, url, params=get_wttr_params())
    return get_weather_block_from_html(full_html)


async def get_weather_html_block(place: str) -> str:
    """Getting html block for our site."""
    url: str = f'{WEATHER_URL}/{place}'
    async with ClientSession() as session:
        advice_html_text: str = await get_top_of_weather_block(session, url, place)
        html_for_div: str = await get_visualisation_weather(session, url)
    return advice_html_text + html_for_div


async def get_weather_with_comments(request: web.Request) -> web.Response:
    """Getting html block & info for user."""
    place: str = request.rel_url.query.get("place", "")
    try:
        weather_html_block: str = await get_weather_html_block(place)
    except Exception as ex:
        logging.error(f"Error in weather block: {ex}")
        return web.HTTPInternalServerError(text="Weather not available at the moment")
    return web.Response(text=weather_html_block, content_type='text/html')
