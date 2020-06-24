# test_functions.py

import pytest
import functions as f

def test_fraction2Float():
    assert f.fraction2Float('1/2') == 0.5

def test_raises_exception_on_non_fraction_arguments():
    with pytest.raises(ValueError):
        f.fraction2Float('abc')

