from __future__ import annotations

from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from uuid import uuid4

matching_probabilities = {
    "never": 0,
    "1_past_exchange": 0,
    "2_past_exchange": 0.2,
    "3_past_exchange": 0.4,
    "none": 1,
}


class Constraint:
    """One constraint for who should not give a gift to whom."""

    def __init__(
        self,
        giver_id: uuid4,
        giftee_id: uuid4,
        probability_level: Literal[
            "never",
            "1_past_exchange",
            "2_past_exchange",
            "3_past_exchange",
        ],
    ):
        """One single constraint.

        Args:
            giver_id (uuid4): Person that would be giving the gift
            giftee_id (uuid4): Person that would be receiving the gift
            probability_level (Literal): How much to avoid this pairing.
                Never: Never match these people in either direction;
                [1/2/3]_past_exchange: this pairing was used 1/2/3 exchanges ago.

        """
        self.giver_id = giver_id
        self.giftee_id = giftee_id
        self.probability_level = probability_level

    def __eq__(self, value: any):
        if isinstance(value, Constraint):
            return self.__dict__ == value.__dict__
        return NotImplemented

    def __str__(self):
        arrow = "↔" if self.probability_level == "never" else "→"
        return f"{self.giver_id} {arrow} {self.giftee_id}: {self.probability_level}"

    def __repr__(self):
        return (
            f"Constraint(giver={self.giver_id}, giftee={self.giftee_id}, "
            f"probability_level={self.probability_level})"
        )


def get_restricted_pairs(
    constraints: list[Constraint],
) -> list[tuple[uuid4, uuid4]]:
    """Get all pairs restricted by the constraints.

    Args:
        constraints (list[Constraint]): List of constraints

    Returns:
        list[tuple[uuid4, uuid4]]: list of restricted pairings.
        First entry is the giver, second the giftee.

    """
    result = []
    for c in constraints:
        result.append((c.giver_id, c.giftee_id))
    return result


def get_probability_from_constraints(
    constraints: list[Constraint],
    giver_id: uuid4,
    giftee_id: uuid4,
) -> float:
    """Find matching probability for a given pair in a list of constraints.

    Args:
        constraints (list[Constraint]): List of constraints to search
        giver_id (uuid4): Participant giving the gift
        giftee_id (uuid4): Participant receiving the gift

    Returns:
        float: Intended probability of matching

    """
    result = "none"
    for c in constraints:
        if c.giver_id == giver_id and c.giftee_id == giftee_id:
            if list(matching_probabilities.keys()).index(c.probability_level) < list(
                matching_probabilities.keys(),
            ).index(result):
                result = c.probability_level
        elif (
            c.giver_id == giftee_id
            and c.giftee_id == giver_id
            and c.probability_level == "never"
        ):
            result = "never"
    return matching_probabilities[result]


def get_used_constraint_levels_from_constraints(constraints: list[Constraint]) -> list:
    """Get all constraint levels form a list of constraints.

    Args:
        constraints (list[Constraint]): List of constraints

    Returns:
        list: Used constraint levels

    """
    result = set()
    for c in constraints:
        result.add(c.probability_level)
    return list(result)


def get_all_probability_values_from_constraints(constraints: list[Constraint]) -> list:
    """Get all probability levels used in a list of constraints.

    Args:
        constraints (list[Constraint]): List of constraints

    Returns:
        list: Probability levels

    """
    return [
        matching_probabilities[level]
        for level in get_used_constraint_levels_from_constraints(constraints)
    ]
