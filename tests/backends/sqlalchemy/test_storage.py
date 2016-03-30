# -*- encoding: utf-8 -*-

from __future__ import unicode_literals
from builtins import str
from future.utils import python_2_unicode_compatible

import pytest
import datetime

from hamsterlib.backends.sqlalchemy import AlchemyCategory, AlchemyActivity, AlchemyFact


@python_2_unicode_compatible
class TestCategoryManager():
    def test_add_new(self, category, alchemy_store):
        """
        Our manager methods return the persistant instance as hamster objects.
        As we want to make sure that we compare our expectations against the
        raw saved object, we look it up explicitly again.
        """
        count_before = alchemy_store.session.query(AlchemyCategory).count()
        result = alchemy_store.categories._add(category)
        count_after = alchemy_store.session.query(AlchemyCategory).count()
        assert count_before < count_after
        db_instance = alchemy_store.session.query(AlchemyCategory).get(result.pk)
        assert category.equal_fields(db_instance)
        assert category != db_instance

    def test_add_existing_name(self, alchemy_store, existing_category):
        """Make sure that adding a category with a name that is already present gives an error."""
        with pytest.raises(ValueError):
            alchemy_store.categories._add(existing_category.as_hamster())

    def test_add_with_pk(self, alchemy_store, existing_category):
        """Make sure that adding a category that already got an PK raisess an exception."""
        existing_category.name += 'foobar'
        with pytest.raises(ValueError):
            alchemy_store.categories._add(existing_category.as_hamster())

    def test_update(self, existing_category, new_category_values, alchemy_store):
        """Test that updateing a category works as expected."""
        count_before = alchemy_store.session.query(AlchemyCategory).count()
        new_values = new_category_values(existing_category.as_hamster())
        for key, value in new_values.items():
            assert getattr(existing_category, key) != value
        for key, value in new_values.items():
            setattr(existing_category, key, value)
        alchemy_store.categories._update(existing_category.as_hamster())
        updated_category = alchemy_store.session.query(AlchemyCategory).get(existing_category.pk)
        count_after = alchemy_store.session.query(AlchemyCategory).count()
        assert count_before == count_after
        assert existing_category.as_hamster().equal_fields(updated_category)

    def test_update_without_pk(self, alchemy_store, existing_category):
        existing_category.pk = None
        with pytest.raises(ValueError):
            alchemy_store.categories._update(existing_category.as_hamster())

    def test_existing_name(self, alchemy_store, existing_category_factory):
        """Make sure that renaming a given category to a name already taken throws an error."""
        category_1, category_2 = (existing_category_factory(), existing_category_factory())
        category_2.name = category_1.name
        with pytest.raises(ValueError):
            alchemy_store.categories._update(category_2.as_hamster())

    def test_remove(self, existing_category, alchemy_store):
        """Make sure passing a valid category removes it from the db."""
        assert alchemy_store.session.query(AlchemyCategory).get(
            existing_category.pk) is not None
        result = alchemy_store.categories.remove(existing_category.as_hamster())
        assert result is None
        assert alchemy_store.session.query(AlchemyCategory).get(
            existing_category.pk) is None

    def test_remove_invalid_type(self, alchemy_store):
        """Make sure passing an invalid type raises error."""
        with pytest.raises(TypeError):
            alchemy_store.categories.remove({})

    def test_remove_no_pk(self, alchemy_store, category):
        """Ensure that passing a category without an PK raises an error."""
        with pytest.raises(ValueError):
            alchemy_store.categories.remove(category)

    def test_get_existing_pk(self, existing_category, alchemy_store):
        """Make sure method retrieves corresponding object."""
        result = alchemy_store.categories.get(existing_category.pk)
        assert result == existing_category

    def test_get_non_existing_pk(self, alchemy_store, existing_category):
        """Make sure we throw an error if PK can not be resolved."""
        with pytest.raises(KeyError):
            alchemy_store.categories.get(existing_category.pk + 1)

    def test_get_by_name(self, existing_category, alchemy_store):
        """Make sure a category can be retrieved by name."""
        result = alchemy_store.categories.get_by_name(existing_category.name)
        assert result == existing_category

    def test_get_all(self, alchemy_store, set_of_existing_categories):
        result = alchemy_store.categories.get_all()
        assert len(result) == len(set_of_existing_categories)
        assert len(result) == alchemy_store.session.query(AlchemyCategory).count()

    # Test convinience methods.
    def test_get_or_create_get(self, alchemy_store, existing_category):
        """Test that if we pass a category of existing name, we just return it."""
        old_count = alchemy_store.session.query(AlchemyCategory).count()
        result = alchemy_store.categories.get_or_create(existing_category)
        new_count = alchemy_store.session.query(AlchemyCategory).count()
        assert old_count == new_count
        assert result == existing_category

    def test_get_or_create_new_name(self, alchemy_store, category):
        """Make sure that passing a category with new name creates and returns new instance."""
        old_count = alchemy_store.session.query(AlchemyCategory).count()
        result = alchemy_store.categories.get_or_create(category)
        new_count = alchemy_store.session.query(AlchemyCategory).count()
        assert old_count < new_count
        assert result.equal_fields(category)


@python_2_unicode_compatible
class TestActivityManager():


#    def test_get_or_create_get(self, alchemy_store, existing_activity):
#        activity = existing_activity.as_hamster()
#        result = alchemy_store.activities.get_or_create(activity.name,
#            activity.category)
#        assert activity.name == result.name
#        assert activity.pk == result.pk
#        assert result.category.pk == activity.category.pk
#
#    def test_get_or_create_new(self, alchemy_store, activity):
#        result = alchemy_store.activities.get_or_create(activity.name,
#            activity.category)
#        print(activity)
#        print(result)
#        assert result.name == activity.name
#        assert result.category.name == activity.category.name
    #def test_save_new(self, activity, alchemy_store):
    #    # [TODO]
    #    # This should not be needed as ``save`` is a basestore method.
    #    assert activity.pk is None
    #    count_before = alchemy_store.session.query(AlchemyActivity).count()
    #    result = alchemy_store.activities._add(activity)
    #    count_after = alchemy_store.session.query(AlchemyActivity).count()
    #    assert count_before < count_after
    #    assert result.name == activity.name

#    #def test_save_existing(self, existing_activity, new_activity_values,
#    #        alchemy_store):
#    #    # [TODO]
#    #    # This should not be needed as ``save`` is a basestore method.
#    #    count_before = alchemy_store.session.query(AlchemyActivity).count()
#    #    new_values = new_activity_values(existing_activity.as_hamster())
#    #    for attr, value in new_values.items():
#    #        setattr(existing_activity, attr, value)
#    #    result = alchemy_store.activities.save(existing_activity)
#    #    count_after = alchemy_store.session.query(AlchemyActivity).count()
#    #    assert count_before == count_after
#    #    assert result == existing_activity
#    #    for key, value in new_values.items():
#    #        assert getattr(existing_activity, key) == value

    def test_add_new_with_new_category(self, alchemy_store, activity):
        """Test that adding a new activity with new category creates both."""
        old_activity_count = alchemy_store.session.query(AlchemyActivity).count()
        old_category_count = alchemy_store.session.query(AlchemyCategory).count()
        result = alchemy_store.activities._add(activity)
        db_instance = alchemy_store.session.query(AlchemyActivity).get(result.pk)
        new_activity_count = alchemy_store.session.query(AlchemyActivity).count()
        new_category_count = alchemy_store.session.query(AlchemyCategory).count()
        assert old_activity_count < new_activity_count
        assert old_category_count < new_category_count
        assert db_instance.as_hamster().equal_fields(activity)
        # This should not be needed
        assert db_instance.as_hamster().category.equal_fields(activity.category)

    def test_add_new_with_existing_category(self, alchemy_store, activity, existing_category):
        """Test that adding a new activity with existing category does not create a new one."""
        activity.category = existing_category.as_hamster()
        old_activity_count = alchemy_store.session.query(AlchemyActivity).count()
        old_category_count = alchemy_store.session.query(AlchemyCategory).count()
        result = alchemy_store.activities._add(activity)
        db_instance = alchemy_store.session.query(AlchemyActivity).get(result.pk)
        new_activity_count = alchemy_store.session.query(AlchemyActivity).count()
        new_category_count = alchemy_store.session.query(AlchemyCategory).count()
        assert old_activity_count < new_activity_count
        assert old_category_count == new_category_count
        assert db_instance.as_hamster().equal_fields(activity)

    def test_add_new_with_existing_name_and_category(self, alchemy_store, activity,
            existing_activity):
        """Test that adding a new activity_with_existing_composite_key_throws error."""
        activity.name = existing_activity.name
        activity.category.name = existing_activity.category.name
        old_activity_count = alchemy_store.session.query(AlchemyActivity).count()
        old_category_count = alchemy_store.session.query(AlchemyCategory).count()
        with pytest.raises(ValueError):
            alchemy_store.activities._add(activity)
        new_activity_count = alchemy_store.session.query(AlchemyActivity).count()
        new_category_count = alchemy_store.session.query(AlchemyCategory).count()
        assert old_activity_count == new_activity_count
        assert old_category_count == new_category_count

    def test_add_with_pk(self, alchemy_store, existing_activity):
        """Make sure that adding an activity with a PK raises error."""
        with pytest.raises(ValueError):
            alchemy_store.activities._add(existing_activity)

    def test_update_without_pk(self, alchemy_store, activity):
        """Make sure that calling update without a PK raises exception."""
        with pytest.raises(ValueError):
            alchemy_store.activities._update(activity)

    def test_update_with_existing_name_and_category_name(self, alchemy_store,
            activity, existing_activity):
        """Make sure that calling update with a taken name/category.name raises exception."""
        activity.name = existing_activity.name
        activity.category.name = existing_activity.category.name
        with pytest.raises(ValueError):
            alchemy_store.activities._update(activity)

    def test_update_with_existing_category(self, alchemy_store, existing_activity,
            existing_category):
        """Test that updateting an activity with existing category does not create a new one."""
        activity = existing_activity.as_hamster()
        activity.category = existing_category.as_hamster()
        old_activity_count = alchemy_store.session.query(AlchemyActivity).count()
        old_category_count = alchemy_store.session.query(AlchemyCategory).count()
        alchemy_store.activities._update(activity)
        db_instance = alchemy_store.session.query(AlchemyActivity).get(activity.pk)
        new_activity_count = alchemy_store.session.query(AlchemyActivity).count()
        new_category_count = alchemy_store.session.query(AlchemyCategory).count()
        assert old_activity_count == new_activity_count
        assert old_category_count == new_category_count
        assert db_instance.as_hamster().equal_fields(activity)

    def test_update_name(self, alchemy_store, existing_activity,
            name_string_valid_parametrized):
        """Test that updateting an activity with existing category does not create a new one."""
        activity = existing_activity.as_hamster()
        activity.name = name_string_valid_parametrized
        alchemy_store.activities._update(activity)
        db_instance = alchemy_store.session.query(AlchemyActivity).get(activity.pk)
        assert db_instance.as_hamster().equal_fields(activity)

    def test_remove_existing(self, existing_activity, alchemy_store):
        """Make sure removing an existsing activity works as intended."""
        count_before = alchemy_store.session.query(AlchemyActivity).count()
        assert alchemy_store.session.query(AlchemyActivity).get(
            existing_activity.pk) is not None
        result = alchemy_store.activities.remove(existing_activity)
        count_after = alchemy_store.session.query(AlchemyActivity).count()
        assert count_after < count_before
        assert result is True
        assert alchemy_store.session.query(AlchemyActivity).get(
            existing_activity.pk) is None

    def test_remove_no_pk(self, alchemy_store, activity):
        """Make sure that trying to remove an activity without a PK raises errror."""
        with pytest.raises(ValueError):
            alchemy_store.activities.remove(activity)

    def test_remove_invalid_pk(self, alchemy_store, existing_activity):
        """Test that removing of a non-existent key raises error."""
        activity = existing_activity.as_hamster()
        activity.pk = existing_activity.pk + 1
        with pytest.raises(KeyError):
            alchemy_store.activities.remove(activity)

    def test_get_existing(self, alchemy_store, existing_activity):
        """Make sure that retrieving an existing activity by pk works as intended."""
        result = alchemy_store.activities.get(existing_activity.pk)
        assert result == existing_activity.as_hamster()
        assert result is not existing_activity

    def test_get_existing_raw(self, alchemy_store, existing_activity):
        """Make sure that retrieving an existing alchemy activity by pk works as intended."""
        result = alchemy_store.activities.get(existing_activity.pk, raw=True)
        assert result == existing_activity
        assert result is existing_activity

    def test_get_non_existing(self, alchemy_store):
        """Make sure quering for a non existent PK raises error."""
        with pytest.raises(KeyError):
            alchemy_store.activities.get(4)

    @pytest.mark.parametrize('raw', (True, False))
    def test_get_by_composite_valid(self, alchemy_store, existing_activity, raw):
        """Make sure that querying for a valid name/category combo succeeds."""
        activity = existing_activity.as_hamster()
        result = alchemy_store.activities.get_by_composite(activity.name,
            activity.category, raw=raw)
        if raw:
            result == existing_activity
            result is existing_activity
        else:
            assert result == activity
            result is not activity

    def test_get_by_composite_invalid_category(self, alchemy_store, existing_activity, category):
        """Make sure that querying with an invalid category raises errror."""
        activity = existing_activity.as_hamster()
        with pytest.raises(KeyError):
            alchemy_store.activities.get_by_composite(activity.name, category)

    def test_get_by_composite_invalid_name(self, alchemy_store, existing_activity,
            name_string_valid_parametrized):
        """Make sure that querying with an invalid category raises errror."""
        activity = existing_activity.as_hamster()
        with pytest.raises(KeyError):
            alchemy_store.activities.get_by_composite(name_string_valid_parametrized,
                activity.category)

    def test_get_all_without_category(self, alchemy_store, existing_activity):
        """
        Note:
            This method is not meant to return 'all-activities' but rather
            all of a certain category.
        """
        result = alchemy_store.activities.get_all()
        assert len(result) == 0

    def test_get_all_with_category(self, alchemy_store, existing_activity):
        """Make sure that activities matching the given category are returned."""
        activity = existing_activity.as_hamster()
        result = alchemy_store.activities.get_all(category=activity.category)
        assert len(result) == 1

    def test_get_all_with_search_term(self, alchemy_store, existing_activity):
        """Make sure that activities matching the given term ass name are returned."""
        activity = existing_activity.as_hamster()
        result = alchemy_store.activities.get_all(category=activity.category,
            search_term=activity.name)
        assert len(result) == 1


@python_2_unicode_compatible
class TestFactManager():

    def test_add_new_valid_fact_new_activity(self, alchemy_store, fact):
        """Make sure that adding a new valid fact with a new activity works as intended."""
        old_fact_count = alchemy_store.session.query(AlchemyFact).count()
        old_activity_count = alchemy_store.session.query(AlchemyCategory).count()
        result = alchemy_store.facts._add(fact)
        db_instance = alchemy_store.session.query(AlchemyFact).get(result.pk)
        new_fact_count = alchemy_store.session.query(AlchemyFact).count()
        new_activity_count = alchemy_store.session.query(AlchemyActivity).count()
        assert old_fact_count < new_fact_count
        assert old_activity_count < new_activity_count
        assert db_instance.as_hamster().equal_fields(fact)

    def test_add_new_valid_fact_existing_activity(self, alchemy_store, fact, existing_activity):
        """Make sure that adding a new valid fact with an existing activity works as intended."""
        #fact.activity = existing_activity.as_hamster()
        fact.activity = existing_activity.as_hamster()
        old_fact_count = alchemy_store.session.query(AlchemyFact).count()
        old_activity_count = alchemy_store.session.query(AlchemyCategory).count()
        result = alchemy_store.facts._add(fact)
        db_instance = alchemy_store.session.query(AlchemyFact).get(result.pk)
        new_fact_count = alchemy_store.session.query(AlchemyFact).count()
        new_activity_count = alchemy_store.session.query(AlchemyActivity).count()
        assert old_fact_count < new_fact_count
        assert old_activity_count == new_activity_count
        assert db_instance.as_hamster().equal_fields(fact)

    def test_add_with_pk(self, alchemy_store, fact):
        """Make sure that passing a fact with a PK raises error."""
        fact.pk = 101
        with pytest.raises(ValueError):
            alchemy_store.facts._add(fact)

    def test_add_occupied_timewindow(self, alchemy_store, fact, existing_fact):
        """
        Make sure that passing a fact with a timewindow that already has a fact raisess error.
        """
        fact.start = existing_fact.start - datetime.timedelta(days=4)
        fact.end = existing_fact.start + datetime.timedelta(minutes=15)
        with pytest.raises(ValueError):
            alchemy_store.facts._add(fact)

    def test_update_fact_new_valid_timeframe(self, alchemy_store, existing_fact, new_fact_values):
        """Make sure updating an existing fact works as expected."""
        fact = existing_fact.as_hamster()
        new_values = new_fact_values(fact)
        fact.pk = existing_fact.pk
        fact.start = new_values['start']
        fact.end = new_values['end']
        old_fact_count = alchemy_store.session.query(AlchemyFact).count()
        old_activity_count = alchemy_store.session.query(AlchemyCategory).count()
        result = alchemy_store.facts._update(fact)
        db_instance = alchemy_store.session.query(AlchemyFact).get(result.pk)
        new_fact_count = alchemy_store.session.query(AlchemyFact).count()
        new_activity_count = alchemy_store.session.query(AlchemyActivity).count()
        assert old_fact_count == new_fact_count
        assert old_activity_count == new_activity_count
        assert db_instance.as_hamster().equal_fields(fact)


#    def test_save_new(self, fact, alchemy_store):
#        count_before = alchemy_store.session.query(AlchemyFact).count()
#        result = alchemy_store.facts.save(fact)
#        count_after = alchemy_store.session.query(AlchemyFact).count()
#        assert count_before < count_after
#        assert result.activity.name == fact.activity.name
#        assert result.description == fact.description
#
#    def test_save_existing(self, existing_fact, new_fact_values, alchemy_store):
#        count_before = alchemy_store.session.query(AlchemyFact).count()
#        new_values = new_fact_values(existing_fact.as_hamster())
#        for key, value in new_values.items():
#            setattr(existing_fact, key, value)
#        result = alchemy_store.facts.save(existing_fact)
#        count_after = alchemy_store.session.query(AlchemyFact).count()
#        assert count_before == count_after
#        result_dict = result.as_dict()
#        for key, value in new_values.items():
#            assert result_dict[key] == value
#
    def test_remove(self, existing_fact, alchemy_store):
        count_before = alchemy_store.session.query(AlchemyFact).count()
        result = alchemy_store.facts.remove(existing_fact)
        count_after = alchemy_store.session.query(AlchemyFact).count()
        assert count_after < count_before
        assert result is True
        assert alchemy_store.session.query(AlchemyFact).get(existing_fact.pk) is None

#    def test_get(self, existing_fact, alchemy_store):
#        result = alchemy_store.facts.get(existing_fact.pk)
#        assert result == existing_fact
#
#    def test_get_all(self, set_of_existing_facts, alchemy_store):
#        result = alchemy_store.facts.get_all()
#        assert len(result) == len(set_of_existing_facts)
#        assert len(result) == alchemy_store.session.query(AlchemyFact).count()
#
#    def test_get_all_with_datetimes(self, start_datetime, set_of_existing_facts, alchemy_store):
#        start = start_datetime
#        end = start_datetime + datetime.timedelta(hours=5)
#        result = alchemy_store.facts.get_all(start=start, end=end)
#        assert len(result) == 1

    def test_timeframe_is_free_false_start(self, alchemy_store, existing_fact):
        """Make sure that a start within our timeframe returns expected result."""
        start = existing_fact.start + datetime.timedelta(hours=1)
        end = existing_fact.start + datetime.timedelta(days=20)
        assert alchemy_store.facts._timeframe_is_free(start, end) is False

    def test_timeframe_is_free_false_end(self, alchemy_store, existing_fact):
        """Make sure that a end within our timeframe returns expected result."""
        start = existing_fact.start - datetime.timedelta(days=20)
        end = existing_fact.start + datetime.timedelta(hours=1)
        assert alchemy_store.facts._timeframe_is_free(start, end) is False

    def test_timeframe_is_free_true(self, alchemy_store, existing_fact):
        """Make sure that a valid timeframe returns expected result."""
        start = existing_fact.start - datetime.timedelta(days=20)
        end = existing_fact.start - datetime.timedelta(seconds=1)
        assert alchemy_store.facts._timeframe_is_free(start, end)



