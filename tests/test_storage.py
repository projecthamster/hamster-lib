# -*- encoding: utf-8 -*-
from __future__ import unicode_literals


import pytest

from hamsterlib.storage import BaseStore


@pytest.fixture
def store_path():
    return 'foobar'


@pytest.fixture
def basestore(store_path):
    return BaseStore(store_path)


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

    def test_save_new(self, basestore, category):
        with pytest.raises(NotImplementedError):
            basestore.categories.save(category)

    def test_save_existing(self, basestore, category):
        category.pk = 0
        with pytest.raises(NotImplementedError):
            basestore.categories.save(category)

    def test_get_or_create_existing(self, basestore, category):
        with pytest.raises(NotImplementedError):
            basestore.categories.get_or_create(category.name)

    def test_get_all(self, basestore):
        with pytest.raises(NotImplementedError):
            basestore.categories.get_all()


class TestActivityManager:
    def test_add(self, basestore, activity):
        with pytest.raises(NotImplementedError):
            basestore.activities._add(activity)

    def test_update(self, basestore, activity):
        with pytest.raises(NotImplementedError):
            basestore.activities._update(activity)

    def test_remove(self, basestore, activity):
        with pytest.raises(NotImplementedError):
            basestore.activities.remove(activity)

    def test_get(self, basestore):
        with pytest.raises(NotImplementedError):
            basestore.activities.get(12)


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

    def test_get_all(self, basestore):
        with pytest.raises(NotImplementedError):
            basestore.facts.get_all()
