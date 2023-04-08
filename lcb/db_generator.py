import argparse
import csv
import logging
import os
import random
import sqlite3

from pathlib import Path
from sqlite3 import Connection, Cursor
from typing import Type

from constant_lcb_data import *


parser = argparse.ArgumentParser(
    description="Generator script for LocalCelestialBodies database"
)
parser.add_argument(
    "-v", "--verbose", action="store_true", help="Print verbose status messages"
)
if parser.parse_args().verbose:
    logging.getLogger().setLevel(logging.INFO)

# Helper functions
def orbit_class_key(orbit_class: str) -> int:
    """Get the orbit_class_key of a given orbit class string"""
    return list(ORBIT_CLASSES.keys()).index(orbit_class.upper()) + 1


def type_to_sqltype(t: Type) -> str:
    """Convert a Python type to a SQLite type"""
    if t == float:
        return "REAL"
    elif t == str:
        return "TEXT"
    return "NULL"


def get_minerals() -> str:
    """Generate random minerals"""
    return ", ".join(
        random.sample(
            [
                "Gold",
                "Cobalt",
                "Iron",
                "Manganese",
                "Molybdenum",
                "Nickel",
                "Osmium",
                "Palladium",
                "Platinum",
                "Rhenium",
                "Rhodium",
                "Ruthenium",
                "Tungsten",
            ],
            random.randint(3, 7),
        )
    )


DB_FILENAME = Path(__file__).parents[1] / "lsb.db"
DATA_PATH = Path(__file__).parents[1] / "data"

# Delete database if it already exists
if os.path.exists(DB_FILENAME):
    logging.info("Removing existing database file")
    os.remove(DB_FILENAME)

# Open connection to database file
logging.info("Connecting to database")
db_connection: Connection = sqlite3.connect(DB_FILENAME)
cursor: Cursor = db_connection.cursor()

# Generate table schema
logging.info("Generating table schemas")
for table_name, (
    table_fields,
    table_needs_primary_key,
    foreign_tables,
) in DB_TABLES_FIELDS.items():
    logging.info(f"    - {table_name}")
    # Generate fields needed for table
    fields = [
        f"{field_name} {type_to_sqltype(field_type)}"
        for field_name, field_type in table_fields
    ]

    # Prepend primary key if it's needed
    if table_needs_primary_key:
        fields.insert(0, f"{table_name}_key INTEGER PRIMARY KEY")

    # Append foreign key with constraint if it's needed
    if foreign_tables:
        for foreign_table in foreign_tables:
            fields.append(f"{foreign_table}_key INTEGER NOT NULL")
        for foreign_table in foreign_tables:
            fields.append(
                f"FOREIGN KEY ({foreign_table}_key) REFERENCES {foreign_table}({foreign_table}_key)"
            )

    # Build the query
    fields_str = ",\n\t".join(fields).strip()
    query = f"""
    CREATE TABLE {table_name} (
        {fields_str}
);
    """.strip()

    # Execute the query
    cursor.execute(query)

# Insert data
logging.info("Inserting data")
# ORBITS
logging.info("Inserting orbit data")
for orbit_name, (orbit_distance, orbit_location) in ORBIT_CLASSES.items():
    cursor.execute(
        "INSERT INTO orbit_class (name, size, location) VALUES (?, ?, ?);",
        (orbit_name, orbit_distance, orbit_location),
    )
# PLANETS
logging.info("Inserting planet data")
for planet_name, (
    climate,
    temperature,
    defining_features,
    has_rings,
    ring_color,
    ring_width,
) in PLANETS.items():
    cursor.execute(
        "INSERT INTO planet (name, climate, temperature, defining_features, ring_exists, ring_color, ring_width) VALUES (?,?,?,?,?,?,?);",
        (
            planet_name,
            climate,
            temperature,
            defining_features,
            int(has_rings),
            ring_color,
            ring_width,
        ),
    )
# ASTEROIDS
latest_small_body_key: int = 1
# full_name, diameter, class
for small_object in ("comet", "asteroid"):
    logging.info(f"Inserting {small_object} data")
    with open(DATA_PATH / f"{small_object}.csv") as file:
        # Open csv file, skip first line
        reader = csv.DictReader(file)

        # Iterate over rows
        for row in reader:
            # Skip any lines with NaNs
            if any([not item for item in row.values()]):
                continue

            # Clean data
            full_name = row["full_name"].strip().split(None, 1)[-1]
            diameter = float(row["diameter"])

            # Insert
            cursor.execute(
                "INSERT INTO small_body (name, size, orbit_class_key) VALUES (?,?,?);",
                (full_name, diameter, orbit_class_key(row["class"])),
            )

            if small_object == "asteroid":
                cursor.execute(
                    "INSERT INTO asteroid (has_solid_composition, minerals, small_body_key) VALUES (?,?,?);",
                    (random.getrandbits(1), get_minerals(), latest_small_body_key),
                )
            else:
                has_ice = random.getrandbits(1)
                has_dust = max(1, has_ice + random.getrandbits(1))
                has_tail = random.getrandbits(1)
                cursor.execute(
                    "INSERT INTO comet (has_ice, has_dust, has_tail, small_body_key) VALUES (?,?,?,?);",
                    (has_ice, has_dust, has_tail, latest_small_body_key),
                )

            latest_small_body_key += 1

# Close database connection
logging.info("Closing database connection")
db_connection.commit()
db_connection.close()
