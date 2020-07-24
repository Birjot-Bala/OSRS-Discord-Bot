# test_formatter_discord.py
# contains tests for formatter_discord.py

import pytest

import osrs_discord_bot.formatter_discord as f


def test_formatSearch():
    assert f.formatSearch('a,2.5 G / ') == 'a25g'


@pytest.mark.parametrize("frac", ["1/2", "1.0/2.0"])
def test_fraction2Float(frac):
    assert f.fraction2Float(frac) == 0.5

    
def test_raises_exception_on_non_fraction_arguments():
    with pytest.raises(ValueError):
        f.fraction2Float('abc')


def test_formatDiscord():
    assert f.formatDiscord('test') == '```test```'