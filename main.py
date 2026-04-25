import os
from flask import Flask, request, jsonify
import logging
from waitress import serve
from data import db_session
from data.statistics import Statistics

db_session.global_init("db/statistics.db")
app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

sessionStorage = {} # Формат данных: Пользователь: {место, маштаб, метки, маршруты, кнопки}

@app.route('/')
def health_check():
    return 'Hello World!'


@app.route('/user_statistics/<string:user_id>')
def user_statistics(user_id):
    db_sess = db_session.create_session()
    lines = db_sess.query(Statistics).filter(Statistics.user_id == user_id).all()
    text = f'''<!DOCTYPE html>
<html lang="en">
<head>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Statistics</title>
</head>
<body>
<h1>Statistics of user "{user_id}"</h1>'''
    text += f'<h2>This user made {len(lines)} requests</h2><br><br>'
    for i, line in enumerate(lines):
        text+=f'''<div class="card">
  <h5 class="card-header">Request {i + 1}</h5>
  <div class="card-body">
    <h4 class="card-title">{line.full_name_place}</h4>
    <h5 class="card-text">Data: {line.created_date.strftime("%Y-%m-%d")}, Time: {line.created_date.strftime("%H:%M:%S")}.</h5>
    <a target="_blank" href={line.url} class="card-text">URL<a/>
  </div>
</div><br><br>'''

    text += '</body></html>'
    return text


@app.route('/general_statistics')
def general_statistics():
    db_sess = db_session.create_session()
    lines = db_sess.query(Statistics).all()
    text = f'''<!DOCTYPE html>
<html lang="en">
<head>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Statistics</title>
</head>
<body>
<h1>General statistics</h1>'''
    text += f'<h2>At all, there are {len(lines)} requests</h2><br><br>'
    for i, line in enumerate(lines):
        text+=f'''<div class="card">
  <h5 class="card-header">Request {i + 1}</h5>
  <div class="card-body">
    <h4 class="card-title">{line.full_name_place}</h4>
    <h5 class="card-text">By user '{line.user_id}'</h5>
    <h5 class="card-text">Data: {line.created_date.strftime("%Y-%m-%d")}, Time: {line.created_date.strftime("%H:%M:%S")}.</h5>
    <a target="_blank" href={line.url} class="card-text">URL<a/>
  </div>
</div><br><br>'''

    text += '</body></html>'
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

    if req["session"]["new"]: # Определие нового пользователя
        sessionStorage[user_id] = {}

        res["response"]["test"] = ("Привет, я путеводитель. "
                                   "Напиши место с указанием маштаба карты, меток и/или маршрутов,"
                                   "а я отображу это на карте.")
        return
    #-------------------------------------------------------------------------------------------------------------------
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


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    #serve(app, host='0.0.0.0', port=port)
    serve(app, host='127.0.0.1', port=port)
