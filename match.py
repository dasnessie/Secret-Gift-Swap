from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uuid import uuid4


class Match:
    """Match of one giver to one giftee."""

    def __init__(self, giver_id: uuid4, giftee_id: uuid4):
        """Match one participant (giver) to another (giftee).

        Args:
            giver_id (uuid4): Participant giving the gift
            giftee_id (uuid4): Participant receiving the gift

        """
        self.giver_id = giver_id
        self.giftee_id = giftee_id

    def __eq__(self, value: any):
        if isinstance(value, Match):
            return self.giver_id == value.giver_id and self.giftee_id == value.giftee_id
        return NotImplemented

    def __str__(self):
        return f"{str(self.giver_id)}: {str(self.giftee_id)}"

    def __repr__(self):
        return f"Match(giver={self.giver_id}, giftee={self.giftee_id})"


def get_giftee_for_giver(
    matching: list[Match],
    giver_id: uuid4,
) -> uuid4 | None:
    """Given a giver, get their giftee from a list of matches.

    Args:
        matching (list[Match]): Pairing to use
        giver_id (uuid4): Participant to get giftee for

    Returns:
        uuid4|None: Giftee

    """
    for m in matching:
        if m.giver_id == giver_id:
            return m.giftee_id
    return None
