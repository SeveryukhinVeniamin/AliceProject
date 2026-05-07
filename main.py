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

for end in ['', 'а', 'у', 'ом', 'е', 'ы', 'ов', 'ам', 'ами', 'ах']:
    key_words_for_size.append('размер' + end)
    key_words_for_size.append('масштаб' + end)
    key_words_for_pl.append('маршрут' + end)

for end in ['ка', 'ки', 'ок', 'ке', 'кой', 'ками', 'ку', 'ках']:
    key_words_for_pt.append('мет' + end)

for end in ['ие', 'ия', 'ий', 'ию', 'иям', 'ием', 'иями', 'ии', 'иях']:
    key_words_for_pt.append('обозначен' + end)
    key_words_for_size.append('приближен' + end)

for end in ['ь', 'и', 'я', 'ей', 'ю', 'ям', 'ем', 'ём', 'и', 'ях']:
    key_words_for_pl.append('пут' + end)

key_words_for_size.sort()
key_words_for_pt.sort()
key_words_for_pl.sort()


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
                                   "Напиши место с указанием масштаба карты, меток и/или маршрутов,"
                                   "а я отображу это на карте.")
        return
    # -------------------------------------------------------------------------------------------------------------------
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
    elif "size" not in sessionStorage[user_id]:
        res["response"]["text"] = "Ты забыл указать масштаб."
        res['response']['end_session'] = False
    # ------------------------------------------------------------------------------------------------------------------
    else:
        p, s, pt, pl = (sessionStorage[user_id]["place"], sessionStorage[user_id]["size"],
                        sessionStorage[user_id].get("points", None), sessionStorage[user_id].get("ways", None))
        pt = [] if pt is None else pt
        pl = [] if pl is None else pl

        res['response']['card'] = {}
        res['response']['card']['type'] = 'BigImage'
        res['response']['card']['title'] = 'Карта'
        res["response"]["card"]["image_id"] = all_for_picture(p, s, pt=pt, pl=pl, user_id=user_id)
        res['response']['end_session'] = False
        res['response']['text'] = 'Вот карта'


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# Распределение информации по типу: место, размер, метки или маршруты
def cut_in_sections(nlu, user_id):
    place, size, points, ways = (None, None,
                                 sessionStorage[user_id].get("points", []), sessionStorage[user_id].get("ways", []))
    # last_word = len(nlu["tokens"])

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

        elif last_type == 'place':
            for geo in list_of_geo:
                if geo["tokens"]['start'] <= num < geo["tokens"]['end']:
                    place = ' '.join(geo["value"].values())
                    last_type = 'no'
                    list_of_geo.remove(geo)
                    break

        elif last_type == 'size':
            if token.isdigit():
                size = int(token)

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


    '''    if "маршруты" in nlu["tokens"]:
        _ways_, last_word = ([i for i in range(nlu["tokens"].index("маршруты"), last_word)],
                             nlu["tokens"].index("маршруты"))
    if "метки" in nlu["tokens"]:
        _points_, last_word = ([i for i in range(nlu["tokens"].index("метки"), last_word)],
                               nlu["tokens"].index("метки"))
    if "размер" in nlu["tokens"]:
        _size_, last_word = ([i for i in range(nlu["tokens"].index("размер"), last_word)],
                             nlu["tokens"].index("размер"))'''
    # _place_ = [i for i in range(0, last_word)]
    # ------------------------------------------------------------------------------------------------------------------
    '''for i in nlu["entities"]:
        if i["type"] == "YANDEX.GEO":
            if i["tokens"]["start"] in _place_ and i["tokens"]["end"] - 1 in _place_:
                place = " ".join(reversed([i["value"][j] for j in i["value"]]))
            elif i["tokens"]["start"] in _points_ and i["tokens"]["end"] - 1 in _points_:
                points.append(" ".join(reversed([i["value"][j] for j in i["value"]])))
        elif i["type"] == "YANDEX.NUMBER" and i["tokens"]["start"] in _size_ and i["tokens"]["end"] - 1 in _size_:
            size = i["value"]'''

    message_sections = {"place": place, "size": size, "points": points, "ways": ways}
    print(message_sections)
    return message_sections


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    serve(app, host='0.0.0.0', port=port)
    # serve(app, host='127.0.0.1', port=port)
