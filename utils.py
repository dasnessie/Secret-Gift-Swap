from copy import deepcopy
from random import random, shuffle


def _generate_pairing(participants: list[str]) -> dict[str, str]:
    """Generate a single pairing from a list of participants

    Args:
        participants (list[str]): list of participant names

    Returns:
        dict[str, str]: dict mapping each participant (as key) to someone to gift (as value)
    """
    shuffled_participants = deepcopy(participants)
    shuffle(shuffled_participants)
    result = {}
    for i in range(len(shuffled_participants)):
        result[shuffled_participants[i]] = shuffled_participants[
            (i + 1) % len(shuffled_participants)
        ]
    return result


def _accept_pairing(
    pairs_with_probabilities: dict[tuple[str, str], float], pairing: dict
) -> bool:
    """Decide if pairing should be accepted given probabilities for specific pairs

    Args:
        pairs_with_probabilities (dict[tuple[str, str], float]): Dict containing tuple of (giver, giftee) as key and probability as value
        pairing (dict): a pairing, eg generated with _generate_pairing

    Returns:
        bool: true if pairing should be accepted
    """
    restricted_pairs = pairs_with_probabilities.keys()
    for gifter, giftee in pairing.items():
        if (gifter, giftee) in restricted_pairs:
            if random() > pairs_with_probabilities[(gifter, giftee)]:
                return False
    return True
