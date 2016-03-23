## -*- encoding: utf-8 -*-


import pytest
import datetime

from hamsterlib.backends.sqlalchemy import AlchemyCategory, AlchemyActivity, AlchemyFact
from hamsterlib import Category, Activity, Fact


class TestCategoryManager():
    def test_category_add(self, category, alchemy_store):
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
        assert db_instance.name == category.name

    def test_category_update(self, existing_category, new_category_values, alchemy_store):
        """Test that updateing a category works as expected."""
        count_before = alchemy_store.session.query(AlchemyCategory).count()
        new_values = new_category_values(existing_category.as_hamster())
        for key, value in new_values.items():
            assert getattr(existing_category, key) != value
        for key, value in new_values.items():
            setattr(existing_category, key, value)
        result = alchemy_store.categories._update(existing_category.as_hamster())
        count_after = alchemy_store.session.query(AlchemyCategory).count()
        assert count_before == count_after
        for key, value in new_values.items():
            assert getattr(existing_category, key) == value

    def test_remove(self, existing_category, alchemy_store):
        assert alchemy_store.session.query(AlchemyCategory).get(
            existing_category.pk) != None
        result = alchemy_store.categories.remove(existing_category)
        assert result is True
        assert alchemy_store.session.query(AlchemyCategory).get(
            existing_category.pk) == None

    def test_remove_invalid_type(self, alchemy_store):
        with pytest.raises(TypeError):
            alchemy_store.categories.remove({})

    def test_remove_no_pk(self, alchemy_store, category):
        with pytest.raises(ValueError):
            alchemy_store.categories.remove(category)

    def test_get(self, existing_category, alchemy_store):
        result = alchemy_store.categories.get(existing_category.pk)
        assert result.name == existing_category.name

    def test_get_by_name(self, existing_category, alchemy_store):
        result = alchemy_store.categories.get_by_name(existing_category.name)
        assert result.pk == existing_category.pk

    def test_get_by_name_no_string(self, alchemy_store):
        with pytest.raises(TypeError):
            alchemy_store.categories.get_by_name(112314)

    def test_get_or_create_get(self, alchemy_store, existing_category):
        old_count = alchemy_store.session.query(AlchemyCategory).count()
        alchemy_category = alchemy_store.categories.get_or_create(
            existing_category.name)
        new_count = alchemy_store.session.query(AlchemyCategory).count()
        assert old_count == new_count
        assert alchemy_category.pk == existing_category.pk
        assert alchemy_category.name == existing_category.name

    def test_get_or_create_create_bew(self, alchemy_store, category):
        old_count = alchemy_store.session.query(AlchemyCategory).count()
        result = alchemy_store.categories.get_or_create(
            category.name)
        new_count = alchemy_store.session.query(AlchemyCategory).count()
        assert old_count < new_count
        assert result.name == category.name

    def test_get_all(self, alchemy_store, set_of_existing_categories):
        result = alchemy_store.categories.get_all()
        assert len(result) == len(set_of_existing_categories)
        assert len(result) == alchemy_store.session.query(AlchemyCategory).count()


class TestActivityManager():
    def test_save_new(self, activity, alchemy_store):
        assert activity.pk == None
        count_before = alchemy_store.session.query(AlchemyActivity).count()
        result = alchemy_store.activities._add(activity)
        count_after = alchemy_store.session.query(AlchemyActivity).count()
        assert count_before < count_after
        new_activity = alchemy_store.session.query(AlchemyActivity).get(
            result.pk)
        assert result.name== activity.name

    def test_save_existing(self, existing_activity, new_activity_values,
            alchemy_store):
        old_values = existing_activity.as_dict()
        count_before = alchemy_store.session.query(AlchemyActivity).count()
        new_values = new_activity_values(existing_activity.as_hamster())
        for attr, value in new_values.items():
            setattr(existing_activity, attr, value)
        result = alchemy_store.activities.save(existing_activity)
        count_after = alchemy_store.session.query(AlchemyActivity).count()
        assert count_before == count_after
        assert result == existing_activity
        for key, value in new_values.items():
            assert getattr(existing_activity, key) == value

    def test_remove(self, existing_activity, alchemy_store):
        count_before = alchemy_store.session.query(AlchemyActivity).count()
        assert alchemy_store.session.query(AlchemyActivity).get(
            existing_activity.pk) != None
        result = alchemy_store.activities.remove(existing_activity)
        count_after = alchemy_store.session.query(AlchemyActivity).count()
        assert count_after < count_before
        assert result is True
        assert alchemy_store.session.query(AlchemyActivity).get(
            existing_activity.pk) == None

    def test_get_or_create_get(self, alchemy_store, existing_activity):
        activity = existing_activity.as_hamster()
        result = alchemy_store.activities.get_or_create(activity.name,
            activity.category)
        assert activity.name == result.name
        assert activity.pk == result.pk
        assert result.category.pk == activity.category.pk

    def test_get_or_create_new(self, alchemy_store, activity):
        result = alchemy_store.activities.get_or_create(activity.name,
            activity.category)
        assert result.name == activity.name
        assert result.category.name == activity.category.name

    def test_get(self, alchemy_store, existing_activity):
        result = alchemy_store.activities.get(existing_activity.pk)
        assert result.pk == existing_activity.pk
        assert result.name == existing_activity.name
        assert result.category.pk == existing_activity.category.pk

    def test_get_non_existingt(self, alchemy_store):
        result = alchemy_store.activities.get(4)
        assert result == None

    def test_get_by_composite(self, alchemy_store, existing_activity):
        activity = existing_activity.as_hamster()
        result = alchemy_store.activities.get_by_composite(activity.name,
            activity.category)
        assert result.pk == activity.pk
        assert result.name == activity.name
        assert result.category.pk == activity.category.pk

    def test_get_all_without_category(self, alchemy_store, existing_activity):
        """
        Note:
            This method is not meant to return 'all-activities' but rather
            all of a certain category.
        """
        result = alchemy_store.activities.get_all()
        assert len(result) == 0

    def test_get_all_with_category(self, alchemy_store, existing_activity):
        activity = existing_activity.as_hamster()
        result = alchemy_store.activities.get_all(category=activity.category)
        assert len(result) == 1


class TestFactManager():
    def test_save_new(self, fact, alchemy_store):
        count_before = alchemy_store.session.query(AlchemyFact).count()
        result = alchemy_store.facts.save(fact)
        count_after = alchemy_store.session.query(AlchemyFact).count()
        assert count_before < count_after
        assert result.activity.name == fact.activity.name
        assert result.description == fact.description

    def test_save_existing(self, existing_fact, new_fact_values, alchemy_store):
        count_before = alchemy_store.session.query(AlchemyFact).count()
        old_values = existing_fact.as_dict()
        new_values = new_fact_values(existing_fact.as_hamster())
        for key, value in new_values.items():
            setattr(existing_fact, key, value)
        result = alchemy_store.facts.save(existing_fact)
        count_after = alchemy_store.session.query(AlchemyFact).count()
        assert count_before == count_after
        result_dict = result.as_dict()
        for key, value in new_values.items():
            assert result_dict[key] == value

    def test_remove(self, existing_fact, alchemy_store):
        count_before = alchemy_store.session.query(AlchemyFact).count()
        result = alchemy_store.facts.remove(existing_fact)
        count_after = alchemy_store.session.query(AlchemyFact).count()
        assert count_after < count_before
        assert result == True
        assert alchemy_store.session.query(AlchemyFact).get(existing_fact.pk) == None

    def test_get(self, existing_fact, alchemy_store):
        result = alchemy_store.facts.get(existing_fact.pk)
        assert result == existing_fact

    def test_get_all(self, set_of_existing_facts, alchemy_store):
        result = alchemy_store.facts.get_all()
        assert len(result) == len(set_of_existing_facts)
        assert len(result) == alchemy_store.session.query(AlchemyFact).count()

    def test_get_all_with_datetimes(self, start_datetime, set_of_existing_facts, alchemy_store):
        start = start_datetime
        end = start_datetime + datetime.timedelta(hours=5)
        result = alchemy_store.facts.get_all(start=start, end=end)
        assert len(result) == 1
