import random

import pytest

from constraint import Constraint
from match import Match
from participant import Participant
from utils import _accept_pairing, _generate_pairing, get_pairing_with_probabilities


def test_generate_pairing():
    pa = Participant(names="a", uuid="a")
    pb = Participant(names="b", uuid="b")
    pc = Participant(names="c", uuid="c")
    participants = [pa, pb, pc]
    assert sorted(
        _generate_pairing(participants),
        key=lambda m: m.giver_id,
    ) in [
        [Match(pa.uuid, pb.uuid), Match(pb.uuid, pc.uuid), Match(pc.uuid, pa.uuid)],
        [Match(pa.uuid, pc.uuid), Match(pb.uuid, pa.uuid), Match(pc.uuid, pb.uuid)],
    ]
    assert participants == [
        pa,
        pb,
        pc,
    ]


def test_accept_pairing():
    pa = Participant(names="a", uuid="a")
    pb = Participant(names="b", uuid="b")
    pc = Participant(names="c", uuid="c")
    pairing = [
        Match(pa.uuid, pb.uuid),
        Match(pb.uuid, pc.uuid),
        Match(pc.uuid, pa.uuid),
    ]
    pairs_with_probability = [Constraint(pa.uuid, pb.uuid, "3_past_exchange")]

    random.seed(6740)

    selected_count = 0
    for i in range(100):
        if _accept_pairing(pairs_with_probability, pairing):
            selected_count += 1

    assert selected_count == 41


def test_get_pairing_with_probabilities():
    pa = Participant(names="a", uuid="a")
    pb = Participant(names="b", uuid="b")
    pc = Participant(names="c", uuid="c")
    pd = Participant(names="d", uuid="d")
    participants = [pa, pb, pc]
    assert sorted(
        get_pairing_with_probabilities(participants),
        key=lambda m: m.giver_id,
    ) in [
        [Match(pa.uuid, pb.uuid), Match(pb.uuid, pc.uuid), Match(pc.uuid, pa.uuid)],
        [Match(pa.uuid, pc.uuid), Match(pb.uuid, pa.uuid), Match(pc.uuid, pb.uuid)],
    ]

    assert sorted(
        get_pairing_with_probabilities(
            participants=[pa, pb, pc, pd],
            pairs_with_probabilities=[
                Constraint(pa.uuid, pb.uuid, "1_past_exchange"),
                Constraint(pa.uuid, pc.uuid, "1_past_exchange"),
                Constraint(pb.uuid, pc.uuid, "1_past_exchange"),
                Constraint(pb.uuid, pd.uuid, "1_past_exchange"),
                Constraint(pc.uuid, pa.uuid, "1_past_exchange"),
                Constraint(pc.uuid, pd.uuid, "1_past_exchange"),
                Constraint(pd.uuid, pa.uuid, "1_past_exchange"),
                Constraint(pd.uuid, pb.uuid, "1_past_exchange"),
            ],
        ),
        key=lambda m: m.giver_id,
    ) == [
        Match(pa.uuid, pd.uuid),
        Match(pb.uuid, pa.uuid),
        Match(pc.uuid, pb.uuid),
        Match(pd.uuid, pc.uuid),
    ]

    random.seed(6851)

    assert sorted(
        get_pairing_with_probabilities(
            participants=[pa, pb, pc, pd],
            pairs_with_probabilities=[
                Constraint(pa.uuid, pb.uuid, "3_past_exchange"),
                Constraint(pb.uuid, pd.uuid, "3_past_exchange"),
                Constraint(pc.uuid, pd.uuid, "3_past_exchange"),
                Constraint(pd.uuid, pa.uuid, "3_past_exchange"),
            ],
        ),
        key=lambda m: m.giver_id,
    ) == [
        Match(pa.uuid, pc.uuid),
        Match(pb.uuid, pa.uuid),
        Match(pc.uuid, pd.uuid),
        Match(pd.uuid, pb.uuid),
    ]

    with pytest.raises(ValueError):
        get_pairing_with_probabilities(
            participants=[pa, pb, pc, pd],
            pairs_with_probabilities=[
                Constraint(pa.uuid, pb.uuid, "1_past_exchange"),
                Constraint(pa.uuid, pc.uuid, "1_past_exchange"),
                Constraint(pa.uuid, pd.uuid, "1_past_exchange"),
            ],
        )

    random.seed(6851)

    with pytest.warns(
        UserWarning,
        match="Could not generate a pairing with given constraints",
    ):
        cs = [
            Constraint(pa.uuid, pb.uuid, "2_past_exchange"),
            Constraint(pa.uuid, pc.uuid, "2_past_exchange"),
            Constraint(pa.uuid, pd.uuid, "2_past_exchange"),
        ]
        assert sorted(
            get_pairing_with_probabilities(
                participants=[pa, pb, pc, pd],
                pairs_with_probabilities=cs,
                retries=1,
            ),
            key=lambda m: m.giver_id,
        ) == [
            Match(pa.uuid, pc.uuid),
            Match(pb.uuid, pa.uuid),
            Match(pc.uuid, pd.uuid),
            Match(pd.uuid, pb.uuid),
        ]
