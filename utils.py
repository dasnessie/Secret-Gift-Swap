from copy import deepcopy
from random import random, shuffle
import warnings


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
    for gifter, giftee in pairing:
        if (gifter, giftee) in restricted_pairs:
            if random() > pairs_with_probabilities[(gifter, giftee)]:
                return False
    return True


def get_pairing_with_probabilities(
    participants: list[str], pairs_with_probabilities: dict[tuple[str, str], float] = {}
) -> set[tuple[str, str]]:
    """_summary_

    Args:
        participants (list[str]): list of participant names
        pairs_with_probabilities (dict[tuple[str, str], float], optional): Dict containing tuple of (giver, giftee) as key and probability as value. Defaults to {}.

    Raises:
        ValueError: No suitable pairing found

    Returns:
        set[tuple[str, str]]: set of tuples mapping each participant (first tuple entry) to someone to gift (second tuple entry)
    """
    for i in range(5):
        for i in range(100):
            pairing = _generate_pairing(participants)
            if _accept_pairing(pairs_with_probabilities, pairing):
                return pairing
        if (
            all(value == 0 for value in pairs_with_probabilities.values())
            or len(pairs_with_probabilities) == 0
        ):
            break  # increasing the probability would not help here, so we skip that
        warnings.warn(
            "Could not generate a pairing with given constraints (I tried 100 times)! Increasing probabilities and trying again..."
        )
        for pair, probability in pairs_with_probabilities.items():
            pairs_with_probabilities[pair] == probability * 1.2
    raise ValueError("Could not generate a pairing with these constraints!")
