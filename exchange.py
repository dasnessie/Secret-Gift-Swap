from participants import Participant, Participants
from constraints import Constraints


class Exchange:
    def __init__(self, name: str, participants: Participants, constraints: Constraints):
        """Holds all information about one gift exchange

        Args:
            name (str): name of exchange. Used to identify it.
            participants (Participants): People participating in the exchange
            constraints (Constraints): Constraints used in generation of matching
        """
        self.name = name
        self.participants = participants
        self.constraints = constraints
