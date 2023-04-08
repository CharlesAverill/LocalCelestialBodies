# LocalCelestialBodies
Scripts and data to generate a database of celestial bodies local to our Solar System

# Generation
```bash
git clone https://github.com/CharlesAverill/LocalCelestialBodies.git lcb
cd lcb
python db_generator.py
```

# Example Queries
```sql
-- Select all asteroids with diameter between 90KM and 100KM
SELECT 
  small_body.name, small_body.size 
FROM 
  small_body, asteroid
WHERE 
  90 < small_body.size AND small_body.size < 100 AND
  asteroid.small_body_key=small_body.small_body_key 
ORDER BY 
  small_body.size DESC;
  
-- Select all comets with tails
SELECT 
  small_body.name
FROM 
  small_body, comet 
WHERE 
  comet.has_tail=1 AND 
  comet.small_body_key=small_body.small_body_key 
ORDER BY small_body.name DESC;
```

# Randomly-generated data
The following data fields were generated at the time of the creation of the database:
- `asteroid.has_solid_composition`
- `asteroid.minerals`
- `comet.has_ice`
- `comet.has_dust`
- `comet.has_tail`
