# Import all module and library
import os
from flask import Flask, request, jsonify
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


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# Main page
@app.route('/')
@app.route('/index')
def index():
    return '''
<!DOCTYPE html>
<html lang="rus">
    <head>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" 
        integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Главная страница</title>
    </head>
    
    <body>
        <h1>Уважаемый пользователь!</h1>
        <h3>Это главная страница сайта "Алиса путеводитель", где вы можете найти информацию о статистике чат-бота.</h3>
        <br>
        <br>
        <a target="_blank" href='/general_statistics' class="card-text">
            <h4>Информация о всех записях.</h4>
        <a/>
        <br>
        <br>
        <a target="_blank" href='/user_statistics' class="card-text">
            <h4>Информация о конкретном пользователе.</h4>
        <a/>
        <br>
        <br>
        <a target="_blank" href='/statistics_of_users_and_places' class="card-text">
            <h4>Общая информация о пользователях и местах.</h4>
        <a/>
        <br>
        <br>
        <a target="_blank" href='/last_image' class="card-text">
            <h4>Последняя нарисованная карта.</h4>
        <a/>
        <br>
        <br>
        <h3>Мы надеемся, что эта информация была вам полезна.</h3>
    </body>
</html>'''


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# Page for special user
@app.route('/user_statistics/<string:user_id>')
def user_statistics_(user_id):
    db_sess = db_session.create_session()
    requests = db_sess.query(Statistics).filter(Statistics.user_id == user_id).all()
    # ------------------------------------------------------------------------------------------------------------------
    text = f'''
<!DOCTYPE html>
<html lang="rus">
    <head>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet"
        integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Статистика пользователя</title>
    </head>
    
    <body>
        <h1>Пользователь "{user_id}".</h1>
        <h2>Общее количество запросов - {len(requests)}.</h2>
        <br>
        <br>'''
    # ------------------------------------------------------------------------------------------------------------------
    for i, line in enumerate(requests):
        text += f'''
        <div class="card">
            <h5 class="card-header">Запрос номер {i + 1}.</h5>
            <div class="card-body">
                <h4 class="card-title">Место карты: {line.full_name_place}.</h4>
                <h5 class="card-text">{line.created_date.strftime("Дата: %Y-%m-%d, Время: %H:%M:%S")}.</h5>
                <a target="_blank" href={line.url} class="card-text">Ссылка на карту.<a/>
            </div>
        </div>
        <br>
        <br>
    </body>
</html>'''
    return text


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# Help page
@app.route('/user_statistics')
def user_statistics():
    return '''
<!DOCTYPE html>
<html lang="rus">
    <head>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" 
        integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Статистика пользователя</title>
    </head>
    
    <body>
        <h3>Пожалуйста, добавьте код пользователя в строке поиска.</h3>
    </body>
</html>'''


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# Page with all requests
@app.route('/general_statistics')
def general_statistics():
    db_sess = db_session.create_session()
    requests = db_sess.query(Statistics).all()
    # ------------------------------------------------------------------------------------------------------------------
    text = f'''
<!DOCTYPE html>
<html lang="rus">
    <head>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" 
        integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Общая Статистика</title>
    </head>
    
    <body>
        <h1>Общая статистика</h1>
        <h2>Всего зарегистрировано {len(requests)} обработанных запросов.</h2>
        <br>
        <br>'''
    # ------------------------------------------------------------------------------------------------------------------
    for i, line in enumerate(requests):
        text += f'''
        <div class="card">
            <h5 class="card-header">Запрос номер {i + 1}.</h5>
            <div class="card-body">
                <h4 class="card-title">Место карты: {line.full_name_place}</h4>
                <h5 class="card-text">Пользователь '{line.user_id}'</h5>
                <h5 class="card-text">{line.created_date.strftime("Дата: %Y-%m-%d, Время: %H:%M:%S")}.</h5>
                <a target="_blank" href={line.url} class="card-text">Ссылка на карту.<a/>
            </div>
        </div>
        <br>
        <br>
    </body>
</html>'''
    return text


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# Page with statistics of users and places
@app.route('/statistics_of_users_and_places')
def statistics_of_users_and_places():
    db_sess = db_session.create_session()
    lines = db_sess.query(Statistics).all()
    # ------------------------------------------------------------------------------------------------------------------
    text = f'''
<!DOCTYPE html>
<html lang="rus">
    <head>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" 
        integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Точечная статистика</title>
    </head>
    
    <body>
        <h1>Точечная статистика.</h1>
        <br>
        <h3>Пользователи:</h3>'''
    # ------------------------------------------------------------------------------------------------------------------
    list_of_users = sorted(list(set(list(map(lambda x: x.user_id, lines)))))
    for user in list_of_users:
        number_of_requests = len(list(filter(lambda x: x.user_id == user, lines)))
        last_time = max(list(map(lambda x: x.created_date, list(filter(lambda x: x.user_id == user, lines)))))
        text += f'''
        <br>
        <h4>"{user}" сделал всего {number_of_requests} запросов.</h4>
        <h5>Последняя активность - {last_time.strftime("%Y-%m-%d; %H:%M:%S")}.</h5>'''
    # ------------------------------------------------------------------------------------------------------------------
    text += '''
        <br>
        <br>
        <h3>Места:</h3>'''
    # ------------------------------------------------------------------------------------------------------------------
    list_of_places = sorted(list(set(list(map(lambda x: x.full_name_place, lines)))))
    for place in list_of_places:
        number_of_requests = len(list(filter(lambda x: x.full_name_place == place, lines)))
        last_time = max(list(map(lambda x: x.created_date, list(filter(lambda x: x.full_name_place == place, lines)))))
        text += f'''
        <br>
        <h4>"{place}" искалось в {number_of_requests} запросах.</h4>
        <h5>Последний поиск - {last_time.strftime("%Y-%m-%d; %H:%M:%S")}.</h5>'''
    # ------------------------------------------------------------------------------------------------------------------
    text += '''
    </body>
</html>'''
    return text


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# Page with last image
@app.route('/last_image')
def last_image():
    return '''
<!DOCTYPE html>
<html lang="rus">
    <head>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" 
        integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Последняя карта</title>
    </head>

    <body>
        <h1>Последняя загруженная карта</h1>
        <img src='static/img/map.png' alt='Похоже в этом приложении карт ещё не загружалось.'>
    </body>
</html>'''


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
                                   "Напиши место с указанием маштаба карты, меток и/или маршрутов,"
                                   "а я отображу это на карте.")
        return
    # -------------------------------------------------------------------------------------------------------------------
    # Изменение параметров карты в зависимости от переданных переменных
    message_sections = cut_in_sections(req["request"]["nlu"])
    for i in message_sections:
        if message_sections[i] is not None:
            sessionStorage[user_id][i] = message_sections[i]
    # ------------------------------------------------------------------------------------------------------------------
    # Обработка недостаточной информации
    if "place" not in sessionStorage[user_id]:
        res["response"]["text"] = "Ты забыл указать место."
        res['response']['end_session'] = False
    elif "size" not in sessionStorage[user_id]:
        res["response"]["text"] = "Ты забыл указать маштаб."
        res['response']['end_session'] = False
    # ------------------------------------------------------------------------------------------------------------------
    else:
        p, s, pt, pl = (sessionStorage[user_id]["place"], sessionStorage[user_id]["size"],
                        sessionStorage[user_id]["points"], sessionStorage[user_id]["ways"])
        pt = [] if pt is None else pt
        pl = [] if pl is None else pl

        res["response"]["card"]["image_id"] = all_for_picture(p, s, pt=pt, pl=pl, user_id=user_id)
        res['response']['end_session'] = False


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# Распределение информации по типу: место, размер, метки или маршруты
def cut_in_sections(nlu):
    place, size, points, ways = None, None, None, None
    last_word = len(nlu["tokens"])

    # Определиние индексов элементов запроса
    if "маршруты" in nlu["tokens"]:
        _ways_, last_word = ([i for i in range(nlu["tokens"].index("маршруты"), last_word)],
                             nlu["tokens"].index("маршруты"))
    if "метки" in nlu["tokens"]:
        _points_, last_word = ([i for i in range(nlu["tokens"].index("метки"), last_word)],
                               nlu["tokens"].index("метки"))
    if "размер" in nlu["tokens"]:
        _size_, last_word = ([i for i in range(nlu["tokens"].index("размер"), last_word)],
                             nlu["tokens"].index("размер"))
    _place_ = [i for i in range(0, last_word)] if last_word != 0 else None
    # ------------------------------------------------------------------------------------------------------------------
    for i in nlu["entities"]:
        if i["type"] == "YANDEX.GEO":
            if i["tokens"]["start"] in _place_ and i["tokens"]["end"] - 1 in _place_:
                place = " ".join(reversed([i["value"][j] for j in i["value"]]))
            elif i["tokens"]["start"] in _points_ and i["tokens"]["end"] - 1 in _points_:
                if points is None:
                    points = []
                points.append(" ".join(reversed([i["value"][j] for j in i["value"]])))
        elif i["type"] == "YANDEX.NUMBER" and i["tokens"]["start"] in _size_ and i["tokens"]["end"] - 1 in _size_:
            size = i["value"]

    message_sections = {"place": place, "size": size, "points": points, "ways": ways}

    return message_sections


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    serve(app, host='0.0.0.0', port=port)
    # serve(app, host='127.0.0.1', port=port)
