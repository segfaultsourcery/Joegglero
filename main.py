from flask import Flask, jsonify as _jsonify, request

from juggler import Juggler

app = Flask(__name__)


def jsonify(fn):
    def _wrapper(*args, **kw):
        return _jsonify(fn(*args, **kw))

    _wrapper.__name__ = fn.__name__
    _wrapper.__doc__ = fn.__doc__

    return _wrapper


@app.route('/submit/<path:command>', methods=['GET'])
@app.route('/submit', methods=['POST'])
@jsonify
def submit(command=None):
    if command is None:
        command = request.json

    job_id = Juggler.submit_job(command)
    return {'job_id': job_id}


@app.route('/submit_many', methods=['POST'])
@jsonify
def submit_many():
    commands = request.json
    job_ids = list(map(Juggler.submit_job, commands))
    return {'job_ids': job_ids}


@app.route('/submit_chain', methods=['POST'])
@jsonify
def submit_chain():
    commands = request.json
    job_ids = Juggler.submit_queue(commands)
    return {'job_ids': job_ids}


@app.route('/result/<int:job_id>')
@jsonify
def get_result(job_id):
    try:
        job_id, result = Juggler.get_result(job_id)
        return {job_id: result}

    except KeyError as e:
        return {'error': str(e)}


@app.route('/status/<int:job_id>')
@jsonify
def get_status(job_id):
    try:
        job_id, result = Juggler.get_status(job_id)
        return {job_id: result}

    except KeyError as e:
        return {'error': str(e)}


@app.route('/status')
@jsonify
def get_all_statuses():
    try:
        result = Juggler.get_all_statuses()
        return dict(result)

    except KeyError as e:
        return {'error': str(e)}


if __name__ == '__main__':
    app.run(debug=True)
