# Simple scripts for testing on Neo4J graph DB

Scripts:
- ingest_data.py
  - Script to create a fake dataset.
  - If any existing graph on DB, it will be replaced by a new one.
  - Model to create will include:
    - Team nodes
    - SocialChannel nodes
    - Follower nodes
    - A team may own a social channel
    - A follower may follow a social channel
- read_data.py
  - Script to extract some aggregated demographics on one social channel followers

Scripts are coded on Python 3
