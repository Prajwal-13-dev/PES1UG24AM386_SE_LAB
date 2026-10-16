"""Track telecom tower maintenance, faults, and servicing risks."""

import sqlite3


conn = sqlite3.connect(":memory:")
conn.execute(
    """
    CREATE TABLE towers (
        id INTEGER PRIMARY KEY,
        site TEXT,
        last_service INTEGER,
        faults INTEGER
    )
    """
)


def add_tower(site, last_service, faults=0):
    """Add a tower and its maintenance details to the database."""
    conn.execute(
        """
        INSERT INTO towers (site, last_service, faults)
        VALUES (?, ?, ?)
        """,
        (site, last_service, faults),
    )
    conn.commit()


def service_tower(tower_id, year):
    """Record servicing and return whether the operation succeeded."""
    try:
        cursor = conn.execute(
            """
            UPDATE towers
            SET last_service = ?, faults = 0
            WHERE id = ?
            """,
            (year, tower_id),
        )
        conn.commit()
    except sqlite3.Error:
        conn.rollback()
        print("Service failed because of a database error.")
        return False

    if cursor.rowcount == 0:
        print(f"No tower found with ID {tower_id}.")
        return False

    return True


def overdue(year):
    """Return tower sites that have gone at least two years without service."""
    rows = conn.execute(
        "SELECT site, last_service FROM towers"
    ).fetchall()

    result = []
    for site, last_service in rows:
        if year - last_service >= 2:
            result.append(site)

    return result


def risk_level(tower_id):
    """Return the risk level of a tower based on its fault count."""
    row = conn.execute(
        "SELECT faults FROM towers WHERE id = ?",
        (tower_id,),
    ).fetchone()

    if row is None:
        return "unknown"

    if row[0] > 3:
        return "high"

    return "normal"


def snapshot():
    """Return a snapshot of all tower records."""
    return conn.execute("SELECT * FROM towers").fetchall()


def main():
    """Run a demonstration of the tower maintenance tracker."""
    add_tower("Ridge-A", 2021, 5)
    add_tower("Coast-B", 2024)

    service_count = int(service_tower(2, 2025))
    total = len(snapshot())

    print(overdue(2025), risk_level(1), total, service_count)


if __name__ == "__main__":
    main()
