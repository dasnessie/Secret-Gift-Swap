from copy import deepcopy
from random import random, shuffle
import warnings

from constraint import (
    Constraint,
    get_all_probability_values_from_constraints,
    get_probability_from_constraints,
    get_restricted_pairs,
)
from match import Match, get_giftee_for_giver
from participant import Participant


def _generate_pairing(participants: list[Participant]) -> list[Match]:
    """Generate a single pairing from a list of participants

    Args:
        participants (list[Participant]): participants

    Returns:
        list[Match]: Matching of participants
    """
    shuffled_participants = deepcopy(participants)
    shuffle(shuffled_participants)
    result = []
    for i in range(len(shuffled_participants)):
        result.append(
            Match(
                giver=shuffled_participants[i],
                giftee=shuffled_participants[(i + 1) % len(shuffled_participants)],
            )
        )
    return result


def _accept_pairing(
    pairs_with_probabilities: list[Constraint],
    pairing: list[Match],
    probability_multiplier: float = 1.0,
) -> bool:
    """Decide if pairing should be accepted given probabilities for specific pairs

    Args:
        pairs_with_probabilities (list[Constraint]): Constraints
        pairing (list[Match]): a pairing, eg generated with _generate_pairing

    Returns:
        bool: true if pairing should be accepted
    """
    for m in pairing:
        if (m.giver, m.giftee) in get_restricted_pairs(pairs_with_probabilities):
            if (
                random()
                > get_probability_from_constraints(
                    pairs_with_probabilities, m.giver, m.giftee
                )
                * probability_multiplier
            ):
                return False
    return True


def get_pairing_with_probabilities(
    participants: list[Participant],
    pairs_with_probabilities: list[Constraint] = [],
    retries: int = 100,
) -> list[Match]:
    """Generate one pairing, using probabilities

    Args:
        participants (list[Participant]): participants
        pairs_with_probabilities (list[Constraint], optional): Constraints to respect. Defaults to empty set of constraints.

    Raises:
        ValueError: No suitable pairing found

    Returns:
        list[Match]: A matching
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
                for value in get_all_probability_values_from_constraints(
                    pairs_with_probabilities
                )
            )
            or len(pairs_with_probabilities) == 0
        ):
            break  # increasing the probability would not help here, so we skip that
        warnings.warn(
            "Could not generate a pairing with given constraints (I tried 100 times)! Increasing probabilities and trying again..."
        )
        probability_multiplier = probability_multiplier * 1.2
    raise ValueError("Could not generate a pairing with these constraints!")
