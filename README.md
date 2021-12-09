
### Transform ICIJ dataset to aleph entities

This repository contains FTM mappings to convert the ICIJ neo4j csv datadump to
FTM entities.

1.  Extract the ICIJ dataset into a `./data` directory in this project
2.  Setup docker env through `docker-compose run --rm shell`
3.  Run `python src/transform.py` to transform data into FTM entities stored in
    ftm store dataset `icij`
