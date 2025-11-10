import json
import sqlite3

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
            "names TEXT, "
            "active_name INTEGER, "
            "exchange_name TEXT, "
            "FOREIGN KEY (exchange_name) REFERENCES exchanges (name)"
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
                f"('{participant.uuid}', '{json.dumps(participant.names)}', "
                f"{participant.active_name}, '{exchange.name}')",
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

        Returns:
            Exchange: The exchange object from the database

        """
        if not self.exchange_exists(name):
            return None
        result = self.cursor.execute(
            f"SELECT * FROM participants WHERE exchange_name = '{name}'",
        )
        participants = []
        for r in result.fetchall():
            uuid, names, active_name, exchange = r
            participants.append(
                Participant(
                    names=json.loads(names),
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

        return Exchange(exchange_name, participants, constraints, pairing)
