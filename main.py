# Import all module and library
import os
from flask import Flask, request, jsonify, render_template
import logging
from waitress import serve
from data import db_session
from data.statistics import Statistics
from api_functions import *

# Init db_session and creating app
db_session.global_init("db/statistics.db")

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

sessionStorage = {}  # Формат данных: Пользователь: {место, маштаб, метки, маршруты, кнопки}

key_words_for_size = []
key_words_for_pt = []
key_words_for_pl = []
key_words_for_theme = []
key_words_for_map = []

for end in ['', 'а', 'у', 'ом', 'е', 'ы', 'ов', 'ам', 'ами', 'ах']:
    key_words_for_size.append('размер' + end)
    key_words_for_size.append('масштаб' + end)
    key_words_for_pl.append('маршрут' + end)
    key_words_for_theme.append('цвет' + end)

for end in ['ка', 'ки', 'ок', 'ке', 'кой', 'ками', 'ку', 'ках']:
    key_words_for_pt.append('мет' + end)

for end in ['а', 'ы', 'е', 'у']:
    key_words_for_theme.append('тем' + end)

for end in ['ие', 'ия', 'ий', 'ию', 'иям', 'ием', 'иями', 'ии', 'иях']:
    key_words_for_pt.append('обозначен' + end)
    key_words_for_size.append('приближен' + end)

for end in ['я', 'и', 'е', 'ю', 'ей', 'й', 'ям', 'ях']:
    key_words_for_map.append('вариаци' + end)

for end in ['ь', 'и', 'я', 'ей', 'ю', 'ям', 'ем', 'ём', 'и', 'ях']:
    key_words_for_pl.append('пут' + end)

for end in ['ь', 'я', 'ю', 'ем', 'е', 'и', 'ей', 'ям', 'ями', 'ях']:
    key_words_for_map.append('стил' + end)

key_words_for_size.sort()
key_words_for_pt.sort()
key_words_for_pl.sort()
key_words_for_theme.sort()
key_words_for_map.sort()


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# Main page
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# Page for special user
@app.route('/user_statistics/<string:user_id>')
def user_statistics(user_id):
    db_sess = db_session.create_session()
    requests = db_sess.query(Statistics).filter(Statistics.user_id == user_id).all()

    # ------------------------------------------------------------------------------------------------------------------
    transform_list = list(map(lambda x:
                              [x.full_name_place, x.created_date.strftime("Дата: %Y-%m-%d, Время: %H:%M:%S"), x.url],
                              requests))[::-1]
    return render_template("user_statistics.html",
                           user_id=user_id, number=len(transform_list), requests=transform_list)


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# Help page
@app.route('/user_statistics')
def user_statistics_help():
    db_sess = db_session.create_session()
    lines = db_sess.query(Statistics).all()
    list_of_users = sorted(list(set(list(map(lambda x: x.user_id, lines)))))
    return render_template('user_statistics_help.html',
                           number=len(list_of_users), list_of_users=list_of_users)


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# Page with all requests
@app.route('/general_statistics')
def general_statistics():
    db_sess = db_session.create_session()
    requests = db_sess.query(Statistics).all()
    transform_list = list(map(lambda x: [x.full_name_place, x.user_id,
                                         x.created_date.strftime("Дата: %Y-%m-%d, Время: %H:%M:%S"), x.url], requests))[
        ::-1]

    # ------------------------------------------------------------------------------------------------------------------
    return render_template('general_statistics.html',
                           number=len(transform_list), requests=transform_list)


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# Page with statistics of users and places
@app.route('/statistics_of_users_and_places')
def statistics_of_users_and_places():
    db_sess = db_session.create_session()
    lines = db_sess.query(Statistics).all()

    # ------------------------------------------------------------------------------------------------------------------
    list_of_users = sorted(list(set(list(map(lambda x: x.user_id, lines)))))
    transform_users = []
    for user in list_of_users:
        number_of_requests = len(list(filter(lambda x: x.user_id == user, lines)))
        last_time = max(list(map(lambda x: x.created_date, list(filter(lambda x: x.user_id == user,
                                                                       lines))))).strftime(
            "Дата: %Y-%m-%d, Время: %H:%M:%S")
        transform_users.append([user, number_of_requests, last_time])

    # ------------------------------------------------------------------------------------------------------------------
    list_of_places = sorted(list(set(list(map(lambda x: x.full_name_place, lines)))))
    transform_places = []
    for place in list_of_places:
        number_of_requests = len(list(filter(lambda x: x.full_name_place == place, lines)))
        last_time = max(list(map(lambda x: x.created_date, list(filter(lambda x: x.full_name_place == place,
                                                                       lines))))).strftime(
            "Дата: %Y-%m-%d, Время: %H:%M:%S")
        transform_places.append([place, number_of_requests, last_time])
    return render_template('statistics_of_users_and_places.html',
                           list_of_users=transform_users, list_of_places=transform_places)


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# Page with last image
@app.route('/last_map')
def last_image():
    return render_template('last_map.html')


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
@app.route('/post', methods=['POST'])
def main():
    logging.info(f'Request: {request.json!r}')

    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    handle_dialog(request.json, response)

    logging.info(f'Response:  {response!r}')

    return jsonify(response)


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
def handle_dialog(req, res):
    user_id = req["session"]["user_id"]

    if req["session"]["new"]:  # Определие нового пользователя
        sessionStorage[user_id] = {}

        res["response"]["text"] = ("Привет, я путеводитель. "
                                   "Напиши место, которое хочешь увидеть на карте. "
                                   "Ты можешь указать масштаб карты, "
                                   "где 1 - вся планета, 21 - максимальное приближение. " 
                                   "А также метки и/или маршруты, а я отображу всё это на карте. "
                                   "Как дополнительные возможности можно использовать "
                                   "переключение темы и стиля карты (обычный, водительский, транспортный). "
                                   "Ещё существует команда 'Очистка' для очищения параметров карты.")
        return
    # ------------------------------------------------------------------------------------------------------------------
    # Изменение параметров карты в зависимости от переданных переменных
    message_sections = cut_in_sections(req["request"]["nlu"], user_id)
    for i in message_sections:
        if message_sections[i] is not None:
            sessionStorage[user_id][i] = message_sections[i]
    # ------------------------------------------------------------------------------------------------------------------
    # Обработка недостаточной информации
    if "place" not in sessionStorage[user_id]:
        res["response"]["text"] = "Ты забыл указать место."
        res['response']['end_session'] = False
    # ------------------------------------------------------------------------------------------------------------------
    else:
        p, s, pt, pl, t, m = (sessionStorage[user_id]["place"], sessionStorage[user_id].get("size", None),
                        sessionStorage[user_id].get("points", None), sessionStorage[user_id].get("ways", None),
                           sessionStorage[user_id].get("theme", 'light'), sessionStorage[user_id].get("map", 'map'))
        pt = [] if pt is None else pt
        pl = [] if pl is None else pl

        res['response']['card'] = {}
        res['response']['card']['type'] = 'BigImage'
        res['response']['card']['title'] = f'Вот карта по адресу {get_full_name(p)}'
        res["response"]["card"]["image_id"] = all_for_picture(p, s, pt=pt, pl=pl, user_id=user_id, theme=t, maptype=m)
        res['response']['end_session'] = False
        res['response']['text'] = f'Вот карта по адресу {get_full_name(p)}'


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# Распределение информации по типу: место, размер, метки или маршруты
def cut_in_sections(nlu, user_id):
    place = None
    size = sessionStorage[user_id].get("size", 0)
    points = sessionStorage[user_id].get("points", [])
    ways = sessionStorage[user_id].get("ways", [])
    theme = sessionStorage[user_id].get("theme", 'light')
    maptype = sessionStorage[user_id].get("map", 'map')

    if 'очистка' in nlu["tokens"]:
        size = 0
        points = []
        ways = []
        theme = 'light'
        maptype = 'map'

    list_of_geo = list(filter(lambda x: x["type"] == "YANDEX.GEO", nlu["entities"]))

    last_type = 'place'
    for num, token in enumerate(nlu["tokens"]):

        if token in key_words_for_size:
            last_type = 'size'

        elif token in key_words_for_pt:
            last_type = 'points'

        elif token in key_words_for_pl:
            last_type = 'ways'
            ways.append([])

        elif token in key_words_for_theme:
            last_type = 'theme'

        elif token in key_words_for_map:
            last_type = 'map'

        elif last_type == 'place':
            for geo in list_of_geo:
                if geo["tokens"]['start'] <= num < geo["tokens"]['end']:
                    place = ' '.join(geo["value"].values())
                    list_of_geo.remove(geo)
                    break

        elif last_type == 'size':
            if token.isdigit():
                size = int(token)
            elif 'авто' in token:
                size = 0

        elif last_type == 'points':
            for geo in list_of_geo:
                if geo["tokens"]['start'] <= num < geo["tokens"]['end']:
                    points.append(' '.join(geo["value"].values()))
                    list_of_geo.remove(geo)
                    break

        elif last_type == 'ways':
            for geo in list_of_geo:
                if geo["tokens"]['start'] <= num < geo["tokens"]['end']:
                    ways[-1].append(' '.join(geo["value"].values()))
                    list_of_geo.remove(geo)
                    break

        elif last_type == 'theme':
            if 'свет' in token or 'бел' in token:
                theme = 'light'
                last_type = 'place'
            elif 'темн' in token or 'тёмн' in token or 'чёрн' in token or 'черн' in token:
                theme = 'dark'
                last_type = 'place'

        elif last_type == 'map':
            if 'прост' in token or 'обычн' in token:
                maptype = 'map'
                last_type = 'place'
            elif 'водител' in token or 'доро' in token:
                maptype = 'driving'
                last_type = 'place'
            elif 'транспорт' in token:
                maptype = 'transit'
                last_type = 'place'

    message_sections = {"place": place, "size": size, "points": points, "ways": ways, "theme": theme, "map": maptype}
    return message_sections


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    serve(app, host='0.0.0.0', port=port)
