from typing import Dict, List, Tuple, Type, Optional


# Constants
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
