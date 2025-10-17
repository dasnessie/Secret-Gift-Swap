from typing import Optional
from uuid import UUID, uuid4


class Participant:
    def __init__(self, name: str | list[str], active_name: int = 0):
        """A person participating in a gift exchange

        Args:
            name (str | list[str]): name or list of names for the person.
            active_name (int, optional): name to use for the person. Defaults to 0.
        """
        self.id = uuid4()
        self.name = name if isinstance(name, list) else [name]
        self.active_name = active_name

    def add_name(self, new_name: str):
        """Add a new name for the person, without making it the active one.

        Args:
            new_name (str): the new name
        """
        self.name.append(new_name)

    def change_name(self, new_name: str):
        """Add a new name for the person, and make it the default.

        Args:
            new_name (str): the new name
        """
        self.add_name(new_name)
        self.active_name = len(self.name) - 1

    def get_name(self) -> str:
        """
        Returns:
            str: the current name of the person
        """
        return self.name[self.active_name]

    def __hash__(self):
        return self.id.__hash__()

    def __str__(self):
        return self.get_name()

    def __repr__(self):
        return f"Participant(name={self.name}, active_name = {self.active_name})"

    def __eq__(self, value):
        if isinstance(value, Participant):
            return self.id == value.id
        return NotImplemented


def get_participants_by_name(
    participants: list[Participant], name: str
) -> list[Participant]:
    """Get all participants matching a name, from a list of participants

    Args:
        participants (list[Participant]): list of participants to search
        name (str): Name to search for

    Returns:
        list[Participant]: List of participants using that name
    """
    result = []
    for p in participants:
        if name in p.name:
            result.append(p)
    return result


def get_participant_by_id(participants: list[Participant], id: UUID) -> Optional[Participant]:
    """Get participant with given UUID from a list of participants

    Args:
        participants (list[Participant]): list of participants to search
        id (UUID): UUID to search for

    Returns:
        Participant: Participant using that UUID
    """
    for p in participants:
        if id == p.id:
            return p
    return None
