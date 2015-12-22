# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

import pytest
from pytest_factoryboy import LazyFixture
import datetime
from freezegun import freeze_time

from hamsterlib.objects import Category, Activity, Fact
from hamsterlib import lib

class TestControler:
    def test_init_no_store(self, base_config):
        base_config['store'] = None
        with pytest.raises(KeyError):
            lib.HamsterControl(base_config)

    def test_get_today_facts(self, controler, persistent_today_fact,
            persistent_not_today_fact):
        result = [fact.pk for fact in controler.get_today_facts()]
        assert persistent_today_fact.pk in result
        assert persistent_not_today_fact.pk not in result

    def test_parse_raw_fact(self, controler, fact_various_raw_facts):
        raw_fact, expectation = fact_various_raw_facts
        fact = controler.parse_raw_fact(raw_fact)
        assert fact.start == expectation['start']
        assert fact.end == expectation['end']
        assert fact.activity.name == expectation['activity']
        if fact.activity.category:
            assert fact.activity.category.name == expectation['category']
        else:
            assert expectation['category'] == None
        assert fact.description == expectation['description']

    def test_parse_raw_fact_invalid_string(self, controler, invalid_raw_fact):
        with pytest.raises(ValueError):
            controler.parse_raw_fact(invalid_raw_fact)


    def test_parse_raw_fact_with_persistent_activity(self, controler,
        raw_fact_with_persistent_activity):
        raw_fact, expectation = raw_fact_with_persistent_activity
        fact = controler.parse_raw_fact(raw_fact)
        assert fact.start == expectation['start']
        assert fact.end == expectation['end']
        assert fact.activity.name == expectation['activity']
        if fact.activity.category:
            assert fact.activity.category._name== expectation['category']
        else:
            assert expectation['category'] == None
        assert fact.description == expectation['description']



    @pytest.mark.parametrize(('raw_fact', 'expectations'), [
        ('-7 foo@bar, palimpalum', {
            'end': None,
            'activity': 'foo',
            'category': 'bar',
            'description': 'palimpalum',
            }
        ),
    ])
    def test_parse_raw_fact_with_delta(self, controler, raw_fact, expectations):
        fact = controler.parse_raw_fact(raw_fact)
        fact_start = fact.start.replace(second=0, microsecond=0)
        expectation_start = (datetime.datetime.now() + datetime.timedelta(
            minutes=-7)).replace(second=0, microsecond=0)
        assert fact_start == expectation_start





