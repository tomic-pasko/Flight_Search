from string import ascii_uppercase as alc
import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd


# scrape for iata codes from wiki site "https://en.wikipedia.org/wiki/List_of_airports_by_IATA_airport_code:_A"
def scrape_wiki():
    final_data = []

    # loop through letters from A to Z, create url and soup
    for i in alc:
        url = f"https://en.wikipedia.org/wiki/List_of_airports_by_IATA_airport_code:_{i}"

        # requesting for the website
        Web = requests.get(url)
        # creating a BeautifulSoup object and specifying the parser
        soup = BeautifulSoup(Web.text, 'html.parser')
        table_soup = soup.find('table', class_='wikitable sortable')

        # include only table rows that don't have class defined
        tr_soup = table_soup.find_all('tr', {'class': ''})

        # skip 0th item in tr_soup list tr_soup[1:]
        for row in tr_soup[1:]:
            columns = row.find_all('td')

            record = {
                "iata": columns[0].getText().rstrip().split('[')[0],
                "airport_name": columns[2].getText().rstrip(),
                "location_served": columns[3].getText().rstrip(),
                "location_served_city": columns[3].getText().split(",")[0]
            }
            final_data.append(record)

    # write dict to csv "Airport_Location"
    field_names = ['iata', 'airport_name', 'location_served', 'location_served_city']
    with open('Airport_Location.csv', 'w', encoding='utf-8', newline='\n') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()
        writer.writerows(final_data)

    # using pandas read two csv files, csv file scraped from wiki page and csv file from Global Airport Database
    df_airport_iata_wiki = pd.read_csv('Airport_Location.csv')
    df_airport_iata_location = pd.read_csv('Global_Airport_Database_v2.csv')

    # rename column in "df_airport_iata_location" dataframe
    df_airport_iata_location.rename(columns={'IATA code': 'iata'}, inplace=True)

    # join two dataframes, on index 'iata
    df_airport = df_airport_iata_wiki.join(df_airport_iata_location.set_index('iata'), on='iata')

    df_airport.rename(columns={'Lat Decimal Degrees': 'lat'}, inplace=True)
    df_airport.rename(columns={'Long Decimal Degrees': 'long'}, inplace=True)

    # df.to_dict('records'), result: [{'col1': 1, 'col2': 0.5}, {'col1': 2, 'col2': 0.75}]
    dict_Airport = df_airport.to_dict('records')

    return dict_Airport









