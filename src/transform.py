
import pandas as pd

def main():
    columns = ['_start', '_end', '_type', 'link', 'start_date', 'end_date']
    dtype = {
            'link': 'str',
            'start_date': 'str',
            'end_date': 'str'
            }
    relations = pd.read_csv('data/relationships.csv', usecols=columns, dtype=dtype)

    print(relations[0:125])

if __name__ == "__main__":
    main()


