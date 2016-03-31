# -*- encoding: utf-8 -*-

from __future__ import unicode_literals
from builtins import str

import pytest
import datetime

from hamsterlib.backends.sqlalchemy import AlchemyCategory, AlchemyActivity, AlchemyFact


class TestCategoryManager():
    def test_add_new(self, alchemy_store, alchemy_category_factory):
        """
        Our manager methods return the persistant instance as hamster objects.
        As we want to make sure that we compare our expectations against the
        raw saved object, we look it up explicitly again.
        """
        assert alchemy_store.session.query(AlchemyCategory).count() == 0
        category = alchemy_category_factory.build()
        assert alchemy_store.session.query(AlchemyCategory).count() == 0
        result = alchemy_store.categories._add(category)
        assert alchemy_store.session.query(AlchemyCategory).count() == 1
        db_instance = alchemy_store.session.query(AlchemyCategory).get(result.pk)
        assert category.equal_fields(db_instance)
        assert category != db_instance

#    def test_add_existing_name(self, alchemy_store, alchemy_alchemy_category):
#        """Make sure that adding a alchemy_category with a name that is already present gives an error."""
#        with pytest.raises(ValueError):
#            alchemy_store.categories._add(alchemy_alchemy_category.as_hamster())
#
#    def test_add_with_pk(self, alchemy_store, alchemy_alchemy_category):
#        """Make sure that adding a alchemy_category that already got an PK raisess an exception."""
#        alchemy_category = alchemy_alchemy_category.as_hamster()
#        alchemy_category.name += 'foobar'
#        with pytest.raises(ValueError):
#            alchemy_store.categories._add(alchemy_category)
#
#    def test_update(self, alchemy_store, alchemy_alchemy_category, new_alchemy_category_values):
#        """Test that updateing a alchemy_category works as expected."""
#        count_before = alchemy_store.session.query(AlchemyCategory).count()
#        alchemy_category = alchemy_alchemy_category.as_hamster()
#        new_values = new_alchemy_category_values(alchemy_category)
#        for key, value in new_values.items():
#            assert getattr(alchemy_category, key) != value
#        for key, value in new_values.items():
#            setattr(alchemy_category, key, value)
#        alchemy_store.categories._update(alchemy_category)
#        updated_alchemy_category = alchemy_store.session.query(AlchemyCategory).get(alchemy_category.pk)
#        count_after = alchemy_store.session.query(AlchemyCategory).count()
#        assert count_before == count_after
#        assert alchemy_alchemy_category.as_hamster().equal_fields(updated_alchemy_category)
#
#    def test_update_without_pk(self, alchemy_store, alchemy_alchemy_category):
#        alchemy_alchemy_category.pk = None
#        with pytest.raises(ValueError):
#            alchemy_store.categories._update(alchemy_alchemy_category.as_hamster())
#
#    def test_update_existing_name(self, alchemy_store, alchemy_alchemy_category_factory):
#        """Make sure that renaming a given alchemy_category to a name already taken throws an error."""
#        alchemy_category_1, alchemy_category_2 = (alchemy_alchemy_category_factory(), alchemy_alchemy_category_factory())
#        alchemy_category = alchemy_category_2.as_hamster()
#        alchemy_category.name = alchemy_category_1.name
#        with pytest.raises(ValueError):
#            alchemy_store.categories._update(alchemy_category)
#
#    def test_remove(self, alchemy_alchemy_category, alchemy_store):
#        """Make sure passing a valid alchemy_category removes it from the db."""
#        assert alchemy_store.session.query(AlchemyCategory).get(
#            alchemy_alchemy_category.pk) is not None
#        result = alchemy_store.categories.remove(alchemy_alchemy_category.as_hamster())
#        assert result is None
#        assert alchemy_store.session.query(AlchemyCategory).get(
#            alchemy_alchemy_category.pk) is None
#
#    def test_remove_invalid_type(self, alchemy_store):
#        """Make sure passing an invalid type raises error."""
#        with pytest.raises(TypeError):
#            alchemy_store.categories.remove({})
#
#    def test_remove_no_pk(self, alchemy_store, alchemy_category):
#        """Ensure that passing a alchemy_category without an PK raises an error."""
#        with pytest.raises(ValueError):
#            alchemy_store.categories.remove(alchemy_category)
#
#    def test_get_existing_pk(self, alchemy_alchemy_category, alchemy_store):
#        """Make sure method retrieves corresponding object."""
#        result = alchemy_store.categories.get(alchemy_alchemy_category.pk)
#        assert result == alchemy_alchemy_category
#
#    def test_get_non_existing_pk(self, alchemy_store, alchemy_alchemy_category):
#        """Make sure we throw an error if PK can not be resolved."""
#        with pytest.raises(KeyError):
#            alchemy_store.categories.get(alchemy_alchemy_category.pk + 1)
#
#    def test_get_by_name(self, alchemy_alchemy_category, alchemy_store):
#        """Make sure a alchemy_category can be retrieved by name."""
#        result = alchemy_store.categories.get_by_name(alchemy_alchemy_category.name)
#        assert result == alchemy_alchemy_category
#
#    def test_get_all(self, alchemy_store, set_of_existing_categories):
#        result = alchemy_store.categories.get_all()
#        assert len(result) == len(set_of_existing_categories)
#        assert len(result) == alchemy_store.session.query(AlchemyCategory).count()
#
#    # Test convinience methods.
#    def test_get_or_create_get(self, alchemy_store, alchemy_alchemy_category):
#        """Test that if we pass a alchemy_category of existing name, we just return it."""
#        old_count = alchemy_store.session.query(AlchemyCategory).count()
#        result = alchemy_store.categories.get_or_create(alchemy_alchemy_category)
#        new_count = alchemy_store.session.query(AlchemyCategory).count()
#        assert old_count == new_count
#        assert result == alchemy_alchemy_category
#
#    def test_get_or_create_new_name(self, alchemy_store, alchemy_category):
#        """Make sure that passing a alchemy_category with new name creates and returns new instance."""
#        old_count = alchemy_store.session.query(AlchemyCategory).count()
#        result = alchemy_store.categories.get_or_create(alchemy_category)
#        new_count = alchemy_store.session.query(AlchemyCategory).count()
#        assert old_count < new_count
#        assert result.equal_fields(alchemy_category)
#
#
#class TestActivityManager():
#
#
##    def test_get_or_create_get(self, alchemy_store, existing_alchemy_activity):
##        alchemy_activity = existing_alchemy_activity.as_hamster()
##        result = alchemy_store.activities.get_or_create(alchemy_activity.name,
##            alchemy_activity.alchemy_category)
##        assert alchemy_activity.name == result.name
##        assert alchemy_activity.pk == result.pk
##        assert result.alchemy_category.pk == alchemy_activity.alchemy_category.pk
##
##    def test_get_or_create_new(self, alchemy_store, alchemy_activity):
##        result = alchemy_store.activities.get_or_create(alchemy_activity.name,
##            alchemy_activity.alchemy_category)
##        print(alchemy_activity)
##        print(result)
##        assert result.name == alchemy_activity.name
##        assert result.alchemy_category.name == alchemy_activity.alchemy_category.name
#    #def test_save_new(self, alchemy_activity, alchemy_store):
#    #    # [TODO]
#    #    # This should not be needed as ``save`` is a basestore method.
#    #    assert alchemy_activity.pk is None
#    #    count_before = alchemy_store.session.query(AlchemyActivity).count()
#    #    result = alchemy_store.activities._add(alchemy_activity)
#    #    count_after = alchemy_store.session.query(AlchemyActivity).count()
#    #    assert count_before < count_after
#    #    assert result.name == alchemy_activity.name
#
##    #def test_save_existing(self, existing_alchemy_activity, new_alchemy_activity_values,
##    #        alchemy_store):
##    #    # [TODO]
##    #    # This should not be needed as ``save`` is a basestore method.
##    #    count_before = alchemy_store.session.query(AlchemyActivity).count()
##    #    new_values = new_alchemy_activity_values(existing_alchemy_activity.as_hamster())
##    #    for attr, value in new_values.items():
##    #        setattr(existing_alchemy_activity, attr, value)
##    #    result = alchemy_store.activities.save(existing_alchemy_activity)
##    #    count_after = alchemy_store.session.query(AlchemyActivity).count()
##    #    assert count_before == count_after
##    #    assert result == existing_alchemy_activity
##    #    for key, value in new_values.items():
##    #        assert getattr(existing_alchemy_activity, key) == value
#
#    def test_add_new_with_new_alchemy_category(self, alchemy_store, alchemy_activity):
#        """Test that adding a new alchemy_activity with new alchemy_category creates both."""
#        old_alchemy_activity_count = alchemy_store.session.query(AlchemyActivity).count()
#        old_alchemy_category_count = alchemy_store.session.query(AlchemyCategory).count()
#        result = alchemy_store.activities._add(alchemy_activity)
#        db_instance = alchemy_store.session.query(AlchemyActivity).get(result.pk)
#        new_alchemy_activity_count = alchemy_store.session.query(AlchemyActivity).count()
#        new_alchemy_category_count = alchemy_store.session.query(AlchemyCategory).count()
#        assert old_alchemy_activity_count < new_alchemy_activity_count
#        assert old_alchemy_category_count < new_alchemy_category_count
#        assert db_instance.as_hamster().equal_fields(alchemy_activity)
#        # This should not be needed
#        assert db_instance.as_hamster().alchemy_category.equal_fields(alchemy_activity.alchemy_category)
#
#    def test_add_new_with_alchemy_alchemy_category(self, alchemy_store, alchemy_activity, alchemy_alchemy_category):
#        """Test that adding a new alchemy_activity with existing alchemy_category does not create a new one."""
#        alchemy_activity.alchemy_category = alchemy_alchemy_category.as_hamster()
#        old_alchemy_activity_count = alchemy_store.session.query(AlchemyActivity).count()
#        old_alchemy_category_count = alchemy_store.session.query(AlchemyCategory).count()
#        result = alchemy_store.activities._add(alchemy_activity)
#        db_instance = alchemy_store.session.query(AlchemyActivity).get(result.pk)
#        new_alchemy_activity_count = alchemy_store.session.query(AlchemyActivity).count()
#        new_alchemy_category_count = alchemy_store.session.query(AlchemyCategory).count()
#        assert old_alchemy_activity_count < new_alchemy_activity_count
#        assert old_alchemy_category_count == new_alchemy_category_count
#        assert db_instance.as_hamster().equal_fields(alchemy_activity)
#
#    def test_add_new_with_existing_name_and_alchemy_category(self, alchemy_store, alchemy_activity,
#            alchemy_alchemy_activity):
#        """Test that adding a new alchemy_activity_with_existing_composite_key_throws error."""
#        alchemy_activity.name = alchemy_alchemy_activity.name
#        alchemy_activity.alchemy_category.name = alchemy_alchemy_activity.alchemy_category.name
#        old_alchemy_activity_count = alchemy_store.session.query(AlchemyActivity).count()
#        old_alchemy_category_count = alchemy_store.session.query(AlchemyCategory).count()
#        with pytest.raises(ValueError):
#            alchemy_store.activities._add(alchemy_activity)
#        new_alchemy_activity_count = alchemy_store.session.query(AlchemyActivity).count()
#        new_alchemy_category_count = alchemy_store.session.query(AlchemyCategory).count()
#        assert old_alchemy_activity_count == new_alchemy_activity_count
#        assert old_alchemy_category_count == new_alchemy_category_count
#
#    def test_add_with_pk(self, alchemy_store, alchemy_alchemy_activity):
#        """Make sure that adding an alchemy_activity with a PK raises error."""
#        with pytest.raises(ValueError):
#            alchemy_store.activities._add(alchemy_alchemy_activity)
#
#    def test_update_without_pk(self, alchemy_store, alchemy_activity):
#        """Make sure that calling update without a PK raises exception."""
#        with pytest.raises(ValueError):
#            alchemy_store.activities._update(alchemy_activity)
#
#    def test_update_with_existing_name_and_alchemy_category_name(self, alchemy_store,
#            alchemy_activity, alchemy_alchemy_activity):
#        """Make sure that calling update with a taken name/alchemy_category.name raises exception."""
#        alchemy_activity.name = alchemy_alchemy_activity.name
#        alchemy_activity.alchemy_category.name = alchemy_alchemy_activity.alchemy_category.name
#        with pytest.raises(ValueError):
#            alchemy_store.activities._update(alchemy_activity)
#
#    def test_update_with_existing_alchemy_category(self, alchemy_store, alchemy_alchemy_activity,
#            alchemy_alchemy_category_factory):
#        """Test that updateting an alchemy_activity with existing alchemy_category does not create a new one."""
#        alchemy_activity = alchemy_alchemy_activity.as_hamster()
#        alchemy_activity.alchemy_category = alchemy_alchemy_category_factory().as_hamster()
#        old_alchemy_activity_count = alchemy_store.session.query(AlchemyActivity).count()
#        old_alchemy_category_count = alchemy_store.session.query(AlchemyCategory).count()
#        alchemy_store.activities._update(alchemy_activity)
#        db_instance = alchemy_store.session.query(AlchemyActivity).get(alchemy_activity.pk)
#        new_alchemy_activity_count = alchemy_store.session.query(AlchemyActivity).count()
#        new_alchemy_category_count = alchemy_store.session.query(AlchemyCategory).count()
#        assert old_alchemy_activity_count == new_alchemy_activity_count
#        assert old_alchemy_category_count == new_alchemy_category_count
#        assert db_instance.as_hamster().equal_fields(alchemy_activity)
#
#    def test_update_name(self, alchemy_store, alchemy_alchemy_activity,
#            name_string_valid_parametrized):
#        """Test that updateting an alchemy_activity with existing alchemy_category does not create a new one."""
#        alchemy_activity = alchemy_alchemy_activity.as_hamster()
#        alchemy_activity.name = name_string_valid_parametrized
#        alchemy_store.activities._update(alchemy_activity)
#        db_instance = alchemy_store.session.query(AlchemyActivity).get(alchemy_activity.pk)
#        assert db_instance.as_hamster().equal_fields(alchemy_activity)
#
#    def test_remove_existing(self, alchemy_alchemy_activity, alchemy_store):
#        """Make sure removing an existsing alchemy_activity works as intended."""
#        count_before = alchemy_store.session.query(AlchemyActivity).count()
#        assert alchemy_store.session.query(AlchemyActivity).get(
#            alchemy_alchemy_activity.pk) is not None
#        result = alchemy_store.activities.remove(alchemy_alchemy_activity)
#        count_after = alchemy_store.session.query(AlchemyActivity).count()
#        assert count_after < count_before
#        assert result is True
#        assert alchemy_store.session.query(AlchemyActivity).get(
#            alchemy_alchemy_activity.pk) is None
#
#    def test_remove_no_pk(self, alchemy_store, alchemy_activity):
#        """Make sure that trying to remove an alchemy_activity without a PK raises errror."""
#        with pytest.raises(ValueError):
#            alchemy_store.activities.remove(alchemy_activity)
#
#    def test_remove_invalid_pk(self, alchemy_store, alchemy_alchemy_activity):
#        """Test that removing of a non-existent key raises error."""
#        alchemy_activity = alchemy_alchemy_activity.as_hamster()
#        alchemy_activity.pk = alchemy_alchemy_activity.pk + 1
#        with pytest.raises(KeyError):
#            alchemy_store.activities.remove(alchemy_activity)
#
#    def test_get_existing(self, alchemy_store, alchemy_alchemy_activity):
#        """Make sure that retrieving an existing alchemy_activity by pk works as intended."""
#        result = alchemy_store.activities.get(alchemy_alchemy_activity.pk)
#        assert result == alchemy_alchemy_activity.as_hamster()
#        assert result is not alchemy_alchemy_activity
#
#    def test_get_existing_raw(self, alchemy_store, alchemy_alchemy_activity):
#        """Make sure that retrieving an existing alchemy alchemy_activity by pk works as intended."""
#        result = alchemy_store.activities.get(alchemy_alchemy_activity.pk, raw=True)
#        assert result == alchemy_alchemy_activity
#        assert result is alchemy_alchemy_activity
#
#    def test_get_non_existing(self, alchemy_store):
#        """Make sure quering for a non existent PK raises error."""
#        with pytest.raises(KeyError):
#            alchemy_store.activities.get(4)
#
#    @pytest.mark.parametrize('raw', (True, False))
#    def test_get_by_composite_valid(self, alchemy_store, alchemy_alchemy_activity, raw):
#        """Make sure that querying for a valid name/alchemy_category combo succeeds."""
#        alchemy_activity = alchemy_alchemy_activity.as_hamster()
#        result = alchemy_store.activities.get_by_composite(alchemy_activity.name,
#            alchemy_activity.alchemy_category, raw=raw)
#        if raw:
#            result == alchemy_alchemy_activity
#            result is alchemy_alchemy_activity
#        else:
#            assert result == alchemy_activity
#            result is not alchemy_activity
#
#    def test_get_by_composite_invalid_alchemy_category(self, alchemy_store, alchemy_alchemy_activity, alchemy_category):
#        """Make sure that querying with an invalid alchemy_category raises errror."""
#        alchemy_activity = alchemy_alchemy_activity.as_hamster()
#        with pytest.raises(KeyError):
#            alchemy_store.activities.get_by_composite(alchemy_activity.name, alchemy_category)
#
#    def test_get_by_composite_invalid_name(self, alchemy_store, alchemy_alchemy_activity,
#            name_string_valid_parametrized):
#        """Make sure that querying with an invalid alchemy_category raises errror."""
#        alchemy_activity = alchemy_alchemy_activity.as_hamster()
#        with pytest.raises(KeyError):
#            alchemy_store.activities.get_by_composite(name_string_valid_parametrized,
#                alchemy_activity.alchemy_category)
#
#    def test_get_all_without_alchemy_category(self, alchemy_store, alchemy_alchemy_activity):
#        """
#        Note:
#            This method is not meant to return 'all-activities' but rather
#            all of a certain alchemy_category.
#        """
#        result = alchemy_store.activities.get_all()
#        assert len(result) == 0
#
#    def test_get_all_with_alchemy_category(self, alchemy_store, alchemy_alchemy_activity):
#        """Make sure that activities matching the given alchemy_category are returned."""
#        alchemy_activity = alchemy_alchemy_activity.as_hamster()
#        result = alchemy_store.activities.get_all(alchemy_category=alchemy_activity.alchemy_category)
#        assert len(result) == 1
#
#    def test_get_all_with_search_term(self, alchemy_store, alchemy_alchemy_activity):
#        """Make sure that activities matching the given term ass name are returned."""
#        alchemy_activity = alchemy_alchemy_activity.as_hamster()
#        result = alchemy_store.activities.get_all(alchemy_category=alchemy_activity.alchemy_category,
#            search_term=alchemy_activity.name)
#        assert len(result) == 1
#
#
#class TestFactManager():
#
#    def test_add_new_valid_fact_new_alchemy_activity(self, alchemy_store, fact):
#        """Make sure that adding a new valid fact with a new alchemy_activity works as intended."""
#        old_fact_count = alchemy_store.session.query(AlchemyFact).count()
#        old_alchemy_activity_count = alchemy_store.session.query(AlchemyCategory).count()
#        result = alchemy_store.facts._add(fact)
#        db_instance = alchemy_store.session.query(AlchemyFact).get(result.pk)
#        new_fact_count = alchemy_store.session.query(AlchemyFact).count()
#        new_alchemy_activity_count = alchemy_store.session.query(AlchemyActivity).count()
#        assert old_fact_count < new_fact_count
#        assert old_alchemy_activity_count < new_alchemy_activity_count
#        assert db_instance.as_hamster().equal_fields(fact)
#
#    def test_add_new_valid_fact_existing_alchemy_activity(self, alchemy_store, fact, alchemy_alchemy_activity):
#        """Make sure that adding a new valid fact with an existing alchemy_activity works as intended."""
#        #fact.alchemy_activity = existing_alchemy_activity.as_hamster()
#        fact.alchemy_activity = alchemy_alchemy_activity.as_hamster()
#        old_fact_count = alchemy_store.session.query(AlchemyFact).count()
#        old_alchemy_activity_count = alchemy_store.session.query(AlchemyCategory).count()
#        result = alchemy_store.facts._add(fact)
#        db_instance = alchemy_store.session.query(AlchemyFact).get(result.pk)
#        new_fact_count = alchemy_store.session.query(AlchemyFact).count()
#        new_alchemy_activity_count = alchemy_store.session.query(AlchemyActivity).count()
#        assert old_fact_count < new_fact_count
#        assert old_alchemy_activity_count == new_alchemy_activity_count
#        assert db_instance.as_hamster().equal_fields(fact)
#
#    def test_add_with_pk(self, alchemy_store, fact):
#        """Make sure that passing a fact with a PK raises error."""
#        fact.pk = 101
#        with pytest.raises(ValueError):
#            alchemy_store.facts._add(fact)
#
#    def test_add_occupied_timewindow(self, alchemy_store, fact, alchemy_fact):
#        """
#        Make sure that passing a fact with a timewindow that already has a fact raisess error.
#        """
#        fact.start = alchemy_fact.start - datetime.timedelta(days=4)
#        fact.end = alchemy_fact.start + datetime.timedelta(minutes=15)
#        with pytest.raises(ValueError):
#            alchemy_store.facts._add(fact)
#
#    def test_update_fact_new_valid_timeframe(self, alchemy_store, alchemy_fact, new_fact_values):
#        """Make sure updating an existing fact works as expected."""
#        fact = alchemy_fact.as_hamster()
#        new_values = new_fact_values(fact)
#        fact.pk = alchemy_fact.pk
#        fact.start = new_values['start']
#        fact.end = new_values['end']
#        old_fact_count = alchemy_store.session.query(AlchemyFact).count()
#        old_alchemy_activity_count = alchemy_store.session.query(AlchemyCategory).count()
#        result = alchemy_store.facts._update(fact)
#        db_instance = alchemy_store.session.query(AlchemyFact).get(result.pk)
#        new_fact_count = alchemy_store.session.query(AlchemyFact).count()
#        new_alchemy_activity_count = alchemy_store.session.query(AlchemyActivity).count()
#        assert old_fact_count == new_fact_count
#        assert old_alchemy_activity_count == new_alchemy_activity_count
#        assert db_instance.as_hamster().equal_fields(fact)
#
#
##    def test_save_new(self, fact, alchemy_store):
##        count_before = alchemy_store.session.query(AlchemyFact).count()
##        result = alchemy_store.facts.save(fact)
##        count_after = alchemy_store.session.query(AlchemyFact).count()
##        assert count_before < count_after
##        assert result.alchemy_activity.name == fact.alchemy_activity.name
##        assert result.description == fact.description
##
##    def test_save_existing(self, existing_fact, new_fact_values, alchemy_store):
##        count_before = alchemy_store.session.query(AlchemyFact).count()
##        new_values = new_fact_values(existing_fact.as_hamster())
##        for key, value in new_values.items():
##            setattr(existing_fact, key, value)
##        result = alchemy_store.facts.save(existing_fact)
##        count_after = alchemy_store.session.query(AlchemyFact).count()
##        assert count_before == count_after
##        result_dict = result.as_dict()
##        for key, value in new_values.items():
##            assert result_dict[key] == value
##
#    def test_remove(self, alchemy_fact, alchemy_store):
#        count_before = alchemy_store.session.query(AlchemyFact).count()
#        result = alchemy_store.facts.remove(alchemy_fact)
#        count_after = alchemy_store.session.query(AlchemyFact).count()
#        assert count_after < count_before
#        assert result is True
#        assert alchemy_store.session.query(AlchemyFact).get(alchemy_fact.pk) is None
#
##    def test_get(self, alchemy_fact, alchemy_store):
##        result = alchemy_store.facts.get(alchemy_fact.pk)
##        assert result == alchemy_fact
##
##    def test_get_all(self, set_of_alchemy_facts, alchemy_store):
##        result = alchemy_store.facts.get_all()
##        assert len(result) == len(set_of_alchemy_facts)
##        assert len(result) == alchemy_store.session.query(AlchemyFact).count()
##
##    def test_get_all_with_datetimes(self, start_datetime, set_of_alchemy_facts, alchemy_store):
##        start = start_datetime
##        end = start_datetime + datetime.timedelta(hours=5)
##        result = alchemy_store.facts.get_all(start=start, end=end)
##        assert len(result) == 1
#
#    def test_timeframe_is_free_false_start(self, alchemy_store, alchemy_fact):
#        """Make sure that a start within our timeframe returns expected result."""
#        start = alchemy_fact.start + datetime.timedelta(hours=1)
#        end = alchemy_fact.start + datetime.timedelta(days=20)
#        assert alchemy_store.facts._timeframe_is_free(start, end) is False
#
#    def test_timeframe_is_free_false_end(self, alchemy_store, alchemy_fact):
#        """Make sure that a end within our timeframe returns expected result."""
#        start = alchemy_fact.start - datetime.timedelta(days=20)
#        end = alchemy_fact.start + datetime.timedelta(hours=1)
#        assert alchemy_store.facts._timeframe_is_free(start, end) is False
#
#    def test_timeframe_is_free_true(self, alchemy_store, alchemy_fact):
#        """Make sure that a valid timeframe returns expected result."""
#        start = alchemy_fact.start - datetime.timedelta(days=20)
#        end = alchemy_fact.start - datetime.timedelta(seconds=1)
#        assert alchemy_store.facts._timeframe_is_free(start, end)
#
#
#
