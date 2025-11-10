from __future__ import annotations

from typing import Optional
from uuid import UUID, uuid4


class Participant:
    """Data about one person participating in a gift exchange."""

    def __init__(self, names: str | list[str], active_name: int = 0):
        """A person participating in a gift exchange.

        Args:
            names (str | list[str]): name or list of names for the person.
            active_name (int, optional): name to use for the person. Defaults to 0.

        """
        self.uuid = uuid4()
        self.names = names if isinstance(names, list) else [names]
        self.active_name = active_name

    def add_name(self, new_name: str) -> None:
        """Add a new name for the person, without making it the active one.

        Args:
            new_name (str): the new name

        """
        self.names.append(new_name)

    def change_name(self, new_name: str) -> None:
        """Add a new name for the person, and make it the default.

        Args:
            new_name (str): the new name

        """
        self.add_name(new_name)
        self.active_name = len(self.names) - 1

    def get_name(self) -> str:
        """Get the currently active name of the participant.

        Returns:
            str: Currently active name of participant

        """
        return self.names[self.active_name]

    def __hash__(self):
        return self.id.__hash__()

    def __str__(self):
        return self.get_name()

    def __repr__(self):
        return f"Participant(name={self.names}, active_name = {self.active_name})"

    def __eq__(self, value: any):
        if isinstance(value, Participant):
            return self.id == value.id
        return NotImplemented


def get_participants_by_name(
    participants: list[Participant],
    name: str,
) -> list[Participant]:
    """Get all participants matching a name, from a list of participants.

    Args:
        participants (list[Participant]): list of participants to search
        name (str): Name to search for

    Returns:
        list[Participant]: List of participants using that name

    """
    result = []
    for p in participants:
        if name in p.names:
            result.append(p)
    return result


def get_participant_by_id(
    participants: list[Participant],
    uuid: UUID,
) -> Optional[Participant]:
    """Get participant with given UUID from a list of participants.

    Args:
        participants (list[Participant]): list of participants to search
        uuid (UUID): UUID to search for

    Returns:
        Participant: Participant using that UUID

    """
    for p in participants:
        if uuid == p.id:
            return p
    return None
