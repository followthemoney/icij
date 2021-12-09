
from os import path
from os import environ
from ftmstore import get_dataset
from followthemoney import model
from followthemoney.cli.util import load_mapping_file

entities = {};

mappings = {
        'entities': 'entities.yml',
        'officers': 'officers.yml',
        'intermediaries': 'intermediaries.yml',
        'others': 'others.yml',
        # TODO - Add these addresses to related LegalEntity address & county fields
        # 'addresses': 'addresses.yml',
        }

def get_map_generators(key, file):
    config = load_mapping_file('mapping/' + file)
    for mapping in config[key]['queries']:
        mapping['csv_url'] = 'file://' + path.abspath(mapping['csv_url'])
        yield model.make_mapping(mapping)

def main():
    dataset = get_dataset('icij', database_uri=environ.get('DATASTORE_URI'))
    bulk = dataset.bulk()

    # Process all addresses/entities/officers into corresponding FTM entities through FTM mappings
    for key, file in mappings.items():
        for gen in get_map_generators(key, file):
            for record in gen.source.records:
                for entity in gen.map(record).values():
                    # Keep a map of ICIJ _id <=> FTM id
                    entities[record['_id']] = entity.id
                    bulk.put(entity)


    # Now process releationships, converting ICIJ _id fields into corresponding FTM entity IDs
    for gen in get_map_generators('relations', 'relations.yml'):
        for record in gen.source.records:
            try:
                record['_start'] = entities[record['_start']]
                record['_end'] = entities[record['_end']]

                for entity in gen.map(record).values():
                    bulk.put(entity)
            except KeyError as err:
                print('Entity with ID %s not found for %s relation' % (err, record['_type']))
                continue

    bulk.flush()

    # TODO - Process address relations seperately as they have to be added to entities
    # Use address relation mapping to add address entities to related LegalEntities


if __name__ == "__main__":
    main()


