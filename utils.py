from copy import deepcopy
from random import random, shuffle


def _generate_pairing(participants: list[str]) -> set[tuple[str, str]]:
    """Generate a single pairing from a list of participants

    Args:
        participants (list[str]): list of participant names

    Returns:
        set[tuple[str, str]]: set of tuples mapping each participant (first tuple entry) to someone to gift (second tuple entry)
    """
    shuffled_participants = deepcopy(participants)
    shuffle(shuffled_participants)
    result = set()
    for i in range(len(shuffled_participants)):
        result.add(
            (
                shuffled_participants[i],
                shuffled_participants[(i + 1) % len(shuffled_participants)],
            )
        )
    return result


def _accept_pairing(
    pairs_with_probabilities: dict[tuple[str, str], float],
    pairing: set[tuple[str, str]],
) -> bool:
    """Decide if pairing should be accepted given probabilities for specific pairs

    Args:
        pairs_with_probabilities (dict[tuple[str, str], float]): Dict containing tuple of (giver, giftee) as key and probability as value
        pairing (set[tuple[str, str]]): a pairing asset of tuples of (giver, giftee), eg generated with _generate_pairing

    Returns:
        bool: true if pairing should be accepted
    """
    restricted_pairs = pairs_with_probabilities.keys()
    for (gifter, giftee) in pairing:
        if (gifter, giftee) in restricted_pairs:
            if random() > pairs_with_probabilities[(gifter, giftee)]:
                return False
    return True
