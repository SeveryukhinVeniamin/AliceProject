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
<html lang="en">
    <head>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" 
        integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Main page of website</title>
    </head>
    
    <body>
        <h1>Hello client!</h1>
        <h3>That is main page of the site "Алиса путеводитель" where you can find information about statistics.</h3>
        <br>
        <a target="_blank" href='/general_statistics' class="card-text">
            <h5>There is information about all requests.</h5>
        <a/>
        <br>
        <a target="_blank" href='/user_statistics' class="card-text">
            <h5>There is information about specific user.</h5>
        <a/>
        <br>
        <a target="_blank" href='/statistics_of_users_and_places' class="card-text">
            <h5>There is information about users requests and places.</h5>
        <a/>
        <br>
        <h3>We believe that this information was useful for you.</h3>
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
<html lang="en">
    <head>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet"
        integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Statistics</title>
    </head>
    
    <body>
        <h1>Statistics of user "{user_id}"</h1>
        <h2>This user made {len(requests)} requests</h2>
        <br>
        <br>'''
    # ------------------------------------------------------------------------------------------------------------------
    for i, line in enumerate(requests):
        text += f'''
        <div class="card">
            <h5 class="card-header">Request {i + 1}</h5>
            <div class="card-body">
                <h4 class="card-title">{line.full_name_place}</h4>
                <h5 class="card-text">{line.created_date.strftime("Data: %Y-%m-%d, Time: %H:%M:%S")}.</h5>
                <a target="_blank" href={line.url} class="card-text">URL<a/>
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
<html lang="en">
    <head>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" 
        integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Users information</title>
    </head>
    
    <body>
        <h3>Please add to url id of user.</h3>
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
<html lang="en">
    <head>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" 
        integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Statistics</title>
    </head>
    
    <body>
        <h1>General statistics</h1>
        <h2>At all, there are {len(requests)} requests</h2>
        <br>
        <br>'''
    # ------------------------------------------------------------------------------------------------------------------
    for i, line in enumerate(requests):
        text += f'''
        <div class="card">
            <h5 class="card-header">Request {i + 1}</h5>
            <div class="card-body">
                <h4 class="card-title">{line.full_name_place}</h4>
                <h5 class="card-text">By user '{line.user_id}'</h5>
                <h5 class="card-text">{line.created_date.strftime("Data: %Y-%m-%d, Time: %H:%M:%S")}.</h5>
                <a target="_blank" href={line.url} class="card-text">URL<a/>
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
<html lang="en">
    <head>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" 
        integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Statistics</title>
    </head>
    
    <body>
        <h1>Statistics of users and places.</h1>
        <br>
        <h3>Users:</h3>'''
    # ------------------------------------------------------------------------------------------------------------------
    list_of_users = sorted(list(set(list(map(lambda x: x.user_id, lines)))))
    for user in list_of_users:
        number_of_requests = len(list(filter(lambda x: x.user_id == user, lines)))
        last_time = max(list(map(lambda x: x.created_date, list(filter(lambda x: x.user_id == user, lines)))))
        text += f'''
        <br>
        <h4>{user} - {number_of_requests} requests</h4>
        <h5>Last activity - {last_time.strftime("%Y-%m-%d; %H:%M:%S")}</h5>'''
    # ------------------------------------------------------------------------------------------------------------------
    text += '''
        <br>
        <br>
        <h3>Places:</h3>'''
    # ------------------------------------------------------------------------------------------------------------------
    list_of_places = sorted(list(set(list(map(lambda x: x.full_name_place, lines)))))
    for place in list_of_places:
        number_of_requests = len(list(filter(lambda x: x.full_name_place == place, lines)))
        last_time = max(list(map(lambda x: x.created_date, list(filter(lambda x: x.full_name_place == place, lines)))))
        text += f'''
        <br>
        <h4>{place} - {number_of_requests} requests</h4>
        <h5>Last search - {last_time.strftime("%Y-%m-%d; %H:%M:%S")}</h5>'''
    # ------------------------------------------------------------------------------------------------------------------
    text += '''
    </body>
</html>'''
    return text


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

        res["response"]["test"] = ("Привет, я путеводитель. "
                                   "Напиши место с указанием маштаба карты, меток и/или маршрутов,"
                                   "а я отображу это на карте.")
        return
    # ------------------------------------------------------------------------------------------------------------------
    message_sections = cut_in_sections(req["request"]["nlu"])
    for i in message_sections:
        if message_sections[i] is not None:
            sessionStorage[i] = message_sections[i]


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# Распределение информации по типу: место, размер, метки или маршруты
def cut_in_sections(nlu):
    place, size, points, ways = None, None, None, None
    last_word = len(nlu["tokens"]) - 1
    if "маршруты" in nlu["tokens"]:
        ways, last_word = (nlu["tokens"].index("маршруты"), last_word), nlu["tokens"].index("маршруты")
    if "метки" in nlu["tokens"]:
        points, last_word = (nlu["tokens"].index("метки"), last_word), nlu["tokens"].index("метки")
    if "размер" in nlu["tokens"]:
        size, last_word = (nlu["tokens"].index("размер"), last_word), nlu["tokens"].index("размер")
    place = (0, last_word) if last_word != 0 else None

    message_sections = {"place": place, "size": size, "points": points, "ways": ways}

    return message_sections


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    # serve(app, host='0.0.0.0', port=port)
    serve(app, host='127.0.0.1', port=port)
