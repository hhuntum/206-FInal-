import requests
import pandas as pd
import sqlite3

api_key = '34d7435988684a1d9d82a54799cb8233'
station_codes = ['All']

def fetch_train_data(api_key, station_codes, limit=25):
    base_url = 'https://api.wmata.com/StationPrediction.svc/json/GetPrediction/'
    headers = {'api_key': api_key}
    train_info = []

    for code in station_codes:
        url = f"{base_url}{code}"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()['Trains']
            train_info.extend(data[:limit])
        else:
            print(f'Error fetching data for station {code}: {response.status_code} - {response.reason}')
    
    return train_info[:limit]

def fetch_station_info(api_key, location_code):
    base_url = f'https://api.wmata.com/Rail.svc/json/jStationInfo?StationCode={location_code}'
    headers = {'api_key': api_key}
    response = requests.get(base_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Error fetching station info for {location_code}: {response.status_code} - {response.reason}')
        return None

def create_destination_id_map(train_data):
    destinations = {train['Destination'] for train in train_data}
    return {dest: idx + 1 for idx, dest in enumerate(sorted(destinations))}

def create_database(train_data, line_id_map, destination_id_map):
    conn = sqlite3.connect('allapis.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS TrainPredictions (
            "Train Number" INTEGER PRIMARY KEY AUTOINCREMENT,
            LineID INTEGER,
            Status TEXT,
            DestinationID INTEGER,
            TrainLengthInCars TEXT,
            TrackNumber TEXT
        )
    ''')

    for item in train_data:
        if item['Min'] in ['ARR', 'BRD'] or item['Min'] == "0":
            status = "On time"
        else:
            status = "Operational Delay"

        line_id = line_id_map.get(item['Line'], 0)
        destination_id = destination_id_map.get(item['Destination'], 0)
        cursor.execute('''
            INSERT INTO TrainPredictions (LineID, Status, DestinationID, TrainLengthInCars, TrackNumber) 
            VALUES (?, ?, ?, ?, ?)
        ''', (line_id, status, destination_id, item['Car'], item['Group']))

    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM TrainPredictions")
    count = cursor.fetchone()[0]
    print(f"Records in database: {count}")
    conn.close()

def main():
    train_data = fetch_train_data(api_key, station_codes)
    line_id_map = {
        'RD': 1,  # Red Line
        'BL': 2,  # Blue Line
        'GR': 3,  # Green Line
        'OR': 4,  # Orange Line
        'SV': 5,  # Silver Line
        'YL': 6   # Yellow Line
    }
    destination_id_map = create_destination_id_map(train_data)

    create_database(train_data, line_id_map, destination_id_map)
    print("Data loaded into SQLite database successfully.")

if __name__ == "__main__":
    main()
