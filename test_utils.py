import random
import pytest
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

    assert get_pairing_with_probabilities(
        participants=["a", "b", "c", "d"],
        pairs_with_probabilities={
            ("a", "b"): 0,
            ("a", "c"): 0,
            ("b", "c"): 0,
            ("b", "d"): 0,
            ("c", "a"): 0,
            ("c", "d"): 0,
            ("d", "a"): 0,
            ("d", "b"): 0,
        },
    ) == {("a", "d"), ("b", "a"), ("c", "b"), ("d", "c")}

    random.seed(6851)

    assert get_pairing_with_probabilities(
        participants=["a", "b", "c", "d"],
        pairs_with_probabilities={
            ("a", "b"): 0.5,
            ("b", "d"): 0.5,
            ("c", "d"): 0.5,
            ("d", "a"): 0.5,
        },
    ) == {("c", "d"), ("a", "c"), ("d", "b"), ("b", "a")}

    with pytest.raises(ValueError):
        get_pairing_with_probabilities(
            participants=["a", "b", "c", "d"],
            pairs_with_probabilities={("a", "b"): 0, ("a", "c"): 0, ("a", "d"): 0},
        )

    random.seed(6851)

    with pytest.warns(
        UserWarning, match="Could not generate a pairing with given constraints"
    ):
        assert get_pairing_with_probabilities(
            participants=["a", "b", "c", "d"],
            pairs_with_probabilities={
                ("a", "b"): 0.001,
                ("a", "c"): 0.001,
                ("a", "d"): 0.001,
            },
        ) == {("b", "a"), ("d", "c"), ("a", "d"), ("c", "b")}
