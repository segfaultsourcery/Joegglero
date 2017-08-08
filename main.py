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
            error = (
                type(exception).__name__,
                str(exception))

        return json.dumps({
            'result': result,
            'error': error})

    _wrapper.__name__ = fn.__name__
    _wrapper.__doc__ = fn.__doc__

    return _wrapper


@app.route('/submit/<path:command>', methods=['GET'])
@app.route('/submit', methods=['POST'])
@apiresult
def submit(command=None):
    """
    Submit a job. This can be a string, which will be split into terms by " ".
    It can also be a pre-split list, which is more robust.
    """
    if command is None:
        command = request.json

    job_id = Juggler.submit_job(command)
    return job_id


@app.route('/submit_many', methods=['POST'])
@apiresult
def submit_many():
    """
    Everything is fired off at once. Think of it as a shotgun.
    Commands are sent in as lists of lists containing terms.

    [['echo', 'before this'],
     ['echo', 'this may happen']]
    """
    commands = request.json
    job_ids = list(map(Juggler.submit_job, commands))
    return job_ids


@app.route('/submit_chain', methods=['POST'])
@apiresult
def submit_chain():
    """
    If submit_many is a shotgun, then this is a machine gun.
    Everything is fired off in order, one by one.
    Commands are sent in as lists of lists containing terms.

    [['echo', 'this will happen'],
     ['echo', 'before this']]
    """
    commands = request.json
    job_ids = Juggler.submit_queue(commands)
    return job_ids


@app.route('/result/<int:job_id>')
@apiresult
def get_result(job_id):
    """
    Gets the result of a finished job.
    If the job has not yet finished, wait for it.
    """
    job_id, result = Juggler.get_result(job_id)
    return result


@app.route('/status/<int:job_id>')
@app.route('/status')
@apiresult
def get_status(job_id=None):
    """
    Gets the job status.
    This will tell you what the command was,
    and if it's still running.
    """
    if job_id is None:
        return dict(Juggler.get_all_statuses())

    job_id, result = Juggler.get_status(job_id)
    return result


if __name__ == '__main__':
    app.run(debug=True)
