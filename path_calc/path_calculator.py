import requests
from bs4 import BeautifulSoup as BS
from datetime import datetime, timedelta
import re
import json
from fuzzywuzzy import fuzz
import pickle


def get_potapovo_time():
    url = 'https://potapovo.com/resident/marshrutki'
    r = requests.get(url)
    soup = BS(r.content, 'html.parser')
    text_time = soup.select('.sel')[1].text

    hour = int(text_time[:2])
    minute = int(text_time[3:])

    current_time = datetime.today()
    time = current_time.replace(hour=hour, minute=minute, second=0, microsecond=0)

    return time


def calc_potapovo_time():
    # TODO: Нужно измерить сколько едет Потаповский автобус
    bus_travel_time = timedelta(minutes=15)
    legs_travel_time = timedelta(minutes=2)
    bus_start_time = get_potapovo_time()

    go_out_time = bus_start_time - legs_travel_time
    arrival_time = bus_start_time + bus_travel_time

    return go_out_time, arrival_time


def get_636_time():
    url = 'https://yandex.ru/maps/213/moscow/stops/stop__9649775/?ll=37.499055%2C55.532824&source=wiztransit&z=17'
    r = requests.get(url)
    soup = BS(r.content, 'html.parser')
    for el in soup.select('.masstransit-vehicle-snippet-view'):
        bus_name = el.select('.masstransit-vehicle-snippet-view__name')[0].text
        if bus_name == '636':
            first_text = el.select('.masstransit-prognoses-view__title._live')[0].text
            second_text = el.select('.masstransit-prognoses-view__time')[0].text
            return first_text, second_text


def calc_636_time():
    # TODO: Нужно измерить сколько едет автобус
    bus_travel_time = timedelta(minutes=15)
    # TODO: Нужно измерить сколько нужно идти до 636
    legs_travel_time = timedelta(minutes=11)
    current_time = datetime.today()
    bus_start_time = False

    for time in process_636_time()[::-1]:
        if (time - legs_travel_time) > current_time:
            bus_start_time = time

    if bus_start_time:
        go_out_time = bus_start_time - legs_travel_time
        arrival_time = bus_start_time + bus_travel_time

        return go_out_time, arrival_time
    else:
        return False


def process_636_time():
    times = get_636_time()
    output = []
    for text in times:
        if re.findall(r'мин', text):
            minute = int(re.findall(r'\d+', text)[0])
            delta = timedelta(minutes=minute)
            current_time = datetime.today()

            time = (current_time + delta).replace(second=0, microsecond=0)
            output.append(time)
    return output


def calc_skate_time():
    go_out_time = datetime.today()
    arrival_time = datetime.today() + timedelta(minutes=15)
    return go_out_time, arrival_time


def get_metro_time(station):
    url = 'https://metrobook.ru/kcmsajax.php'

    data = {'mod': 'metrobook',
            'oper': 'getShortestPath',
            'mid': '2',
            'sdid1': '248',
            'sdid2': station[1],
            'whatToMinimize': '0'}

    r = requests.post(url, data=data)
    time = json.loads(r.text)
    return int(time['table']['totalTime'] / 60)


def find_best_option(user_text):
    with open('metro.stations', 'rb') as file:
        metro_stations = pickle.load(file)
    max_score = -1
    for station, number in metro_stations.items():
        if fuzz.ratio(station, user_text) > max_score:
            max_score = fuzz.ratio(station, user_text)
            best_option = [station, number]

    return best_option


def calc_delta(time):
    current_time = datetime.today()
    delta = time - current_time
    if delta.days != -1:
        minuts = round(delta.seconds / 60)
    else:
        minuts = 0
    text = str(minuts) + ' мин'
    return text


def calc_time_from_datetime(time):
    text = datetime.strftime(time, '%H:%M')
    return text


# ------------------------------------------------------------


def put_ways_in_order():
    bus_potapovo = {
        'name': 'Пот. Автобус',
        'go_out_time': calc_delta(calc_potapovo_time()[0]),
        'arrival_time': calc_potapovo_time()[1]
    }

    if calc_636_time():
        bus_636 = {
            'name': '636 Автобус',
            'go_out_time': calc_delta(calc_636_time()[0]),
            'arrival_time': calc_636_time()[1]
        }
    else:
        bus_636 = False

    skate = {
        'name': 'Скейт',
        'go_out_time': calc_delta(calc_skate_time()[0]),
        'arrival_time': calc_skate_time()[1]
    }

    ways_correct = []
    if bus_636:
        if bus_potapovo['arrival_time'] <= bus_636['arrival_time'] and bus_potapovo['arrival_time'] <= skate['arrival_time']:
            if bus_636['arrival_time'] <= skate['arrival_time']:
                ways_correct.append(bus_potapovo)
                ways_correct.append(bus_636)
                ways_correct.append(skate)
            else:
                ways_correct.append(bus_potapovo)
                ways_correct.append(skate)
                ways_correct.append(bus_636)

        elif bus_636['arrival_time'] <= bus_potapovo['arrival_time'] and bus_636['arrival_time'] <= skate['arrival_time']:
            if bus_potapovo['arrival_time'] <= skate['arrival_time']:
                ways_correct.append(bus_636)
                ways_correct.append(bus_potapovo)
                ways_correct.append(skate)
            else:
                ways_correct.append(bus_636)
                ways_correct.append(skate)
                ways_correct.append(bus_potapovo)

        elif skate['arrival_time'] <= bus_potapovo['arrival_time'] and skate['arrival_time'] <= bus_636['arrival_time']:
            if bus_potapovo['arrival_time'] <= bus_636['arrival_time']:
                ways_correct.append(skate)
                ways_correct.append(bus_potapovo)
                ways_correct.append(bus_636)
            else:
                ways_correct.append(skate)
                ways_correct.append(bus_636)
                ways_correct.append(bus_potapovo)
    else:
        if bus_potapovo['arrival_time'] <= skate['arrival_time']:
            ways_correct.append(bus_potapovo)
            ways_correct.append(skate)
        else:
            ways_correct.append(skate)
            ways_correct.append(bus_potapovo)
    return ways_correct


def get_text_timetable():
    ways = put_ways_in_order()

    text = '<b>Вот как можно добраться до метро:</b>\n\n'
    emoji_numbers = ['1️⃣', '2️⃣', '3️⃣']
    for n in range(len(ways)):
        text += f'{emoji_numbers[n]} <b>{ways[n]["name"]}\n</b>Прибытие в <b>{calc_time_from_datetime(ways[n]["arrival_time"])}</b>\n' \
                f'Выходи через <b>{ways[n]["go_out_time"]}</b>\n\n'
    text += f'<i>Обновлено: {datetime.now().strftime("%H:%M")}</i>'
    return text