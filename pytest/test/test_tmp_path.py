import pytest

# content of test_tmp_path.py
def test_needsfiles(tmp_path):
    print(tmp_path)
    assert 0

@pytest.fixture()
def postcode():
    return '010'


def test_postcode(postcode):
    assert postcode == '010'
