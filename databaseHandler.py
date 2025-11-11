import sqlite3
from uuid import uuid4

from constraint import Constraint
from exchange import Exchange
from match import Match
from participant import Participant


class DatabaseHandler:
    """Manages communication with the database."""

    def __init__(self, db_path: str = "db.sqlite"):
        """Manages communication with the database.

        Args:
            db_path (str, optional): Path to SQLite database. Defaults to "db.sqlite".

        """
        self.db_path = db_path
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()

        self.connection.execute("PRAGMA foreign_keys = ON")

        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS exchanges(name TEXT PRIMARY KEY) STRICT",
        )
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS "
            "participants(uuid TEXT PRIMARY KEY, "
            "exchange_name TEXT, "
            "FOREIGN KEY (exchange_name) REFERENCES exchanges (name)"
            ") STRICT",
        )
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS "
            "participant_names(participant_id TEXT, "
            "name TEXT, "
            "active INTEGER, "
            "exchange_name TEXT, "
            "FOREIGN KEY (exchange_name) REFERENCES exchanges (name), "
            "FOREIGN KEY (participant_id) REFERENCES participants (uuid), "
            "UNIQUE (name, exchange_name)"
            ") STRICT",
        )
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS "
            "matches(exchange_name TEXT, "
            "giver_id TEXT, "
            "giftee_id TEXT, "
            "FOREIGN KEY (exchange_name) REFERENCES exchanges (name), "
            "FOREIGN KEY (giver_id) REFERENCES participants (uuid), "
            "FOREIGN KEY (giftee_id) REFERENCES participants (uuid)"
            ") STRICT",
        )
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS "
            "constraints(giver_id TEXT, "
            "giftee_id TEXT, "
            "exchange_name TEXT, "
            "probability_level TEXT, "
            "FOREIGN KEY (exchange_name) REFERENCES exchanges (name), "
            "FOREIGN KEY (giver_id) REFERENCES participants (uuid), "
            "FOREIGN KEY (giftee_id) REFERENCES participants (uuid)"
            ") STRICT",
        )
        self.connection.commit()

    def close_connection(self) -> None:
        """Close the connection to the database."""
        self.connection.close()

    def exchange_exists(self, name: str) -> bool:
        """Whether an exchange with the given name exists in the database.

        Args:
            name (str): Name of the exchange

        Returns:
            bool: Whether or not the exchange exists

        """
        res = self.cursor.execute(f"SELECT 1 FROM exchanges WHERE name = '{name}'")
        return res.fetchone() is not None

    def create_exchange(
        self,
        exchange: Exchange,
        participants: list[Participant],
        constraints: list[Constraint],
        pairing: list[Match],
    ) -> None:
        """Create a new exchange in the database.

        Args:
            exchange (Exchange): The exchange to create
            participants (list[Participant]): The participants to create
            constraints (list[Constraint]): The constraints of this exchange
            pairing (list[Match]): The pairing to create

        """
        self.cursor.execute(f"INSERT INTO exchanges VALUES ('{exchange.name}')")
        for participant in participants:
            self.cursor.execute(
                "INSERT INTO participants VALUES "
                f"('{participant.uuid}', '{exchange.name}')",
            )
            for i, name in enumerate(participant.names):
                self.cursor.execute(
                    "INSERT INTO participant_names VALUES "
                    f"('{participant.uuid}', '{name}', "
                    f"{int(i == participant.active_name)}, '{exchange.name}')",
                )
        for constraint in constraints:
            self.cursor.execute(
                "INSERT INTO constraints VALUES "
                f"('{constraint.giver_id}', '{constraint.giftee_id}', "
                f"'{exchange.name}', '{constraint.probability_level}')",
            )
        for match in pairing:
            self.cursor.execute(
                "INSERT INTO matches VALUES "
                f"('{exchange.name}', '{match.giver_id}', '{match.giftee_id}')",
            )
        self.connection.commit()

    def get_exchange(
        self,
        name: str,
    ) -> Exchange:
        """Get exchange by name.

        Args:
            name (str): name of the exchange to get

        Raises:
            ValueError: If the exchange does not exist

        Returns:
            Exchange: The exchange object from the database

        """
        if not self.exchange_exists(name):
            raise ValueError(f"There is no exchange with name '{name}'!")
        result = self.cursor.execute(
            f"SELECT * FROM participants WHERE exchange_name = '{name}'",
        )
        participants = []
        for r in result.fetchall():
            uuid, _exchange = r
            result_participant_names = self.cursor.execute(
                "SELECT name, active FROM participant_names "
                f"WHERE participant_id = '{uuid}'",
            )
            participant_names = []
            for participant_name, active in result_participant_names.fetchall():
                participant_names.append(participant_name)
                if active:
                    active_name = len(participant_names) - 1
            participants.append(
                Participant(
                    names=participant_names,
                    active_name=active_name,
                    uuid=uuid,
                ),
            )

        result = self.cursor.execute(
            f"SELECT * FROM constraints WHERE exchange_name = '{name}'",
        )
        constraints = []
        for r in result.fetchall():
            giver_id, giftee_id, exchange_name, probability_level = r
            constraints.append(Constraint(giver_id, giftee_id, probability_level))

        result = self.cursor.execute(
            f"SELECT * FROM matches WHERE exchange_name = '{name}'",
        )
        pairing = []
        for r in result.fetchall():
            exchange_name, giver_uuid, giftee_uuid = r
            pairing.append(Match(giver_uuid, giftee_uuid))

        return Exchange(name, participants, constraints, pairing)

    def get_participant(self, participant_id: uuid4) -> Participant:
        """Get participant by their uuid.

        Args:
            participant_id (uuid4): Id of the participant

        Raises:
            ValueError: If there is no participant with that id

        Returns:
            Participant: The participant with the id

        """
        result_participant_names = self.cursor.execute(
            "SELECT name, active FROM participant_names "
            f"WHERE participant_id = '{participant_id}'",
        )
        participant_names = []
        for participant_name, active in result_participant_names.fetchall():
            participant_names.append(participant_name)
            if active:
                active_name = len(participant_names) - 1
        if len(participant_names) == 0:
            raise ValueError(f"There is no participant with id '{participant_id}'!")
        return Participant(
            names=participant_names,
            active_name=active_name,
            uuid=participant_id,
        )

    def get_giftee_for_giver(self, exchange_name: str, giver_name: str) -> Participant:
        """Get the participant a given participant will get a gift for.

        Args:
            exchange_name (str): name of the exchange to search in
            giver_name (str): name of the giver

        Raises:
            ValueError: If the exchange does not exist
            ValueError: If there is no participant with the given name in the exchange

        Returns:
            Participant: Participant to get a gift for (giftee)

        """
        if not self.exchange_exists(exchange_name):
            raise ValueError(f"There is no exchange with name '{exchange_name}'!")
        result = self.cursor.execute(
            "SELECT m.giftee_id "
            "FROM matches AS m "
            "JOIN participants as p "
            "ON p.uuid = m.giver_id "
            "JOIN participant_names as n "
            "ON p.uuid = n.participant_id "
            f"WHERE n.name = '{giver_name}' "
            f"AND p.exchange_name = '{exchange_name}'",
        )
        giftee_id = result.fetchone()[0]
        if not giftee_id:
            raise ValueError(
                f"There is no participant with name '{giver_name}' "
                f"in exchange '{exchange_name}'!",
            )
        return self.get_participant(giftee_id)
