from participants import Participant
from constraints import *


def test_remove_duplicates():
    p1 = Participant(name="Alice")
    p2 = Participant(name="Bob")
    c1 = Constraint(p1, p2, "2_past_exchange")
    c2 = Constraint(p1, p2, "3_past_exchange")
    cs1 = Constraints([c1, c2])
    assert cs1[(p1, p2)] == 0.2

    c3 = Constraint(p1, p2, "2_past_exchange")
    c4 = Constraint(p2, p1, "never")
    cs2 = Constraints([c3, c4])
    assert cs2[(p1, p2)] == 0
    assert cs2[(p2, p1)] == 0
