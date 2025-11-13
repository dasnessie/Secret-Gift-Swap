import warnings
from copy import deepcopy
from random import random, shuffle

from constraint import (
    Constraint,
    get_all_probability_values_from_constraints,
    get_probability_from_constraints,
    get_restricted_pairs,
)
from match import Match
from participant import Participant


def _generate_pairing(participants: list[Participant]) -> list[Match]:
    """Generate a single pairing from a list of participants.

    Args:
        participants (list[Participant]): participants

    Raises:
        ValueError: If there are none or just one participant

    Returns:
        list[Match]: Matching of participants

    """
    if len(participants) < 2:
        raise ValueError("Can't generate a pairing for just one participant!")
    shuffled_givers = deepcopy(participants)
    shuffled_giftees = deepcopy(participants)
    shuffle(shuffled_givers)
    no_self_gifts = False
    while not no_self_gifts:
        shuffle(shuffled_giftees)
        no_self_gifts = True
        for giver, giftee in zip(shuffled_givers, shuffled_giftees):
            if giver == giftee:
                no_self_gifts = False
    return [
        Match(giver.uuid, giftee.uuid)
        for giver, giftee in zip(shuffled_givers, shuffled_giftees)
    ]


def _accept_pairing(
    pairs_with_probabilities: list[Constraint],
    pairing: list[Match],
    probability_multiplier: float = 1.0,
) -> bool:
    """Decide if pairing should be accepted given probabilities for specific pairs.

    Args:
        pairs_with_probabilities (list[Constraint]): Constraints
        pairing (list[Match]): a pairing, eg generated with _generate_pairing
        probability_multiplier (float): value to multiply probabilities with,
            for situations with very few possible matches

    Returns:
        bool: true if pairing should be accepted

    """
    for m in pairing:
        if (m.giver_id, m.giftee_id) in get_restricted_pairs(pairs_with_probabilities):  # noqa: SIM102 for better legibility
            if (
                random()
                > get_probability_from_constraints(
                    pairs_with_probabilities,
                    m.giver_id,
                    m.giftee_id,
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
    """Generate one pairing, using probabilities.

    Args:
        participants (list[Participant]): participants
        pairs_with_probabilities (list[Constraint], optional): Constraints to respect.
            Defaults to empty set of constraints.
        retries (int): How often to try to find a match

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
                pairs_with_probabilities,
                pairing,
                probability_multiplier,
            ):
                return pairing
        if (
            all(
                value == 0
                for value in get_all_probability_values_from_constraints(
                    pairs_with_probabilities,
                )
            )
            or len(pairs_with_probabilities) == 0
        ):
            break  # increasing the probability would not help here, so we skip that
        warnings.warn(
            "Could not generate a pairing with given constraints (I tried 100 times)! "
            "Increasing probabilities and trying again...",
        )
        probability_multiplier = probability_multiplier * 1.2
    raise ValueError("Could not generate a pairing with these constraints!")
