import json

from flask import Flask, request

from juggler import Juggler

app = Flask(__name__)


def apiresult(fn):
    def _wrapper(*args, **kw):

        result = None
        error = None

        try:
            result = fn(*args, **kw)

        except Exception as exception:
            error = str(exception)

        return json.dumps({
            'result': result,
            'error': error
        })

    _wrapper.__name__ = fn.__name__
    _wrapper.__doc__ = fn.__doc__

    return _wrapper


@app.route('/submit/<path:command>', methods=['GET'])
@app.route('/submit', methods=['POST'])
@apiresult
def submit(command=None):
    if command is None:
        command = request.json

    job_id = Juggler.submit_job(command)
    return job_id


@app.route('/submit_many', methods=['POST'])
@apiresult
def submit_many():
    commands = request.json
    job_ids = list(map(Juggler.submit_job, commands))
    return job_ids


@app.route('/submit_chain', methods=['POST'])
@apiresult
def submit_chain():
    commands = request.json
    job_ids = Juggler.submit_queue(commands)
    return job_ids


@app.route('/result/<int:job_id>')
@apiresult
def get_result(job_id):
    job_id, result = Juggler.get_result(job_id)
    return result


@app.route('/status/<int:job_id>')
@apiresult
def get_status(job_id):
    job_id, result = Juggler.get_status(job_id)
    return result


@app.route('/status')
@apiresult
def get_all_statuses():
    result = Juggler.get_all_statuses()
    return dict(result)


if __name__ == '__main__':
    app.run(debug=True)
