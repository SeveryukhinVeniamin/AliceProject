import os
from flask import Flask, request, jsonify
import logging
from waitress import serve

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

sessionStorage = {} # Формат данных: Пользователь: {место, маштаб, метки, маршруты, кнопки}

@app.route('/')
def health_check():
    return ''


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
    serve(app, host='0.0.0.0', port=port)
