import sqlite3
from uuid import UUID

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
            "CREATE TABLE IF NOT EXISTS "
            "exchanges(slug TEXT PRIMARY KEY, name TEXT) STRICT",
        )
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS "
            "participants(uuid TEXT PRIMARY KEY, "
            "exchange_slug TEXT, "
            "FOREIGN KEY (exchange_slug) REFERENCES exchanges (slug)"
            ") STRICT",
        )
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS "
            "participant_names(participant_id TEXT, "
            "name TEXT, "
            "active INTEGER, "
            "exchange_slug TEXT, "
            "FOREIGN KEY (exchange_slug) REFERENCES exchanges (slug), "
            "FOREIGN KEY (participant_id) REFERENCES participants (uuid), "
            "UNIQUE (name, exchange_slug)"
            ") STRICT",
        )
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS "
            "matches(exchange_slug TEXT, "
            "giver_id TEXT, "
            "giftee_id TEXT, "
            "FOREIGN KEY (exchange_slug) REFERENCES exchanges (slug), "
            "FOREIGN KEY (giver_id) REFERENCES participants (uuid), "
            "FOREIGN KEY (giftee_id) REFERENCES participants (uuid)"
            ") STRICT",
        )
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS "
            "constraints(giver_id TEXT, "
            "giftee_id TEXT, "
            "exchange_slug TEXT, "
            "probability_level TEXT, "
            "FOREIGN KEY (exchange_slug) REFERENCES exchanges (slug), "
            "FOREIGN KEY (giver_id) REFERENCES participants (uuid), "
            "FOREIGN KEY (giftee_id) REFERENCES participants (uuid)"
            ") STRICT",
        )
        self.connection.commit()

    def close_connection(self) -> None:
        """Close the connection to the database."""
        self.connection.close()

    def exchange_exists(self, slug: str) -> bool:
        """Whether an exchange with the given slug exists in the database.

        Args:
            slug (str): Slug of the exchange

        Returns:
            bool: Whether or not the exchange exists

        """
        res = self.cursor.execute("SELECT 1 FROM exchanges WHERE slug = ?", (slug,))
        return res.fetchone() is not None

    def participant_name_available(
        self,
        exchange_slug: str,
        old_name: str,
        new_name: str,
    ) -> bool:
        """Check if a participant name is already taken by someone else.

        Args:
            exchange_slug (str): slug of the exchange to search in
            old_name (str): current name of the participant to exclude from search
            new_name (str): name to check availability of

        Returns:
            bool: Whether the name is available

        """
        res = self.cursor.execute(
            "SELECT 1 FROM participant_names "
            "WHERE exchange_slug = ? "
            "AND participant_id != ("
            "SELECT participant_id FROM participant_names "
            "WHERE name = ? AND exchange_slug = ? LIMIT 1"
            ")"
            "AND name = ?",
            (exchange_slug, old_name, exchange_slug, new_name),
        )
        return res.fetchone() is None

    def get_exchange_name(self, slug: str) -> str:
        """Get the name of an exchange for a given slug.

        Args:
            slug (str): Slug of the exchange

        Raises:
            ValueError: _description_If the exchange does not exist

        Returns:
            str: Name of the exchange

        """
        if not self.exchange_exists(slug):
            raise ValueError(f"There is no exchange with slug '{slug}'!")
        res = self.cursor.execute("SELECT name FROM exchanges WHERE slug = ?", (slug,))
        return res.fetchone()[0]

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
        self.cursor.execute(
            "INSERT INTO exchanges VALUES (?, ?)",
            (exchange.slug, exchange.name),
        )
        for participant in participants:
            self.cursor.execute(
                "INSERT INTO participants VALUES (?, ?)",
                (
                    str(participant.uuid),
                    exchange.slug,
                ),
            )
            for i, name in enumerate(participant.names):
                self.cursor.execute(
                    "INSERT INTO participant_names VALUES (?, ?, ?, ?)",
                    (
                        str(participant.uuid),
                        name,
                        int(i == participant.active_name),
                        exchange.slug,
                    ),
                )
        for constraint in constraints:
            self.cursor.execute(
                "INSERT INTO constraints VALUES (?, ?, ?, ?)",
                (
                    str(constraint.giver_id),
                    str(constraint.giftee_id),
                    exchange.slug,
                    constraint.probability_level,
                ),
            )
        for match in pairing:
            self.cursor.execute(
                "INSERT INTO matches VALUES (?, ?, ?)",
                (
                    exchange.slug,
                    str(match.giver_id),
                    str(match.giftee_id),
                ),
            )
        self.connection.commit()

    def get_exchange(
        self,
        slug: str,
    ) -> Exchange:
        """Get exchange by it's slug.

        Args:
            slug (str): slug of the exchange to get

        Raises:
            ValueError: If the exchange does not exist

        Returns:
            Exchange: The exchange object from the database

        """
        if not self.exchange_exists(slug):
            raise ValueError(f"There is no exchange with slug '{slug}'!")
        result = self.cursor.execute(
            "SELECT * FROM participants WHERE exchange_slug = ?",
            (slug,),
        )
        participants = []
        for r in result.fetchall():
            uuid, _exchange = r
            result_participant_names = self.cursor.execute(
                "SELECT name, active FROM participant_names WHERE participant_id = ?",
                (str(uuid),),
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
                    uuid=UUID(uuid),
                ),
            )

        result = self.cursor.execute(
            "SELECT * FROM constraints WHERE exchange_slug = ?",
            (slug,),
        )
        constraints = []
        for r in result.fetchall():
            giver_id, giftee_id, exchange_slug, probability_level = r
            constraints.append(
                Constraint(
                    UUID(giver_id),
                    UUID(giftee_id),
                    probability_level,
                ),
            )

        result = self.cursor.execute(
            "SELECT * FROM matches WHERE exchange_slug = ?",
            (slug,),
        )
        pairing = []
        for r in result.fetchall():
            exchange_slug, giver_uuid, giftee_uuid = r
            pairing.append(Match(UUID(giver_uuid), UUID(giftee_uuid)))

        exchange_name = self.get_exchange_name(exchange_slug)

        return Exchange(exchange_name, participants, constraints, pairing)

    def get_participant(self, participant_id: UUID) -> Participant:
        """Get participant by their uuid.

        Args:
            participant_id (UUID): Id of the participant

        Raises:
            ValueError: If there is no participant with that id

        Returns:
            Participant: The participant with the id

        """
        result_participant_names = self.cursor.execute(
            "SELECT name, active FROM participant_names WHERE participant_id = ?",
            (str(participant_id),),
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
            uuid=UUID(participant_id),
        )

    def change_participant_name(
        self,
        exchange_slug: str,
        old_name: str,
        new_name: str,
    ) -> None:
        """Change the active name of the participant.

        Args:
            exchange_slug (str): Slug of the exchange to use
            old_name (str): current name of the participant
            new_name (str): new name of the participant

        Raises:
            ValueError: If there is no participant with the given name in the exchange

        """
        res_id = self.cursor.execute(
            "SELECT participant_id FROM participant_names "
            "WHERE name = ? AND exchange_slug = ?",
            (old_name, exchange_slug),
        )
        try:
            participant_id = res_id.fetchone()[0]
        except TypeError:
            raise ValueError(f"There is no participant with name '{old_name}'!")
        self.cursor.execute(
            "UPDATE participant_names SET active = 0 "
            "WHERE participant_id = ? AND name = ?",
            (participant_id, old_name),
        )
        res_name_exists = self.cursor.execute(
            "SELECT * FROM participant_names WHERE participant_id = ? AND name = ?",
            (participant_id, new_name),
        )
        name_exists = bool(res_name_exists.fetchone())
        if name_exists:
            # Don't add a new name, just set the existing new_name to active
            self.cursor.execute(
                "UPDATE participant_names SET active = 1 "
                "WHERE participant_id = ? AND name = ?",
                (participant_id, new_name),
            )
        else:
            # Add a new name
            self.cursor.execute(
                "INSERT INTO participant_names VALUES (?, ?, ?, ?)",
                (
                    str(participant_id),
                    new_name,
                    1,
                    exchange_slug,
                ),
            )
        self.connection.commit()

    def get_active_name(self, exchange_slug: str, name: str) -> str:
        """Get up-to-date name of a participant that used to go by the given name.

        Args:
            exchange_slug (str): Slug of the exchange to search in
            name (str): old name of the participant

        Raises:
            ValueError: if there is no participant with that name

        Returns:
            str: the current name of the participant

        """
        res = self.cursor.execute(
            "SELECT name FROM participant_names "
            "WHERE exchange_slug = ? "
            "AND active = 1 "
            "AND participant_id = ("
            "SELECT participant_id FROM participant_names "
            "WHERE exchange_slug = ? "
            "AND name = ?)",
            (exchange_slug, exchange_slug, name),
        )
        try:
            return res.fetchone()[0]
        except TypeError:
            raise ValueError(
                f"Could not find a match for exchange {exchange_slug} "
                f"and participant name {name}!",
            )

    def get_giftee_for_giver(self, exchange_slug: str, giver_name: str) -> Participant:
        """Get the participant a given participant will get a gift for.

        Args:
            exchange_slug (str): slug of the exchange to search in
            giver_name (str): name of the giver

        Raises:
            ValueError: If the exchange does not exist
            ValueError: If there is no participant with the given name in the exchange

        Returns:
            Participant: Participant to get a gift for (giftee)

        """
        if not self.exchange_exists(exchange_slug):
            raise ValueError(f"There is no exchange with slug '{exchange_slug}'!")
        result = self.cursor.execute(
            "SELECT m.giftee_id "
            "FROM matches AS m "
            "JOIN participants as p "
            "ON p.uuid = m.giver_id "
            "JOIN participant_names as n "
            "ON p.uuid = n.participant_id "
            "WHERE n.name = ? "
            "AND p.exchange_slug = ?",
            (
                giver_name,
                exchange_slug,
            ),
        )
        try:
            giftee_id = result.fetchone()[0]
        except TypeError:
            raise ValueError(
                f"There is no participant with name '{giver_name}' "
                f"in exchange '{exchange_slug}'!",
            )
        return self.get_participant(giftee_id)

    def get_giver_for_giftee(self, exchange_slug: str, giftee_name: str) -> Participant:
        """Get the participant a given participant will be getting a gift from.

        Args:
            exchange_slug (str): slug of the exchange to search in
            giftee_name (str): name of the giftee

        Raises:
            ValueError: If the exchange does not exist
            ValueError: If there is no participant with the given name in the exchange

        Returns:
            Participant: Participant to get a gift from (giver)

        """
        if not self.exchange_exists(exchange_slug):
            raise ValueError(f"There is no exchange with slug '{exchange_slug}'!")
        result = self.cursor.execute(
            "SELECT m.giver_id "
            "FROM matches AS m "
            "JOIN participants as p "
            "ON p.uuid = m.giftee_id "
            "JOIN participant_names as n "
            "ON p.uuid = n.participant_id "
            "WHERE n.name = ? "
            "AND p.exchange_slug = ?",
            (
                giftee_name,
                exchange_slug,
            ),
        )
        try:
            giver_id = result.fetchone()[0]
        except TypeError:
            raise ValueError(
                f"There is no participant with name '{giftee_name}' "
                f"in exchange '{exchange_slug}'!",
            )
        return self.get_participant(giver_id)
