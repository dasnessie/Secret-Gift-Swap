import random
from utils import get_pairing_with_probabilities, _generate_pairing, _accept_pairing


def test_generate_pairing():
    participants = ["a", "b", "c"]
    assert _generate_pairing(participants) in [
        {("a", "b"), ("b", "c"), ("c", "a")},
        {("a", "c"), ("b", "a"), ("c", "b")},
    ]
    assert participants == ["a", "b", "c"]


def test_accept_pairing():
    pairing = {("a", "b"), ("b", "c"), ("c", "a")}
    pairs_with_probability = {("a", "b"): 0.5}

    random.seed(6740)

    selected_count = 0
    for i in range(100):
        if _accept_pairing(pairs_with_probability, pairing):
            selected_count += 1

    assert selected_count == 47


def test_get_pairing_with_probabilities():
    participants = ["a", "b", "c"]
    assert get_pairing_with_probabilities(participants) in [
        {("a", "b"), ("b", "c"), ("c", "a")},
        {("a", "c"), ("b", "a"), ("c", "b")},
    ]
