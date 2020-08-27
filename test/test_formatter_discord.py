# test_formatter_discord.py
# contains tests for formatter_discord.py

import pytest

import osrs_discord_bot.formatter_discord as f


def test_format_search():
    assert f.format_search('a,2.5 G / ') == 'a25g'


@pytest.mark.parametrize("frac", ["1/2", "1.0/2.0"])
def test_fraction_to_float(frac):
    assert f.fraction_to_float(frac) == 0.5

    
def test_raises_exception_on_non_fraction_arguments():
    with pytest.raises(ValueError):
        f.fraction_to_float('abc')


def test_format_discord():
    assert f.format_discord('test') == '```test```'
