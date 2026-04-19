import os
from flask import Flask, request, jsonify
import logging
from waitress import serve

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

sessionStorage = {}


@app.route('/')
def health_check():
    return ''


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


def handle_dialog(req, res):
    pass


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    serve(app, host='0.0.0.0', port=port)
