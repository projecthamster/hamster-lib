# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import os.path
import pickle

import pytest
from freezegun import freeze_time
from hamster_lib import Fact


class TestBaseStore():
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
        basestore.categories.get_by_name = mocker.MagicMock(side_effect=KeyError)
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
        result = basestore.activities.get_or_create(activity)
        assert result.name == activity.name
        assert basestore.activities.save.called is False

    def test_get_or_create_new(self, basestore, activity, mocker):
        basestore.activities.get_by_composite = mocker.MagicMock(side_effect=KeyError())
        basestore.activities.save = mocker.MagicMock(return_value=activity)
        result = basestore.activities.get_or_create(activity)
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


class TestTagManager():
    def test_add(self, basestore, tag):
        with pytest.raises(NotImplementedError):
            basestore.tags._add(tag)

    def test_update(self, basestore, tag):
        with pytest.raises(NotImplementedError):
            basestore.tags._update(tag)

    def test_remove(self, basestore, tag):
        with pytest.raises(NotImplementedError):
            basestore.tags.remove(tag)

    def test_get_invalid_pk(self, basestore):
        with pytest.raises(NotImplementedError):
            basestore.tags.get(12)

    def test_get_invalid_pk_type(self, basestore):
        with pytest.raises(NotImplementedError):
            basestore.tags.get_by_name('fooo')

    def test_save_wrong_type(self, basestore, tag):
        with pytest.raises(TypeError):
            basestore.tags.save([])

    def test_save_new(self, basestore, tag, mocker):
        """Make sure that saving an new tag calls ``__add``."""
        basestore.tags._add = mocker.MagicMock(return_value=tag)
        try:
            basestore.tags.save(tag)
        except NotImplementedError:
            pass
        assert basestore.tags._add.called

    def test_save_existing(self, basestore, tag, mocker):
        tag.pk = 0
        basestore.tags._update = mocker.MagicMock(return_value=tag)
        try:
            basestore.tags.save(tag)
        except NotImplementedError:
            pass
        assert basestore.tags._update.called

    def test_get_or_create_existing(self, basestore, tag, mocker):
        """Make sure the tag is beeing looked up and no new one is created."""
        basestore.tags.get_by_name = mocker.MagicMock(return_value=tag)
        basestore.tags._add = mocker.MagicMock(return_value=tag)
        try:
            basestore.tags.get_or_create(tag.name)
        except NotImplementedError:
            pass
        assert basestore.tags._add.called is False
        assert basestore.tags.get_by_name.called

    def test_get_or_create_new_tag(self, basestore, tag, mocker):
        """Make sure the tag is beeing looked up and new one is created."""
        basestore.tags._add = mocker.MagicMock(return_value=tag)
        basestore.tags.get_by_name = mocker.MagicMock(side_effect=KeyError)
        try:
            basestore.tags.get_or_create(tag.name)
        except NotImplementedError:
            pass
        assert basestore.tags.get_by_name.called
        assert basestore.tags._add.called

    def test_get_all(self, basestore):
        with pytest.raises(NotImplementedError):
            basestore.tags.get_all()


class TestFactManager:
    def test_save_tmp_fact(self, basestore, fact, mocker):
        """
        Make sure that passing a fact without end (aka 'ongoing fact') triggers the right method.
        """
        basestore.facts._start_tmp_fact = mocker.MagicMock()
        fact.end = None
        basestore.facts.save(fact)
        assert basestore.facts._start_tmp_fact.called

    def test_save_to_brief_fact(self, basestore, fact):
        """Ensure that a fact with to small delta raises an exception."""
        delta = datetime.timedelta(seconds=(basestore.config['fact_min_delta'] - 1))
        fact.end = fact.start + delta
        with pytest.raises(ValueError):
            basestore.facts.save(fact)

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

    @freeze_time('2015-10-03 14:45')
    def test_get_today(self, basestore, mocker):
        """Make sure that method uses apropiate timeframe. E. g. it respects ``day_start``."""
        basestore.facts.get_all = mocker.MagicMock(return_value=[])
        result = basestore.facts.get_today()
        assert result == []
        assert basestore.facts.get_all.call_args[0] == (datetime.datetime(2015, 10, 3, 5, 30, 0),
            datetime.datetime(2015, 10, 4, 5, 29, 59))

    def test__get_all(self, basestore):
        with pytest.raises(NotImplementedError):
            basestore.facts._get_all()

    def test_start_tmp_fact_new(self, basestore, fact):
        """Make sure that a valid new fact creates persistent file with proper content."""
        fact.end = None
        basestore.facts._start_tmp_fact(fact)
        with open(basestore.facts._get_tmp_fact_path(), 'rb') as fobj:
            new_fact = pickle.load(fobj)
            assert isinstance(new_fact, Fact)
            assert new_fact == fact

    def test_start_tmp_fact_existsing(self, basestore, fact, tmp_fact):
        """Make sure that starting an new 'ongoing fact' if we already got one throws error."""
        fact.end = None
        with pytest.raises(ValueError):
            basestore.facts._start_tmp_fact(fact)

    def test_start_tmp_fact_with_end(self, basestore, fact):
        """Make sure that starting an new 'ongoing fact' if we already got one throws error."""
        with pytest.raises(ValueError):
            basestore.facts._start_tmp_fact(fact)

    @freeze_time('2019-02-01 18:00')
    @pytest.mark.parametrize('hint', (
        None,
        datetime.timedelta(minutes=10),
        datetime.timedelta(minutes=300),
        datetime.timedelta(seconds=-10),
        datetime.timedelta(minutes=-10),
        datetime.datetime(2019, 2, 1, 19),
        datetime.datetime(2019, 2, 1, 17, 59),
    ))
    def test_stop_tmp_fact(self, basestore, base_config, tmp_fact, fact, hint, mocker):
        """
        Make sure we can stop an 'ongoing fact' and that it will have an end set.

        Please note that ever so often it may happen that the factory generates
        a tmp_fact with ``Fact.start`` after our mocked today-date. In order to avoid
        confusion the easies fix is to make sure the mock-today is well in the future.
        """
        if hint:
            if isinstance(hint, datetime.datetime):
                expected_end = hint
            else:
                expected_end = datetime.datetime(2019, 2, 1, 18) + hint
        else:
            expected_end = datetime.datetime.now()

        basestore.facts._add = mocker.MagicMock()
        basestore.facts.stop_tmp_fact(hint)
        assert basestore.facts._add.called
        fact_to_be_added = basestore.facts._add.call_args[0][0]
        assert fact_to_be_added.end == expected_end
        fact_to_be_added.end = None
        assert fact_to_be_added == tmp_fact
        assert os.path.exists(basestore.facts._get_tmp_fact_path()) is False

    def test_stop_tmp_fact_invalid_offset_hint(self, basestore, tmp_fact):
        """Make sure that stopping with an offset hint that results in end>start raises error."""
        offset = (datetime.datetime.now() - tmp_fact.start).total_seconds() + 100
        offset = datetime.timedelta(seconds=-1 * offset)
        with pytest.raises(ValueError):
            basestore.facts.stop_tmp_fact(offset)

    def test_stop_tmp_fact_invalid_datetime_hint(self, basestore, tmp_fact):
        """Make sure that stopping with a datetime hint that results in end>start raises error."""
        with pytest.raises(ValueError):
            basestore.facts.stop_tmp_fact(tmp_fact.start - datetime.timedelta(minutes=30))

    def test_stop_tmp_fact_invalid_hint_type(self, basestore, tmp_fact):
        """Make sure that passing an invalid hint type raises an error."""
        with pytest.raises(TypeError):
            basestore.facts.stop_tmp_fact(str())

    def test_stop_tmp_fact_non_existing(self, basestore):
        """Make sure that trying to call stop when there is no 'ongoing fact' raises error."""
        with pytest.raises(ValueError):
            basestore.facts.stop_tmp_fact()

    def test_get_tmp_fact(self, basestore, tmp_fact, fact):
        """Make sure we return the 'ongoing_fact'."""
        fact = basestore.facts.get_tmp_fact()
        assert fact == fact

    def test_get_tmp_fact_without_ongoing_fact(self, basestore):
        """Make sure that we raise a KeyError if ther is no 'ongoing fact'."""
        with pytest.raises(KeyError):
            basestore.facts.get_tmp_fact()

    def test_update_tmp_fact(self, basestore, tmp_fact, new_fact_values):
        """Make sure the updated fact has the new values."""
        updated_fact = Fact(**new_fact_values(tmp_fact))
        result = basestore.facts.update_tmp_fact(updated_fact)
        assert result == updated_fact

    def test_update_tmp_fact_invalid_type(self, basestore):
        """Make sure that passing a non-Fact instances raises a ``TypeError``."""
        with pytest.raises(TypeError):
            basestore.facts.update_tmp_fact(dict())

    def test_update_tmp_fact_end(self, basestore, fact):
        """Make sure updating with a fact that has ``Fact.end`` raises ``ValueError."""
        fact.end = datetime.datetime.now()
        with pytest.raises(ValueError):
            basestore.facts.update_tmp_fact(fact)

    def test_cancel_tmp_fact(self, basestore, tmp_fact, fact):
        """Make sure we return the 'ongoing_fact'."""
        result = basestore.facts.cancel_tmp_fact()
        assert result is None
        assert os.path.exists(basestore.facts._get_tmp_fact_path()) is False

    def test_cancel_tmp_fact_without_ongoing_fact(self, basestore):
        """Make sure that we raise a KeyError if ther is no 'ongoing fact'."""
        with pytest.raises(KeyError):
            basestore.facts.cancel_tmp_fact()

    def test_get_tmp_fact_path(self, basestore):
        """Make sure the returned path matches our expectation."""
        # [TODO]
        # Would be nice to avoid the code replication. However, we can not
        # simply use fixed strings as path composition is platform dependent.
        expectation = basestore.config['tmpfile_path']
        assert basestore.facts._get_tmp_fact_path() == expectation
