from copy import deepcopy
from random import random, shuffle
import warnings

from constraints import Constraint, Constraints
from matching import Matching
from participant import Participant


def _generate_pairing(participants: list[Participant]) -> Matching:
    """Generate a single pairing from a list of participants

    Args:
        participants (list[Participant]): list of participants

    Returns:
        Matching: Matching of participants
    """
    shuffled_participants = deepcopy(participants)
    shuffle(shuffled_participants)
    result = {}
    for i in range(len(shuffled_participants)):
        result[shuffled_participants[i]] = shuffled_participants[
            (i + 1) % len(shuffled_participants)
        ]
    return Matching(result)


def _accept_pairing(
    pairs_with_probabilities: Constraints,
    pairing: Matching,
    probability_multiplier: float = 1.0,
) -> bool:
    """Decide if pairing should be accepted given probabilities for specific pairs

    Args:
        pairs_with_probabilities (Constraints): Constraints
        pairing (Matching): a pairing, eg generated with _generate_pairing

    Returns:
        bool: true if pairing should be accepted
    """
    for giver, giftee in pairing:
        if (giver, giftee) in pairs_with_probabilities.restricted_pairs():
            if (
                random()
                > pairs_with_probabilities[(giver, giftee)] * probability_multiplier
            ):
                return False
    return True


def get_pairing_with_probabilities(
    participants: list[Participant],
    pairs_with_probabilities: Constraints = Constraints([]),
    retries: int = 100,
) -> Matching:
    """Generate one pairing, using probabilities

    Args:
        participants (list[Participant]): list of participants
        pairs_with_probabilities (COnstraints, optional): Constraints to respect. Defaults to empty set of constraints.

    Raises:
        ValueError: No suitable pairing found

    Returns:
        Matching: A matching
    """
    probability_multiplier = 1.0
    for i in range(5):
        for i in range(retries):
            pairing = _generate_pairing(participants)
            if _accept_pairing(
                pairs_with_probabilities, pairing, probability_multiplier
            ):
                return pairing
        if (
            all(
                value == 0
                for value in pairs_with_probabilities.values_as_probabilities()
            )
            or len(pairs_with_probabilities) == 0
        ):
            break  # increasing the probability would not help here, so we skip that
        warnings.warn(
            "Could not generate a pairing with given constraints (I tried 100 times)! Increasing probabilities and trying again..."
        )
        probability_multiplier = probability_multiplier * 1.2
    raise ValueError("Could not generate a pairing with these constraints!")
