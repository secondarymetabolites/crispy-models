"Data models for CRISPy API"

import json
import random
from datetime import datetime


class Session(object):
    """A CRISPy web session object"""
    def __init__(self, db, from_id=None, from_file=None, session_id=None):
        self._db = db
        self._timefmt = '%Y-%m-%d %H:%M:%S'

        if session_id is not None:
            self._load_from_db(session_id)
        else:
            self._create(from_id, from_file)


    def _create(self, from_id, from_file):
        "create a new Session object"
        if from_id is None and from_file is None:
            raise ValueError("Need either id or file to start a session")

        if from_id is not None and from_file is not None:
            raise ValueError("Can't set both id and file for a session")

        now = datetime.utcnow().strftime(self._timefmt)
        session = {
            'state': 'pending',
            'error': '',
            'asid': str(from_id),
            'filename': str(from_file),
            'added': now,
            'last_changed': now,
            'genome': json.dumps({}),
            'region': json.dumps({}),
            'from': 0,
            'to': 0,
            'derived': json.dumps(False),
            'pam': 'GG',
            'uniq_size': 13,
            'full_size': 23,
            'best_size': 7,
            'best_offset': 13,
        }

        self._session_id = random.getrandbits(128)
        self._session_key = 'crispy:session:{0:039d}'.format(self._session_id)

        self._db.hmset(self._session_key, session)


    def _load_from_db(self, session_id):
        "load an existing session from the database"
        self._session_id = session_id
        self._session_key = 'crispy:session:{0:039d}'.format(self._session_id)
        if not self._db.exists(self._session_key):
            raise ValueError("No session with ID {}".format(session_id))


    def _update_timestamp(self):
        "update the timestamp with the current time"
        now = datetime.utcnow().strftime(self._timefmt)
        self._db.hset(self._session_key, 'last_changed', now)


    @property
    def state(self):
        return self._db.hget(self._session_key, 'state')

    @state.setter
    def state(self, value):
        self._update_timestamp()
        self._db.hset(self._session_key, 'state', value)


    @property
    def error(self):
        return self._db.hget(self._session_key, 'error')

    @error.setter
    def error(self, value):
        self._update_timestamp()
        self._db.hset(self._session_key, 'error', value)


    @property
    def asid(self):
        return self._db.hget(self._session_key, 'asid')

    @asid.setter
    def asid(self, value):
        self._update_timestamp()
        self._db.hset(self._session_key, 'asid', value)


    @property
    def filename(self):
        name = self._db.hget(self._session_key, 'filename')
        return name if name != 'None' else None

    @filename.setter
    def filename(self, value):
        self._update_timestamp()
        self._db.hset(self._session_key, 'filename', value)


    @property
    def added(self):
        return self._db.hget(self._session_key, 'added')


    @property
    def last_changed(self):
        return self._db.hget(self._session_key, 'last_changed')


    @property
    def last_changed_datetime(self):
        return datetime.strptime(self._db.hget(self._session_key, 'last_changed'), self._timefmt)


    @property
    def genome(self):
        return json.loads(self._db.hget(self._session_key, 'genome'))

    @genome.setter
    def genome(self, value):
        self._update_timestamp()
        self._db.hset(self._session_key, 'genome', json.dumps(value))


    @property
    def from_coord(self):
        return int(self._db.hget(self._session_key, 'from'))

    @from_coord.setter
    def from_coord(self, value):
        self._update_timestamp()
        self._db.hset(self._session_key, 'from', value)


    @property
    def to_coord(self):
        return int(self._db.hget(self._session_key, 'to'))

    @to_coord.setter
    def to_coord(self, value):
        self._update_timestamp()
        self._db.hset(self._session_key, 'to', value)


    @property
    def region(self):
        return json.loads(self._db.hget(self._session_key, 'region'))

    @region.setter
    def region(self, value):
        self._update_timestamp()
        self._db.hset(self._session_key, 'region', json.dumps(value))


    @property
    def derived(self):
        return json.loads(self._db.hget(self._session_key, 'derived'))

    @derived.setter
    def derived(self, value):
        if not isinstance(value, bool):
            raise ValueError('{} is not a boolean value'.format(value))
        self._db.hset(self._session_key, 'derived', json.dumps(value))


    @property
    def pam(self):
        return self._db.hget(self._session_key, 'pam')

    @pam.setter
    def pam(self, value):
        self._update_timestamp()
        self._db.hset(self._session_key, 'pam', value)


    @property
    def uniq_size(self):
        return int(self._db.hget(self._session_key, 'uniq_size'))

    @uniq_size.setter
    def uniq_size(self, value):
        self._update_timestamp()
        self._db.hset(self._session_key, 'uniq_size', value)


    @property
    def full_size(self):
        return int(self._db.hget(self._session_key, 'full_size'))

    @full_size.setter
    def full_size(self, value):
        self._update_timestamp()
        self._db.hset(self._session_key, 'full_size', value)

    @property
    def best_size(self):
        return int(self._db.hget(self._session_key, 'best_size'))

    @best_size.setter
    def best_size(self, value):
        self._update_timestamp()
        self._db.hset(self._session_key, 'best_size', value)

    @property
    def best_offset(self):
        return int(self._db.hget(self._session_key, 'best_offset'))

    @best_offset.setter
    def best_offset(self, value):
        self._update_timestamp()
        self._db.hset(self._session_key, 'best_offset', value)


class Queue(object):
    """A queue for CRISPy-related jobs"""

    def __init__(self, db, jobtype):
        """Initialize a job queue"""
        self._db = db
        self.jobtype = jobtype

        self._key = 'crispy:queue:{}'.format(self.jobtype)


    @property
    def length(self):
        """Get the length of the queue"""
        return self._db.llen(self._key)


    def submit(self, job):
        """Submit a job to the queue"""
        self._db.lpush(self._key, job._session_key)


    def next(self):
        """Get the next job from the queue"""
        return self._db.rpop(self._key)
