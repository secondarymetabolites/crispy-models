import pytest
from crispy_models import Queue, Session


@pytest.fixture
def db():
    """fake redis database"""
    from mockredis import mock_redis_client
    return mock_redis_client(decode_responses=True)


def test_init(db):
    queue = Queue(db, 'test')
    assert isinstance(queue, Queue)
    assert queue._key == 'crispy:queue:test'
    assert queue.jobtype == 'test'


def test_length(db):
    queue = Queue(db, 'test')
    assert queue.length == 0
    db.lpush('crispy:queue:test', 'crispy:session:1234')
    assert queue.length == 1


def test_submit(db):
    queue = Queue(db, 'test')
    assert queue.length == 0
    session = Session(db, from_id='test123')
    queue.submit(session)
    assert queue.length == 1


def test_next(db):
    queue = Queue(db, 'test')
    session = Session(db, from_id='test123')
    queue.submit(session)
    key = queue.next()
    assert key == session._session_key
    key = queue.next()
    assert key is None


def test_repeatability(db):
    first = Queue(db, 'test')
    second = Queue(db, 'test')
    session = Session(db, from_id='test123')
    first.submit(session)
    assert second.length == 1
