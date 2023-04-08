import csv
import os
import random
import sqlite3

from sqlite3 import Connection, Cursor
from typing import Dict, List, Tuple, Type, Optional


# Constants
DB_FILENAME: str = "kgjam_solarsystem.db"
DB_TABLES_FIELDS: Dict[
    str,
    Tuple[
        # Fields (Name, Type)
        List[Tuple[str, Type]],
        # Whether the table needs
        # a primary key "{table_name}_key"
        bool,
        # Foreign Key Name (blank if no fkey needed)
        Optional[List[str]],
    ],
] = {
    "small_body": ([("name", str), ("size", float)], True, ["orbit_class"]),
    "asteroid": (
        [
            ("has_solid_composition", bool),
            ("minerals", str),
        ],
        False,
        ["small_body"],
    ),
    "comet": (
        [("has_ice", bool), ("has_dust", bool), ("has_tail", bool)],
        False,
        ["small_body"],
    ),
    "meteor": ([("lifespan", int)], False, ["planet", "small_body"]),
    "orbit_class": ([("name", str), ("size", float), ("location", str)], True, None),
    "constellation": ([("name", str), ("stars", int)], True, None),
    "planet": (
        [
            ("name", str),
            ("climate", str),
            ("temperature", str),
            ("defining_features", str),
            ("ring_exists", bool),
            ("ring_color", str),
            ("ring_width", float),
        ],
        True,
        None,
    ),
    "moon": ([("size", float), ("distance", float)], False, ["planet"]),
}

PLANETS: Dict[str, Tuple[str, str, str, bool, str, float]] = {
    "Mercury": ("Extreme heat and extreme cold", "100-700K", "Slow rotation, relativistic effects", False, "", 0),
    "Venus": ("Sweltering hot", "737K", "Acid rain, toxic atmosphere", False, "", 0),
    "Earth": ("Extremely variable", "248-318K", "Lush forests, deserts, oceans", False, "", 0),
    "Mars": ("Windy and dry", "133-294K", "Dry rivers, polar ice caps", False, "", 0),
    "Jupiter": ("Invariantly stormy", "123K", "Great Red Spot, hexagonal pole storm", False, "", 0),
    "Saturn": ("Extremely windy", "97K", "Rings", True, "Brown and Gold", 73),
    "Uranus": ("Cold and windy", "59K", "Lopsided rotation and rings", True, "Dark Gray", 3),
    "Neptune": ("Colder and windier", "48K", "Farthest from the Sun, ice giant", True, "Red", 100),
}

ORBIT_CLASSES: Dict[str, Tuple[float, str]] = {
    "AMO": (999, "Near-Earth asteroid orbits similar to that of 1221 Amor"),
    "APO": (
        999,
        "Near-Earth asteroid orbits which cross the Earth's orbit similar to that of 1862 Apollo",
    ),
    "AST": (0, "Asteroids orbits not matching any defined orbit class"),
    "ATE": (999, "Near-Earth asteroid orbits similar to that of 2062 Aten"),
    "CEN": (999, "Objects with orbits between Jupiter and Neptune"),
    "IEO": (999, "An asteroid orbit contained entirely within the orbit of Earth"),
    "IMB": (999, "Asteroids within the Inner Main-Belt"),
    "MBA": (999, "Asteroids within the Main-Belt"),
    "MCA": (999, "Asteroids that cross the orbit of Mars"),
    "OMB": (999, "Asteroids within the Outer Main-Belt"),
    "TJN": (999, "Asteroids trapped within Jupiter's L4/L5 Lagrange points"),
    "TNO": (999, "Objects with orbits outside Neptune"),
    "HTC": (999, "Halley-type comets"),
    "ETC": (999, "Encke-type comets"),
    "JFC": (999, "Jupiter-family comets"),
    "CTC": (999, "Chiron-type comets")
}

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


# Delete database if it already exists
if os.path.exists(DB_FILENAME):
    os.remove(DB_FILENAME)

# Open connection to database file
db_connection: Connection = sqlite3.connect(DB_FILENAME)
cursor: Cursor = db_connection.cursor()

# Generate table schema
for table_name, (
    table_fields,
    table_needs_primary_key,
    foreign_tables,
) in DB_TABLES_FIELDS.items():
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
    print(query)
    cursor.execute(query)

# Insert data
# ORBITS
for orbit_name, (orbit_distance, orbit_location) in ORBIT_CLASSES.items():
    cursor.execute(
        "INSERT INTO orbit_class (name, size, location) VALUES (?, ?, ?);",
        (orbit_name, orbit_distance, orbit_location),
    )
# PLANETS
for planet_name, (climate, temperature, defining_features, has_rings, ring_color, ring_width) in PLANETS.items():
    cursor.execute(
        "INSERT INTO planet (name, climate, temperature, defining_features, ring_exists, ring_color, ring_width) VALUES (?,?,?,?,?,?,?);",
        (planet_name, climate, temperature, defining_features, int(has_rings), ring_color, ring_width)
    )
# ASTEROIDS
latest_small_body_key: int = 1
# full_name, diameter, class
for small_object in ("comet", "asteroid"):
    with open(f"{small_object}.csv") as file:
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
# COMETS


# Close database connection
db_connection.commit()
db_connection.close()
