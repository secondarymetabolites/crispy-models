"Data models for CRISPy API"

from datetime import datetime
import json
import random
from typing import Any, Dict, Optional, Union

from redis import Redis


class Session(object):
    """A CRISPy web session object"""
    def __init__(self, db: Redis, from_id: Optional[str] = None, from_file: Optional[str] = None,
                 session_id: Optional[int] = None):
        self._db = db
        self._timefmt = '%Y-%m-%d %H:%M:%S'

        if session_id is not None:
            self._load_from_db(session_id)
        else:
            self._create(from_id, from_file)

    def _create(self, from_id: Optional[str], from_file: Optional[str]):
        "create a new Session object"
        if from_id is None and from_file is None:
            raise ValueError("Need either id or file to start a session")

        if from_id is not None and from_file is not None:
            raise ValueError("Can't set both id and file for a session")

        now = datetime.utcnow().strftime(self._timefmt)
        session: Dict[str, Union[str, int]] = {
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

        self._db.hset(self._session_key, mapping=session)  # type: ignore

    def _load_from_db(self, session_id: int):
        "load an existing session from the database"
        self._session_id = session_id
        self._session_key = f'crispy:session:{self._session_id:039d}'
        if not self._db.exists(self._session_key):
            raise ValueError("No session with ID {}".format(session_id))

    def _update_timestamp(self):
        "update the timestamp with the current time"
        now = datetime.utcnow().strftime(self._timefmt)
        self._db.hset(self._session_key, 'last_changed', now)

    @property
    def state(self) -> str:
        ret = self._db.hget(self._session_key, 'state')
        assert ret
        return ret

    @state.setter
    def state(self, value):
        self._update_timestamp()
        self._db.hset(self._session_key, 'state', value)

    @property
    def error(self) -> str:
        ret = self._db.hget(self._session_key, 'error')
        assert ret is not None
        return ret

    @error.setter
    def error(self, value):
        self._update_timestamp()
        self._db.hset(self._session_key, 'error', value)

    @property
    def asid(self) -> Optional[str]:
        asid = self._db.hget(self._session_key, 'asid')
        if not asid:
            return None
        return asid if asid != "None" else None

    @asid.setter
    def asid(self, value):
        self._update_timestamp()
        self._db.hset(self._session_key, 'asid', value)

    @property
    def filename(self) -> Optional[str]:
        name = self._db.hget(self._session_key, 'filename')
        if not name:
            return None
        return name if name != "None" else None

    @filename.setter
    def filename(self, value):
        self._update_timestamp()
        self._db.hset(self._session_key, 'filename', value)

    @property
    def added(self) -> str:
        ret = self._db.hget(self._session_key, 'added')
        assert ret
        return ret

    @property
    def last_changed(self) -> str:
        ret = self._db.hget(self._session_key, 'last_changed')
        assert ret
        return ret

    @property
    def last_changed_datetime(self) -> datetime:
        ret = self._db.hget(self._session_key, 'last_changed')
        assert ret
        return datetime.strptime(ret, self._timefmt)

    @property
    def genome(self) -> Dict[str, Any]:
        ret = self._db.hget(self._session_key, 'genome')
        assert ret
        return json.loads(ret)

    @genome.setter
    def genome(self, value):
        self._update_timestamp()
        self._db.hset(self._session_key, 'genome', json.dumps(value))

    @property
    def from_coord(self) -> int:
        ret = self._db.hget(self._session_key, 'from')
        assert ret
        return int(ret)

    @from_coord.setter
    def from_coord(self, value):
        self._update_timestamp()
        self._db.hset(self._session_key, 'from', value)

    @property
    def to_coord(self) -> int:
        ret = self._db.hget(self._session_key, 'to')
        assert ret
        return int(ret)

    @to_coord.setter
    def to_coord(self, value):
        self._update_timestamp()
        self._db.hset(self._session_key, 'to', value)

    @property
    def region(self) -> Dict[str, Any]:
        ret = self._db.hget(self._session_key, 'region')
        assert ret
        return json.loads(ret)

    @region.setter
    def region(self, value):
        self._update_timestamp()
        self._db.hset(self._session_key, 'region', json.dumps(value))

    @property
    def derived(self) -> bool:
        ret = self._db.hget(self._session_key, 'derived')
        assert ret
        return json.loads(ret)

    @derived.setter
    def derived(self, value):
        if not isinstance(value, bool):
            raise ValueError('{} is not a boolean value'.format(value))
        self._db.hset(self._session_key, 'derived', json.dumps(value))

    @property
    def pam(self) -> str:
        ret = self._db.hget(self._session_key, 'pam')
        assert ret
        return ret

    @pam.setter
    def pam(self, value):
        self._update_timestamp()
        self._db.hset(self._session_key, 'pam', value)

    @property
    def uniq_size(self) -> int:
        ret = self._db.hget(self._session_key, 'uniq_size')
        assert ret
        return int(ret)

    @uniq_size.setter
    def uniq_size(self, value):
        self._update_timestamp()
        self._db.hset(self._session_key, 'uniq_size', value)

    @property
    def full_size(self) -> int:
        ret = self._db.hget(self._session_key, 'full_size')
        assert ret
        return int(ret)

    @full_size.setter
    def full_size(self, value):
        self._update_timestamp()
        self._db.hset(self._session_key, 'full_size', value)

    @property
    def best_size(self) -> int:
        ret = self._db.hget(self._session_key, 'best_size')
        assert ret
        return int(ret)

    @best_size.setter
    def best_size(self, value):
        self._update_timestamp()
        self._db.hset(self._session_key, 'best_size', value)

    @property
    def best_offset(self) -> int:
        ret = self._db.hget(self._session_key, 'best_offset')
        assert ret
        return int(ret)

    @best_offset.setter
    def best_offset(self, value):
        self._update_timestamp()
        self._db.hset(self._session_key, 'best_offset', value)


class Queue(object):
    """A queue for CRISPy-related jobs"""

    def __init__(self, db: Redis, jobtype: str):
        """Initialize a job queue"""
        self._db = db
        self.jobtype = jobtype

        self._key = f'crispy:queue:{self.jobtype}'

    @property
    def length(self) -> int:
        """Get the length of the queue"""
        return self._db.llen(self._key)

    def submit(self, job):
        """Submit a job to the queue"""
        self._db.lpush(self._key, job._session_key)

    def next(self) -> str:
        """Get the next job from the queue"""
        return self._db.rpop(self._key)
