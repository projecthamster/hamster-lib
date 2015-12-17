import pytest
from hamsterlib.backends.sqlalchemy.alchemy import (AlchemyCategory,
                                                    AlchemyActivity,
                                                    AlchemyFact)


class TestAlchemyCategory():
    def test_init_not_hamster_category(self):
        with pytest.raises(TypeError):
            AlchemyCategory({})


class TestAlchemyActivity():
    def test_init_not_hamster_activity(self):
        with pytest.raises(TypeError):
            AlchemyActivity({})


class TestAlchemyFact():
    def test_init_not_hamster_fact(self):
        with pytest.raises(TypeError):
            AlchemyFact({})
