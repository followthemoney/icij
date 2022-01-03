
from os import path
from os import environ
from ftmstore import get_dataset
from followthemoney import model
from followthemoney.cli.util import load_mapping_file


def get_map_generators(key, file):
    config = load_mapping_file('mapping/' + file)
    for mapping in config[key]['queries']:
        mapping['csv_url'] = 'file://' + path.abspath(mapping['csv_url'])
        yield model.make_mapping(mapping)

def main():
    mappings = {
            'entities': 'entities.yml',
            'officers': 'officers.yml',
            'intermediaries': 'intermediaries.yml',
            'others': 'others.yml',
            'addresses': 'addresses.yml',
            }
    dataset = get_dataset('icij', database_uri=environ.get('DATASTORE_URI'))
    entities = {};

    # Process all addresses/entities/officers into corresponding FTM entities through FTM mappings
    for key, file in mappings.items():
        for gen in get_map_generators(key, file):
            bulk = dataset.bulk()
            for record in gen.source.records:
                for entity in gen.map(record).values():
                    # Keep a map of ICIJ _id <=> FTM id
                    entities[record['_id']] = entity.id
                    bulk.put(entity)
            bulk.flush()


    # Now process releationships, converting ICIJ _id fields into corresponding FTM entity IDs
    for gen in get_map_generators('relations', 'relations.yml'):
        bulk = dataset.bulk()
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

    # Add addresses to related LegalEntity addressEntity field
    for gen in get_map_generators('address-relations', 'address-relations.yml'):
        bulk = dataset.bulk()
        for record in gen.source.records:
            company = dataset.get(entities[record['_start']]);
            address = dataset.get(entities[record['_end']]);

            # Use summary in relation record for address entity
            if 'link' in record:
                address.add('summary', record['link'])
                bulk.put(address)

            company.add('addressEntity', address)
            bulk.put(company)
        bulk.flush()

if __name__ == "__main__":
    main()


