from utils import _accept_pairing, _generate_pairing


def test_generate_pairing():
    participants = ["a", "b", "c"]
    assert _generate_pairing(participants) in [
        {"a": "b", "b": "c", "c": "a"},
        {"a": "c", "b": "a", "c": "b"},
    ]
    assert participants == ["a", "b", "c"]


def test_accept_pairing():
    pairing = {"a": "b", "b": "c", "c": "a"}
    pairs_with_probability = {("a", "b"): 0.5}

    selected_count = 0
    for i in range(100):
        if _accept_pairing(pairs_with_probability, pairing):
            selected_count += 1

    assert selected_count >= 38
    assert selected_count <= 62
