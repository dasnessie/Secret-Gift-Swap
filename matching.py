from participant import Participant


class Matching:
    def __init__(self, matching: dict[Participant, Participant]):
        """Mapping of one participant (giver) to another (giftee).

        Args:
            matching (dict[Participant, Participant]): Mapping values. Givers as keys, giftees as values.
        """
        self.matching = matching

    def __getitem__(self, key):
        return self.matching[key]

    def __iter__(self):
        return iter(self.matching.items())

    def __str__(self):
        matching_strs = []
        for key in self.matching.keys():
            matching_strs.append(f"'{str(key)}': '{str(self.matching[key])}'")
        return ", ".join(matching_strs)

    def __repr__(self):
        return f"Matching(matching = {self.matching})"

    def __eq__(self, value):
        if isinstance(value, Matching):
            return self.matching == value.matching
        return NotImplemented
