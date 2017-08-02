import subprocess
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from time import sleep

from slinkie import Slinkie


def repeat(fn, *args, **kw):
    while True:
        yield fn(*args, **kw)


class Juggler:
    lock = Lock()
    job_id = 1
    jobs = {}
    tpe = ThreadPoolExecutor(8)

    def __init__(self):
        raise Exception(f"Do not instantiate {type(self).__name__}.")

    @classmethod
    def _get_job_id(cls):
        with cls.lock:
            result, cls.job_id = cls.job_id, cls.job_id + 1
            return result

    @staticmethod
    def _job(command):
        try:
            result = subprocess.run(
                command,
                universal_newlines=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)

            return {
                'command': command,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr}

        except Exception as e:
            return {
                'command': command,
                'returncode': -0xc05fefe,  # covfefe.
                'stdout': None,
                'stderr': str(e)}

    @classmethod
    def submit_job(cls, command):

        if isinstance(command, str):
            _command = Slinkie(command.split(' ')) \
                .map(lambda it: it.strip()) \
                .filter(lambda it: it != "") \
                .list()
        else:
            _command = list(command)

        job_id = cls._get_job_id()
        cls.jobs[job_id] = (_command, cls.tpe.submit(cls._job, _command))

        return job_id

    @classmethod
    def submit_queue(cls, commands):
        job_ids = []
        for command in commands:
            job_id = cls._get_job_id()
            cls.jobs[job_id] = (command, None)
            job_ids.append(job_id)

        cls._chain_commands(job_ids)
        return job_ids

    @classmethod
    def _chain_commands(cls, job_ids):

        def _chainer(_job_ids):
            head, *tail = _job_ids

            command, _ = cls.jobs[head]
            job = cls.tpe.submit(cls._job, command)
            cls.jobs[head] = (command, job)

            if tail:
                while not job.done():
                    sleep(0.01)
                _chainer(tail)

        cls.tpe.submit(_chainer, job_ids)

    @classmethod
    def get_result(cls, job_id):
        _, future = cls.jobs[job_id]

        if future is None:
            return job_id, None

        return job_id, future.result()

    @classmethod
    def get_status(cls, job_id):
        command, future = cls.jobs[job_id]

        if future is None:
            return job_id, {
                'command': command,
                'done': False,
                'running': False,
                'cancelled': False,
                'waiting': True}

        return job_id, {
            'command': command,
            'done': future.done(),
            'running': future.running(),
            'cancelled': future.cancelled(),
            'waiting': False}

    @classmethod
    def get_all_statuses(cls):
        for job_id, (command, future) in cls.jobs.items():
            if future is None:
                yield job_id, {
                    'command': command,
                    'done': False,
                    'running': False,
                    'cancelled': False,
                    'waiting': True}
            else:
                yield job_id, {
                    'command': command,
                    'done': future.done(),
                    'running': future.running(),
                    'cancelled': future.cancelled(),
                    'waiting': False}
