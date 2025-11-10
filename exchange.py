from constraint import Constraint
from participant import Participant


class Exchange:
    """All the data for one gift exchange."""

    def __init__(
        self,
        name: str,
        participants: list[Participant],
        constraints: list[Constraint],
    ):
        """Information about one gift exchange.

        Args:
            name (str): name of exchange. Used to identify it.
            participants (list[Participant]): People participating in the exchange
            constraints (list[Constraint]): Constraints used in generation of matching

        """
        self.name = name
        self.participants = participants
        self.constraints = constraints
