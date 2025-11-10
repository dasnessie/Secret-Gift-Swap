from constraint import *
from participant import Participant


def test_remove_duplicates():
    p1 = Participant(names="Alice")
    p2 = Participant(names="Bob")
    c1 = Constraint(p1, p2, "2_past_exchange")
    c2 = Constraint(p1, p2, "3_past_exchange")
    assert get_probability_from_constraints([c1, c2], p1, p2) == 0.2

    c3 = Constraint(p1, p2, "2_past_exchange")
    c4 = Constraint(p2, p1, "never")
    cs2 = [c3, c4]
    assert get_probability_from_constraints([c3, c4], p1, p2) == 0
    assert get_probability_from_constraints([c3, c4], p2, p1) == 0
