import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def load_data():
    db_path = 'allapis.db'
    conn = sqlite3.connect(db_path)
    query = '''
    SELECT LineID, SUM(CAST(TrainLengthInCars AS INTEGER)) AS TotalCars, COUNT(*) AS TotalTrains 
    FROM TrainPredictions
    GROUP BY LineID
    '''
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def visualize_train_cars(df):
    plt.figure(figsize=(12, 8))

    color_map = {
        1: '#FF0000',  # Red
        2: '#0000FF',  # Blue
        3: '#00FF00',  # Green
        4: '#FFA500',  # Orange
        5: '#C0C0C0',  # Silver
        6: '#FFFF00'   # Yellow
    }

    df['colors'] = df['LineID'].map(color_map)

    bar_plot = sns.barplot(x='LineID', y='TotalCars', data=df, palette=df['colors'])
    plt.title('Total Train Cars by Line', fontsize=20)
    plt.xlabel('LineID', fontsize=16)
    plt.ylabel('Total Cars', fontsize=16)
    plt.tight_layout()
    plt.show()

def calculate_and_export_train_car_totals():
    conn = sqlite3.connect('allapis.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT LineID,
           SUM(CAST(TrainLengthInCars AS INTEGER)) AS TotalCars,
           COUNT(*) AS TotalTrains,
           CAST(SUM(CAST(TrainLengthInCars AS INTEGER)) AS FLOAT) / COUNT(*) AS AvgCarsPerTrain
    FROM TrainPredictions
    GROUP BY LineID
    ''')
    
    line_totals = cursor.fetchall()
    conn.close()
    
    file_path = 'train_line_totals.txt'
    
    with open(file_path, 'w') as file:
        file.write('LineID | Total Cars | Total Trains | Average Cars Per Train\n')
        file.write('-------------------------------------------------------\n')
        for line in line_totals:
            line_text = f"{line[0]} | {line[1]} | {line[2]} | {line[3]:.2f}\n"
            file.write(line_text)
    
    print(f"Train car totals data has been written to {file_path}")



def main():
    df = load_data()
    visualize_train_cars(df)
    calculate_and_export_train_car_totals()

if __name__ == "__main__":
    main()