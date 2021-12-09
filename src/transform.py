
from os import path
from os import environ
from ftmstore import get_dataset
from followthemoney import model
from followthemoney.cli.util import load_mapping_file
import yaml
import pandas as pd

# entities = {
        # 'entities': {
            # 'mapping': 'entities.yml'
        # }

# def load_relations():
    # columns = ['_start', '_end', '_type', 'link', 'start_date', 'end_date']
    # dtype = {
            # 'link': 'str',
            # 'start_date': 'str',
            # 'end_date': 'str'
            # }
    # return pd.read_csv('data/relationships.csv', usecols=columns, dtype=dtype)

entities = {};

mappings = [
        'entities.yml',
        'officers.yml',
        ]

def main():
    dataset = get_dataset('icij', database_uri=environ.get('DATASTORE_URI'))
    bulk = dataset.bulk()

    for mapping in mappings:
        mapping = load_mapping_file('mapping/' + mapping)
        mapping['csv_url'] = 'file://' + path.abspath(mapping['csv_url'])
        gen = model.make_mapping(mapping)

        for record in gen.source.records:
            for entity in gen.map(record).values():
                # Keep a map of ICIJ _id <=> FTM id
                if record['_id'] not in entities:
                    entities[record['_id']] = entity.id
                else:
                    raise Exception('_id %s is not unique!' % record['_id'])

                bulk.put(entity)

    bulk.flush()

    print(entities)

if __name__ == "__main__":
    main()


