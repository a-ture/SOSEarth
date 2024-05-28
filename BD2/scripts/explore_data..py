import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Percorso della directory dei file CSV
csv_directory = os.path.join(os.path.dirname(__file__), '../data')


# Funzione per trovare anomalie nei dati
def find_anomalies(df):
    anomalies = {}
    # Trova colonne con valori nulli
    null_values = df.isnull().sum()
    anomalies['null_values'] = null_values[null_values > 0]

    # Trova outlier usando il metodo IQR
    Q1 = df.quantile(0.25)
    Q3 = df.quantile(0.75)
    IQR = Q3 - Q1
    outliers = ((df < (Q1 - 1.5 * IQR)) | (df > (Q3 + 1.5 * IQR))).sum()
    anomalies['outliers'] = outliers[outliers > 0]

    return anomalies


# Funzione per visualizzare anomalie
def visualize_anomalies(anomalies, file):
    for key, value in anomalies.items():
        if not value.empty:
            value.plot(kind='bar', title=f'{key} in {file}')
            plt.xlabel('Columns')
            plt.ylabel('Count')
            plt.show()


# Funzione per analizzare e trovare anomalie nei CSV
def analyze_csv_files(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.csv'):
                file_path = os.path.join(root, file)
                try:
                    print(f'Analyzing {file_path}')

                    # Carica il CSV
                    df = pd.read_csv(file_path, on_bad_lines='skip', skiprows=4)

                    # Gestione di possibili righe di intestazione multiple
                    if not df.columns.is_unique:
                        df.columns = df.iloc[0]
                        df = df[1:]

                    # Normalizza i nomi delle colonne
                    df.columns = [str(col).strip().lower().replace(' ', '_') for col in df.columns]

                    # Rimozione delle colonne con nomi non significativi
                    df = df.loc[:, ~df.columns.str.contains('^unnamed')]

                    # Trova le anomalie
                    anomalies = find_anomalies(df)

                    # Visualizza le anomalie
                    visualize_anomalies(anomalies, file)

                except Exception as e:
                    print(f'Error analyzing {file}: {e}')


# Analizza tutti i file CSV nella directory
analyze_csv_files(csv_directory)
