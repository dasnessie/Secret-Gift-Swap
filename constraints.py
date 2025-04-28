from typing import Literal
from participants import Participant

matching_probabilities = {
    "never": 0,
    "1_past_exchange": 0,
    "2_past_exchange": 0.2,
    "3_past_exchange": 0.4,
    "none": 1,
}


class Constraint:
    def __init__(
        self,
        giver: Participant,
        giftee: Participant,
        probability_level: Literal[
            "never", "1_past_exchange", "2_past_exchange", "3_past_exchange"
        ],
    ):
        """One single constraint.

        Args:
            giver (Participant): Person that would be giving the gift
            giftee (Participant): Person that would be receiving the gift
            probability_level (Literal[ &quot;never&quot;, &quot;1_past_exchange&quot;, &quot;2_past_exchange&quot;, &quot;3_past_exchange&quot; ]): How much to avoid this pairing. Never: Never match these people in either direction; [1/2/3]_past_exchange: this pairing was used 1/2/3 exchanges ago.
        """
        self.giver = giver
        self.giftee = giftee
        self.probability_level = probability_level

    def __eq__(self, value):
        if isinstance(value, Constraint):
            return self.__dict__ == value.__dict__
        return NotImplemented

    def __str__(self):
        arrow = "↔" if self.probability_level == "never" else "→"
        return f"{self.giver} {arrow} {self.giftee}: {self.probability_level}"

    def __repr__(self):
        return f"Constraint(giver={self.giver}, giftee={self.giftee}, probability_level={self.probability_level})"


class Constraints:
    def __init__(self, constraint_list: list[Constraint]):
        """Set of constraints, eg all constraints in one exchange

        Args:
            constraint_list (list[Constraint]): list of constraints to represent
        """
        self.constraint_list = constraint_list

    def __str__(self):
        return "\n".join([str(c) for c in self.constraint_list])

    def __repr__(self):
        return f"Constraints([{', '.join([repr(c) for c in self.constraint_list])}])"

    def __len__(self):
        return len(self.constraint_list)

    def __getitem__(self, key: tuple[Participant, Participant]):
        result = "none"
        result = self.__getitem_non_recursive(key)
        if result != "never":
            reverse_result = self.__getitem_non_recursive((key[1], key[0]))
            if reverse_result == "never":
                result = "never"
        return matching_probabilities[result]

    def __getitem_non_recursive(self, key: tuple[Participant, Participant]):
        result = "none"
        for c in self.constraint_list:
            if (c.giver, c.giftee) == key:
                if list(matching_probabilities.keys()).index(
                    c.probability_level
                ) < list(matching_probabilities.keys()).index(result):
                    result = c.probability_level
        return result

    def restricted_pairs(self) -> list[tuple[Participant, Participant]]:
        """Get all pairs restricted by the constraints

        Returns:
            list[tuple[Participant, Participant]]: list of restricted pairings. First entry is the giver, second the giftee.
        """
        result = []
        for c in self.constraint_list:
            result.append((c.giver, c.giftee))
        return result

    def values(self) -> list[str]:
        """values of probability levels

        Returns:
            list[str]: list of probability levels
        """
        values = []
        for c in self.constraint_list:
            values.append(c.probability_level)
        return values

    def values_as_probabilities(self) -> list[float]:
        """probability values

        Returns:
            list[float]: list of probability values
        """
        result = []
        for value in self.values():
            result.append(matching_probabilities[value])
        return result
