# test_scope.py

import time
import pytest

def test_multi_scope(sess_scope, mod_scope, func_scope):
    pass

@pytest.mark.usefixtures('class_scope')
class TestClassScope:
    def test_1(self):
        time.sleep(1)
        pass

    def test_2(self):
        time.sleep(2)
        pass
