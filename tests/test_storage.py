# -*- encoding: utf-8 -*-
from __future__ import unicode_literals


import pytest
from freezegun import freeze_time
import datetime

from hamsterlib.storage import BaseStore


@pytest.fixture
def store_path():
    return 'foobar'


@pytest.fixture
def basestore(store_path, base_config):
    store = BaseStore(store_path)
    store.config = base_config
    return store


class TestBaseStore():
    def test_init(self, store_path):
        assert BaseStore(store_path).path == store_path

    def test_cleanup(self, basestore):
        with pytest.raises(NotImplementedError):
            basestore.cleanup()


class TestCategoryManager():
    def test_add(self, basestore, category):
        with pytest.raises(NotImplementedError):
            basestore.categories._add(category)

    def test_update(self, basestore, category):
        with pytest.raises(NotImplementedError):
            basestore.categories._update(category)

    def test_remove(self, basestore, category):
        with pytest.raises(NotImplementedError):
            basestore.categories.remove(category)

    def test_get_invalid_pk(self, basestore):
        with pytest.raises(NotImplementedError):
            basestore.categories.get(12)

    def test_get_invalid_pk_type(self, basestore):
        with pytest.raises(NotImplementedError):
            basestore.categories.get_by_name('fooo')

    def test_save_wrong_type(self, basestore, category):
        with pytest.raises(TypeError):
            basestore.categories.save([])

    def test_save_new(self, basestore, category, mocker):
        """Make sure that saving an new category calls ``__add``."""
        basestore.categories._add = mocker.MagicMock(return_value=category)
        try:
            basestore.categories.save(category)
        except NotImplementedError:
            pass
        assert basestore.categories._add.called

    def test_save_existing(self, basestore, category, mocker):
        category.pk = 0
        basestore.categories._update = mocker.MagicMock(return_value=category)
        try:
            basestore.categories.save(category)
        except NotImplementedError:
            pass
        assert basestore.categories._update.called

    def test_get_or_create_existing(self, basestore, category, mocker):
        """Make sure the category is beeing looked up and no new one is created."""
        basestore.categories.get_by_name = mocker.MagicMock(return_value=category)
        basestore.categories._add = mocker.MagicMock(return_value=category)
        try:
            basestore.categories.get_or_create(category.name)
        except NotImplementedError:
            pass
        assert basestore.categories._add.called is False
        assert basestore.categories.get_by_name.called

    def test_get_or_create_new_category(self, basestore, category, mocker):
        """Make sure the category is beeing looked up and new one is created."""
        basestore.categories._add = mocker.MagicMock(return_value=category)
        basestore.categories.get_by_name = mocker.MagicMock(return_value=None)
        try:
            basestore.categories.get_or_create(category.name)
        except NotImplementedError:
            pass
        assert basestore.categories.get_by_name.called
        assert basestore.categories._add.called

    def test_get_all(self, basestore):
        with pytest.raises(NotImplementedError):
            basestore.categories.get_all()


class TestActivityManager:
    def test_save_new(self, basestore, activity, mocker):
        """Make sure that saving an new activity calls ``_add``."""
        basestore.activities._add = mocker.MagicMock(return_value=activity)
        try:
            basestore.activities.save(activity)
        except NotImplementedError:
            pass
        assert basestore.activities._add.called

    def test_save_existing(self, basestore, activity, mocker):
        """Make sure that saving an existing activity calls ``_update``."""
        activity.pk = 0
        basestore.activities._update = mocker.MagicMock(return_value=activity)
        try:
            basestore.activities.save(activity)
        except NotImplementedError:
            pass
        assert basestore.activities._update.called

    def test_get_or_create_existing(self, basestore, activity, mocker):
        basestore.activities.get_by_composite = mocker.MagicMock(return_value=activity)
        basestore.activities.save = mocker.MagicMock(return_value=activity)
        result = basestore.activities.get_or_create(activity.name, activity.category)
        assert result.name == activity.name
        assert basestore.activities.save.called is False

    def test_get_or_create_new(self, basestore, activity, mocker):
        basestore.activities.get_by_composite = mocker.MagicMock(side_effect=KeyError())
        basestore.activities.save = mocker.MagicMock(return_value=activity)
        result = basestore.activities.get_or_create(activity.name, activity.category)
        assert result.name == activity.name
        assert basestore.activities.save.called is True

    def test_add(self, basestore, activity):
        with pytest.raises(NotImplementedError):
            basestore.activities._add(activity)

    def test_update(self, basestore, activity):
        with pytest.raises(NotImplementedError):
            basestore.activities._update(activity)

    def test_remove(self, basestore, activity):
        with pytest.raises(NotImplementedError):
            basestore.activities.remove(activity)

    def test_get_by_composite(self, basestore, activity):
        with pytest.raises(NotImplementedError):
            basestore.activities.get_by_composite(activity.name, activity.category)

    def test_get(self, basestore):
        with pytest.raises(NotImplementedError):
            basestore.activities.get(12)

    def test_get_all(self, basestore):
        with pytest.raises(NotImplementedError):
            basestore.activities.get_all()


class TestFactManager:
    def test_add(self, basestore, fact):
        with pytest.raises(NotImplementedError):
            basestore.facts._add(fact)

    def test_update(self, basestore, fact):
        with pytest.raises(NotImplementedError):
            basestore.facts._update(fact)

    def test_remove(self, basestore, fact):
        with pytest.raises(NotImplementedError):
            basestore.facts.remove(fact)

    def test_get(self, basestore):
        with pytest.raises(NotImplementedError):
            basestore.facts.get(12)

    @pytest.mark.parametrize(('start', 'end', 'filter_term', 'expectation'), [
        (None, None, '', {
            'start': None,
            'end': None}),
        # Various start info
        (datetime.date(2014, 4, 1), None, '', {
            'start': datetime.datetime(2014, 4, 1, 5, 30, 0),
            'end': None}),
        (datetime.time(13, 40, 25), None, '', {
            'start': datetime.datetime(2015, 4, 1, 13, 40, 25),
            'end': None}),
        (datetime.datetime(2014, 4, 1, 13, 40, 25), None, '', {
            'start': datetime.datetime(2014, 4, 1, 13, 40, 25),
            'end': None}),
        # Various end info
        (None, datetime.date(2014, 2, 1), '', {
            'start': None,
            'end': datetime.datetime(2014, 2, 2, 5, 29, 59)}),
        (None, datetime.time(13, 40, 25), '', {
            'start': None,
            'end': datetime.datetime(2015, 4, 1, 13, 40, 25)}),
        (None, datetime.datetime(2014, 4, 1, 13, 40, 25), '', {
            'start': None,
            'end': datetime.datetime(2014, 4, 1, 13, 40, 25)}),
    ])
    @freeze_time('2015-04-01 18:00')
    def test_get_all_various_start_and_end_times(self, basestore, mocker, start, end,
            filter_term, expectation):
        """Test that time conversion matches expectations."""
        basestore.facts._get_all = mocker.MagicMock()
        basestore.facts.get_all(start, end, filter_term)
        assert basestore.facts._get_all.called
        assert basestore.facts._get_all.call_args[0] == (expectation['start'], expectation['end'],
            filter_term)

    @pytest.mark.parametrize(('start', 'end'), [
        (datetime.date(2015, 4, 5), datetime.date(2012, 3, 4)),
        (datetime.datetime(2015, 4, 5, 18, 0, 0), datetime.datetime(2012, 3, 4, 19, 0, 0)),
    ])
    def test_get_all_end_before_start(self, basestore, mocker, start, end):
        """Test that we throw an exception if passed endtime is before start time."""
        with pytest.raises(ValueError):
            basestore.facts.get_all(start, end)

    @pytest.mark.parametrize(('start', 'end'), [
        (datetime.date(2015, 4, 5), '2012-03-04'),
        ('2015-04-05 18:00:00', '2012-03-04 19:00:00'),
    ])
    def test_get_all_invalid_date_types(self, basestore, mocker, start, end):
        """Test that we throw an exception if we recieve invalid date/time objects."""
        with pytest.raises(TypeError):
            basestore.facts.get_all(start, end)

    def test__get_all(self, basestore):
        with pytest.raises(NotImplementedError):
            basestore.facts._get_all()
