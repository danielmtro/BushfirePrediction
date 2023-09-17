import pandas as pd
from geocoder_functions import get_lat_long
import datetime
import os
import csv
import logging



def clean_data(df: pd.DataFrame) -> pd.DataFrame:

    # Remove any incomplete rows
    df = df.dropna()
    
    # Keep only relevant columns
    df = df[['Year', 'AreaHa', 'Shape__Length', 'StartDate', 'Label', 'FireName']]

    # Consider only wildfires
    df = df[df['Label'].str.contains('Wildfire')]
    
    # Only use data after 2010
    df = df[df['Year'] > 2010]

    # Convert releant columns into integers
    df['Year'] = df['Year'].apply(lambda x: int(x)) 
    df['AreaHa'] = df['AreaHa'].apply(lambda x: int(x) * 1e4)  # Area in square metres
    df['Shape__Length'] = df['Shape__Length'].apply(lambda x: int(x)) # Length in metres

    # Convert Date into Datetime
    df['StartDate'] = df['StartDate'].apply(lambda x: datetime.datetime.strptime(x[:10], "%Y/%m/%d").date())
    
    df.reset_index(drop=True, inplace=True)
    csv_filename = 'test_2.csv'
    logger_filename = 'logger_2.csv'
    failed_list = []
    print(f"Total length of the df is {len(df)}")

    # improve the runtime efficiency by remembering locations that come up multiple times
    locations = {}

    with open(csv_filename, 'a', newline='') as csv_file, open(logger_filename, 'a') as logger_file:
        initial = None
        for i, row in df.iterrows():

            if not initial:
                initial = i

            if row is None or row.empty:
                continue

            new_row = row.copy()

            # Check if the location has already been found before
            if new_row['FireName'] in locations:
                latitude, longitude = locations[new_row['FireName']]
            else:
                latitude, longitude = get_lat_long(new_row['FireName'])
                locations[new_row['FireName']] = (latitude, longitude)

            new_row['Latitude'], new_row['Longitude'] = latitude, longitude
            # test if we can get the new row
            if not new_row['Latitude']:
                append_dict_to_csv(row.to_dict(), logger_file)
                failed_list.append(new_row)
                continue
            append_dict_to_csv(new_row.to_dict(), csv_file)

            # log every 100 rows
            if i%100 == 0:
                print(f"{i - initial}")
            
    df = pd.from_csv(csv_filename)

    print(f"The total number of found locations was {len(df)}. We couldn't determine the locations for {len(failed_list)}. This has a total error rate of {len(failed_list)/(len(df) + len(failed_list)) * 100}%")

    # # Convert the FireName column into latitude and longitude columns
    # df['LatLong'] = df['FireName'].apply(lambda x: get_lat_long(x))

    # # Remove fire locations whose location couldn't be determined 
    # df_final = df[df['LatLong'] is not None]

    # # Error rate (%)
    # error = len(df_final)/len(df) * 100
    # with open('conversion_logging.txt', 'w') as f:
    #     f.write(f"The error rate in the dataset is {error}")

    # # Rename columns for readablity 
    # df = df.rename(columns={'AreaHa': 'Area'})

    return df


def append_dict_to_csv(dictionary, csv_file):
    """
    Appends a dictionary to a CSV file, with each dictionary value in a separate column.

    Parameters:
    - dictionary: The dictionary to append to the CSV file.
    - csv_filename: The filename of the CSV file to which the dictionary will be appended.
    """
    try:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(dictionary.values())
    except Exception as e:
        print(f"Error appending dictionary: {str(e)}")


def main():
    filename = 'bushfire_data/NSW_fire_history_polygons.csv'
    preliminary_df = pd.read_csv(filename)

    csv_filename = 'test.csv'
    already_read = pd.read_csv(csv_filename)
    preliminary_df = preliminary_df.iloc[32700::]
    df = clean_data(preliminary_df)
    # df.to_csv('bushfire_data/fire_locations.csv')
    # print(df)
    # print(df['FireName'])


def main2():
    filename = 'bushfire_data/NSW_fire_history_polygons.csv'
    preliminary_df = pd.read_csv(filename)

    csv_filename = 'test.csv'
    already_read = pd.read_csv(csv_filename)

    last_row = already_read.tail(1)
    for i, row in preliminary_df.iterrows():
        if int(row['Year']) == 2018:
            if int(row['Shape__Length']) == 2241:
                print(i, row)
                break

if __name__ == '__main__':
    main()