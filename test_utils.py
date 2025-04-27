import random
import pytest
from constraints import Constraint, Constraints
from matching import Matching
from participants import Participant
from utils import get_pairing_with_probabilities, _generate_pairing, _accept_pairing


def test_generate_pairing():
    pa = Participant(name="a")
    pb = Participant(name="b")
    pc = Participant(name="c")
    participants = [pa, pb, pc]
    assert _generate_pairing(participants) in [
        Matching({pa: pb, pb: pc, pc: pa}),
        Matching({pa: pc, pb: pa, pc: pb}),
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
    pairing = Matching({pa: pb, pb: pc, pc: pa})
    pairs_with_probability = Constraints([Constraint(pa, pb, "3_past_exchange")])

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
    assert get_pairing_with_probabilities(participants).matching in [
        {pa: pb, pb: pc, pc: pa},
        {pa: pc, pb: pa, pc: pb},
    ]

    assert get_pairing_with_probabilities(
        participants=[pa, pb, pc, pd],
        pairs_with_probabilities=Constraints(
            [
                Constraint(pa, pb, "1_past_exchange"),
                Constraint(pa, pc, "1_past_exchange"),
                Constraint(pb, pc, "1_past_exchange"),
                Constraint(pb, pd, "1_past_exchange"),
                Constraint(pc, pa, "1_past_exchange"),
                Constraint(pc, pd, "1_past_exchange"),
                Constraint(pd, pa, "1_past_exchange"),
                Constraint(pd, pb, "1_past_exchange"),
            ]
        ),
    ).matching == {pa: pd, pb: pa, pc: pb, pd: pc}

    random.seed(6851)

    assert get_pairing_with_probabilities(
        participants=[pa, pb, pc, pd],
        pairs_with_probabilities=Constraints(
            [
                Constraint(pa, pb, "3_past_exchange"),
                Constraint(pb, pd, "3_past_exchange"),
                Constraint(pc, pd, "3_past_exchange"),
                Constraint(pd, pa, "3_past_exchange"),
            ]
        ),
    ).matching == {pc: pd, pa: pc, pd: pb, pb: pa}

    with pytest.raises(ValueError):
        get_pairing_with_probabilities(
            participants=[pa, pb, pc, pd],
            pairs_with_probabilities=Constraints(
                [
                    Constraint(pa, pb, "1_past_exchange"),
                    Constraint(pa, pc, "1_past_exchange"),
                    Constraint(pa, pd, "1_past_exchange"),
                ]
            ),
        )

    random.seed(6851)

    with pytest.warns(
        UserWarning, match="Could not generate a pairing with given constraints"
    ):
        cs = Constraints(
            [
                Constraint(pa, pb, "2_past_exchange"),
                Constraint(pa, pc, "2_past_exchange"),
                Constraint(pa, pd, "2_past_exchange"),
            ]
        )
        assert get_pairing_with_probabilities(
            participants=[pa, pb, pc, pd], pairs_with_probabilities=cs, retries=1
        ).matching == {pb: pa, pd: pb, pa: pc, pc: pd}
