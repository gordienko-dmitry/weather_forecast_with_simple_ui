import re


def get_advices(weather_response: dict) -> str:
    """Getting advice for temperature on the street"""

    # today, tomorrow, day after tomorrow
    days_weather: list = weather_response["weather"]
    advices: list = []

    current_hour: int = int(weather_response["current_condition"][0]["localObsDateTime"][11:13])
    if weather_response["current_condition"][0]["localObsDateTime"][-2:] == "PM":
        current_hour += 12
    current_hour = current_hour - current_hour % 3

    # indexes in hourly weather
    # 9AM - 9PM
    weather_indexes: list = [3, 4, 5, 6, 7]

    today: bool = True
    for day_weather in days_weather:
        avg_temp, rain = get_avg_temp_and_rainy_for_day(day_weather, weather_indexes, today, current_hour)
        advices.append(get_text_advice(avg_temp, rain))
        today = False

    return convert_advices_to_html(advices)


def get_avg_temp_and_rainy_for_day(day_weather: dict, weather_indexes: list, today: bool,
                                   current_hour: int) -> (int, bool):
    """Solving average temperature and rain flag."""
    rain: bool = False
    avg_temp: int = 0
    count_temps: int = 0
    for index in weather_indexes:
        hourly_weather = day_weather["hourly"][index]
        if today and current_hour > int(hourly_weather["time"][0:-2]):
            continue
        avg_temp += int(hourly_weather["tempC"])
        count_temps += 1
        if rain:
            continue
        rain = check_rain_condition(hourly_weather)

    avg_temp //= count_temps
    return avg_temp, rain


def check_rain_condition(hourly_weather: dict) -> bool:
    """Checking if it rain in the day."""
    for weather_condition in hourly_weather["weatherDesc"]:
        if re.match(r'.*rain', weather_condition["value"]):
            return True
    return False


def get_text_advice(avg_temp: int, rain=False) -> str:
    """Getting advice text for average temp and rainy weather."""
    text: str
    if avg_temp < 0:
        text = "Одевайтесь теплее, на улице мороз"
    elif avg_temp < 10:
        text = "Прохладно на улице - будьте осторожны, без куртки не выходите"
    elif avg_temp < 20:
        text = "Накиньте плащ - не май месяц, все-таки"
    else:
        text = "Тепло и приятно - давайте гулять в футболках"

    text += f" (средняя температура: {avg_temp}C)"

    if rain:
        text += "\nИ не забудьте взять зонтик - ожидается дождь"

    return text


def convert_advices_to_html(advices: list) -> str:
    """Converting advice texts to html block."""
    html_text = "<h4 class='mb-4'>Советы редакции:</h4>"
    days = {
        0: "Сегодня",
        1: "Завтра",
        2: "Послезавтра"
    }
    for index, advice in enumerate(advices):
        html_text += "<p class='mb-2'>" \
                 "<div class='row'>" \
                 "<div class='col col-2'>" \
                 "<strong>" + days[index] + "</strong>:" \
                 "</div> " \
                 "<div class='col'>" + advice.replace("\n", "<BR>") + \
                 "</div>" \
                 "</div>" \
                 "</p>"

    return "<div class='alert alert-success' role='alert'>" + html_text + "</div>"
