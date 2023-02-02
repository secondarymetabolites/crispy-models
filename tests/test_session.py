import pytest
from datetime import datetime
from crispy_models import Session


@pytest.fixture
def db():
    from fakeredis import FakeRedis
    return FakeRedis(encoding="utf-8", decode_responses=True)


@pytest.fixture
def fake_session(db):
    "Set up a fake database session"
    def setup(session_id):
        session_key = 'crispy:session:{0:039}'.format(session_id)
        db_session = {
            'state': 'pending',
            'error': '',
            'asid': 'testing',
            'filename': 'None',
            'added': '2015-10-08 12:34:56',
            'last_changed': '2015-10-08 12:34:57',
            'genome': '{}',
            'region': '{}',
            'from': 0,
            'to': 0,
            'derived': 'false',
            'pam': 'GG',
            'uniq_size': 13,
            'full_size': 23,
        }
        db.hset(session_key, mapping=db_session)
        return db_session

    return setup

def test_init(db):
    now = datetime.utcnow()
    session = Session(db, from_id='testid')
    session_key = 'crispy:session:{0:039}'.format(session._session_id)
    assert session._session_key == session_key
    db_session = db.hgetall(session_key)
    assert db_session['state'] == 'pending'
    assert db_session['asid'] == 'testid'
    assert db_session['filename'] == 'None'
    assert db_session['added'] == now.strftime('%Y-%m-%d %H:%M:%S')
    assert db_session['genome'] == '{}'
    assert db_session['region'] == '{}'
    assert db_session['from'] == '0'
    assert db_session['to'] == '0'
    assert db_session['derived'] == 'false'
    assert db_session['pam'] == 'GG'
    assert db_session['uniq_size'] == '13'
    assert db_session['full_size'] == '23'


def test_init_from_id(db, fake_session):
    session_id = 123456789
    db_session = fake_session(session_id)

    session = Session(db, session_id=session_id)
    assert session.asid == db_session['asid']
    assert session.filename is None
    assert session.state == db_session['state']
    assert session.error == db_session['error']
    assert session.added == db_session['added']
    assert session.last_changed == db_session['last_changed']
    assert session.genome == {}
    assert session.region == {}
    assert session.derived is False
    assert session.pam == 'GG'
    assert session.uniq_size == 13
    assert session.full_size == 23


def test_init_from_invalid_id(db):
    with pytest.raises(ValueError):
        session = Session(db, session_id=172342)


def test_init_without_id_or_file(db):
    with pytest.raises(ValueError):
        session = Session(db)


def test_init_with_bot_id_and_file(db):
    with pytest.raises(ValueError):
        session = Session(db, from_id=12345, from_file='test')


def test_state(db):
    session = Session(db, from_id='testid')
    assert session.state == 'pending'
    session.state = 'done'
    assert session.state == 'done'


def test_asid(db):
    session = Session(db, from_id='testid')
    assert session.asid == 'testid'
    session.asid = 'otherid'
    assert session.asid == 'otherid'


def test_filename(db):
    session = Session(db, from_id='testid')
    assert session.filename is None
    session.filename = 'test'
    assert session.filename == 'test'
    session = Session(db, from_file='othertest')
    assert session.filename == 'othertest'


def test_genome(db):
    session = Session(db, from_id='testid')
    assert session.genome == {}
    genome = {
        'locus': 'NC_003888',
        'definition': 'Streptomyces coelicolor A3(2) chromosome, complete genome.',
        'source': 'Streptomyces coelicolor A3(2)',
        'orfs': [
            {'id': 'SCO4711', 'start': 5132708, 'end': 5132995, 'strand': 1, 'gene': 'rpsQ'},
        ],
        'clusters': [
            {'start': 235986, 'end': 271084, 'name': "Cluster 3", 'type': "Lantipeptide",
             'description': "Sanglifehrin_A_biosynthetic_gene_cluster (4% of genes show similarity)"},
        ],
    }
    session.genome = genome
    assert session.genome == genome


def test_coordinates(db):
    session = Session(db, from_id='testid')
    assert session.from_coord == 0
    assert session.to_coord == 0
    session.from_coord = 23
    session.to_coord = 42
    assert session.from_coord == 23
    assert session.to_coord == 42


def test_region(db):
    session = Session(db, from_id='testid')
    assert session.region == {}
    region = {
        'from': 23,
        'to': 42,
    }
    session.region = region
    assert session.region == region


def test_error(db):
    session = Session(db, from_id='testid')
    assert session.error == ''
    session.error = 'something bad happened'
    assert session.error == 'something bad happened'


def test_last_changed(db, fake_session):
    session_id = 12345678
    db_session = fake_session(session_id)

    session = Session(db, session_id=session_id)
    assert session.last_changed == db_session['last_changed']

    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    session.state = 'done'
    assert session.last_changed == now


def test_last_changed_datetime(db, fake_session):
    session_id = 12345678
    db_session = fake_session(session_id)

    session = Session(db, session_id=session_id)
    now = datetime.strptime(db_session['last_changed'], '%Y-%m-%d %H:%M:%S')
    assert session.last_changed_datetime == now


def test_derived(db):
    session = Session(db, from_id='testid')
    assert session.derived is False
    session.derived = True
    assert session.derived is True


def test_derived_raises(db):
    session = Session(db, from_id='testid')
    with pytest.raises(ValueError):
        session.derived = 5


def test_pam(db):
    session = Session(db, from_id='testid')
    assert session.pam == 'GG'
    session.pam = 'TT'
    assert session.pam == 'TT'


def test_uniq_size(db):
    session = Session(db, from_id='testid')
    assert session.uniq_size == 13
    session.uniq_size = 17
    assert session.uniq_size == 17


def test_full_size(db):
    session = Session(db, from_id='testid')
    assert session.full_size == 23
    session.full_size = 17
    assert session.full_size == 17
