from project import player_at_exit
from project import valid_sizes
from project import valid_gen_speed
from project import valid_seed
import pytest

# ... Ok, those don't really check much.
# I'm frankly not sure how to test a curses program with pytest
# or anything else, especially with it having random generation.
# But here is some at least.

def test_playerAtExit():
    assert player_at_exit(75, 1, (75, 1)) == True
    assert player_at_exit(1, 1, (75, 1)) == False

def test_sizes():
    assert valid_sizes("11", 15) == 11
    assert valid_sizes("5", 235) == 5
    with pytest.raises(ValueError):
        valid_sizes("wasd", 15)
    with pytest.raises(ValueError):
        valid_sizes("10", 15)

def test_speed():
    assert valid_gen_speed("100") == 100
    assert valid_gen_speed("1000") == 1000
    with pytest.raises(ValueError):
        valid_gen_speed("2500")
    with pytest.raises(ValueError):
        valid_gen_speed("wasd")

def test_seed():
    assert valid_seed("0") == 0
    assert valid_seed("9000") == 9000
    with pytest.raises(ValueError):
        valid_seed("123456")
    with pytest.raises(ValueError):
        valid_seed("wasd")
