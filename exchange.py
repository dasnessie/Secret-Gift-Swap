from slugify import slugify

from constraint import Constraint
from match import Match
from participant import Participant


class Exchange:
    """All the data for one gift exchange."""

    def __init__(
        self,
        name: str,
        participants: list[Participant],
        constraints: list[Constraint],
        pairing: list[Match],
    ):
        """Information about one gift exchange.

        Args:
            name (str): name of exchange. Used to identify it.
            participants (list[Participant]): People participating in the exchange
            constraints (list[Constraint]): Constraints used in generation of matching
            pairing (list[Match]): Pairing generated for this exchange

        """
        self.name = name
        self.slug = slugify(name)
        if not self.slug:
            raise ValueError(
                "Could not generate reasonable url slug "
                f"from exchange name '{self.name}'!",
            )
        self.participants = participants
        self.constraints = constraints
        self.pairing = pairing
