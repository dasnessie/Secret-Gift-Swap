import random
import pytest
from constraint import Constraint
from match import Match
from participant import Participant
from utils import get_pairing_with_probabilities, _generate_pairing, _accept_pairing


def test_generate_pairing():
    pa = Participant(name="a")
    pb = Participant(name="b")
    pc = Participant(name="c")
    participants = [pa, pb, pc]
    assert sorted(
        _generate_pairing(participants), key=lambda m: m.giver.get_name()
    ) in [
        [Match(pa, pb), Match(pb, pc), Match(pc, pa)],
        [Match(pa, pc), Match(pb, pa), Match(pc, pb)],
    ]
    assert participants == [
        pa,
        pb,
        pc,
    ]


def test_accept_pairing():
    pa = Participant(name="a")
    pb = Participant(name="b")
    pc = Participant(name="c")
    pairing = [Match(pa, pb), Match(pb, pc), Match(pc, pa)]
    pairs_with_probability = [Constraint(pa, pb, "3_past_exchange")]

    random.seed(6740)

    selected_count = 0
    for i in range(100):
        if _accept_pairing(pairs_with_probability, pairing):
            selected_count += 1

    assert selected_count == 41


def test_get_pairing_with_probabilities():
    pa = Participant(name="a")
    pb = Participant(name="b")
    pc = Participant(name="c")
    pd = Participant(name="d")
    participants = [pa, pb, pc]
    assert sorted(
        get_pairing_with_probabilities(participants), key=lambda m: m.giver.get_name()
    ) in [
        [Match(pa, pb), Match(pb, pc), Match(pc, pa)],
        [Match(pa, pc), Match(pb, pa), Match(pc, pb)],
    ]

    assert sorted(
        get_pairing_with_probabilities(
            participants=[pa, pb, pc, pd],
            pairs_with_probabilities=[
                Constraint(pa, pb, "1_past_exchange"),
                Constraint(pa, pc, "1_past_exchange"),
                Constraint(pb, pc, "1_past_exchange"),
                Constraint(pb, pd, "1_past_exchange"),
                Constraint(pc, pa, "1_past_exchange"),
                Constraint(pc, pd, "1_past_exchange"),
                Constraint(pd, pa, "1_past_exchange"),
                Constraint(pd, pb, "1_past_exchange"),
            ],
        ),
        key=lambda m: m.giver.get_name(),
    ) == [Match(pa, pd), Match(pb, pa), Match(pc, pb), Match(pd, pc)]

    random.seed(6851)

    assert sorted(
        get_pairing_with_probabilities(
            participants=[pa, pb, pc, pd],
            pairs_with_probabilities=[
                Constraint(pa, pb, "3_past_exchange"),
                Constraint(pb, pd, "3_past_exchange"),
                Constraint(pc, pd, "3_past_exchange"),
                Constraint(pd, pa, "3_past_exchange"),
            ],
        ),
        key=lambda m: m.giver.get_name(),
    ) == [Match(pa, pc), Match(pb, pa), Match(pc, pd), Match(pd, pb)]

    with pytest.raises(ValueError):
        get_pairing_with_probabilities(
            participants=[pa, pb, pc, pd],
            pairs_with_probabilities=[
                Constraint(pa, pb, "1_past_exchange"),
                Constraint(pa, pc, "1_past_exchange"),
                Constraint(pa, pd, "1_past_exchange"),
            ],
        )

    random.seed(6851)

    with pytest.warns(
        UserWarning, match="Could not generate a pairing with given constraints"
    ):
        cs = [
            Constraint(pa, pb, "2_past_exchange"),
            Constraint(pa, pc, "2_past_exchange"),
            Constraint(pa, pd, "2_past_exchange"),
        ]
        assert sorted(
            get_pairing_with_probabilities(
                participants=[pa, pb, pc, pd], pairs_with_probabilities=cs, retries=1
            ),
            key=lambda m: m.giver.get_name(),
        ) == [Match(pa, pc), Match(pb, pa), Match(pc, pd), Match(pd, pb)]
