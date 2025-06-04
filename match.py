from participant import Participant


class Match:
    def __init__(self, giver: Participant, giftee: Participant):
        """Mapping of one participant (giver) to another (giftee).

        Args:
            giver (Participant): Participant giving the gift
            giftee (Participant): Participant receiving the gift
        """
        self.giver = giver
        self.giftee = giftee

    def __eq__(self, value):
        if isinstance(value, Match):
            return self.giver == value.giver and self.giftee == value.giftee
        return NotImplemented

    def __str__(self):
        return f"{str(self.giver)}: {str(self.giftee)}"

    def __repr__(self):
        return f"Match(giver={self.giver}, giftee={self.giftee})"


def get_giftee_for_giver(matching: list[Match], giver: Participant):
    for m in matching:
        if m.giver == giver:
            return m.giftee
    return None
