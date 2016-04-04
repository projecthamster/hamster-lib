import datetime

import fauxfactory
import pytest


@pytest.fixture
def base_config(tmpdir):
    """Provide a generic baseline configuration."""
    return {
        'work_dir': tmpdir.mkdir('hamsterlib').strpath,
        'store': 'sqlalchemy',
        'day_start': datetime.time(hour=5, minute=30, second=0),
        'db_path': 'sqlite:///:memory:',
        'tmpfile_name': 'hamsterlib.fact',
    }


# Helper fixtures
@pytest.fixture
def start_end_datetimes_from_offset():
    """Generate start/end datetime tuple with given offset in minutes."""
    def generate(offset):
        end = datetime.datetime.now()
        start = end - datetime.timedelta(minutes=offset)
        return (start, end)
    return generate


# Attribute fixtures (non-parametrized)
@pytest.fixture
def name():
    """Randomized, valid but non-parametrized name string."""
    return fauxfactory.gen_utf8()


@pytest.fixture
def start_end_datetimes(start_end_datetimes_from_offset):
    """Return a start/end-datetime-tuple."""
    return start_end_datetimes_from_offset(15)


@pytest.fixture
def start_datetime():
    """Provide an arbitrary datetime."""
    # [TODO]
    # Fixtures using this could propably be refactored using a cleaner way.
    return datetime.datetime.now()


@pytest.fixture
def description():
    return fauxfactory.gen_iplum()


# New value generation
@pytest.fixture
def new_category_values():
    """Return garanteed modified values for a given category."""
    def modify(category):
        return {
            'name': category.name + 'foobar',
        }
    return modify


@pytest.fixture
def new_fact_values():
    """Provide guaranteed different Fact-values for a given Fact-instance."""
    def modify(fact):
        return {
            'start': fact.start - datetime.timedelta(days=10),
            'end': fact.end - datetime.timedelta(days=10),
            'description': fact.description + 'foobar',
        }
    return modify


# Valid attributes parametrized
@pytest.fixture(params='cyrillic utf8'.split())
def name_string_valid_parametrized(request):
    """Provide a variety of strings that should be valid *names*."""
    return fauxfactory.gen_string(request.param)


@pytest.fixture(params=(None, ''))
def name_string_invalid_parametrized(request):
    """Provide a variety of strings that should be valid *names*."""
    return request.param


@pytest.fixture(params=(
    fauxfactory.gen_string('numeric'),
    fauxfactory.gen_string('alphanumeric'),
    fauxfactory.gen_string('utf8'),
    None,
))
def pk_valid_parametrized(request):
    """Provide a variety of valid primary keys.

    Note:
        At our current stage we do *not* make assumptions about the type of primary key.
        Of cause, this may be a different thing on the backend level!
    """
    return request.param


@pytest.fixture(params=(True, False, 0, 1, '', 'foobar'))
def deleted_valid_parametrized(request):
    return request.param


@pytest.fixture(params='alpha cyrillic latin1 utf8'.split())
def description_valid_parametrized(request):
    """Provide a variety of strings that should be valid *descriptions*."""
    return fauxfactory.gen_string(request.param)


@pytest.fixture(params='alpha cyrillic latin1 utf8'.split())
def tag_list_valid_parametrized(request):
    """Provide a variety of strings that should be valid *descriptions*."""
    return [fauxfactory.gen_string(request.param) for i in range(4)]
