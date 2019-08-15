#!/usr/bin/env python3
import os
import json

from flask import Flask, request
from flask_cors import CORS

from exm.conf import settings
from exm import utils


app = Flask(__name__)

cors = CORS(app, resources={r"*": {"origins": "*"}})

@app.route('/load', methods=['GET'])
def load_conf():
    conf = request.args.get('chall')
    challenges_directory = getattr(settings, 'CHALLENGES_DIRECTORY', './challenges/') # from config
    p = os.path.join(challenges_directory, conf.replace('.', ''), 'conf.json')
    return open(p).read()


@app.route('/save', methods=['POST'])
def save_conf():
    conf = request.args.get('chall')
    data = request.get_json()

    challenges_directory = getattr(settings, 'CHALLENGES_DIRECTORY', './challenges/') # from config
    p = os.path.join(challenges_directory, conf.replace('.', ''), 'conf.json')
    with open(p, 'w') as f:
        f.write(json.dumps(data))

    return open(p).read()

@app.route('/challs', methods=['GET'])
def get_challs():
    ret = utils.parse_challenges_from_directory()
    out = []
    for r in ret:
        out.append({"id": r, "name": r})
    return json.dumps(out)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1234, threaded=True)
