from utils import _generate_pairing


def test_generate_pairing():
    participants = ['a', 'b', 'c']
    assert _generate_pairing(participants) in [
        {"a": "b", "b": "c", "c": "a"},
        {"a": "c", "b": "a", "c": "b"},
    ]
    assert participants == ['a', 'b', 'c']
