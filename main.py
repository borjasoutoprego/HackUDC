from climate_data import table_processing

import numpy as np
import json
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

df = pd.read_csv("playas.csv")

df = df[["Nombre", "Longitud", "Grado_ocup", "Condicione", "Nudismo", "Bandera_az", "Auxilio_y_", "Forma_de_a", "Acceso_dis", "Autobús", "Aseos", "Zona_infan", "Submarinis", "Coordena_2", "Coordena_3", "Composici"]]

#print(df.head())
#print(df.dtypes)

# No tenemos nulos
df.isnull().sum()
df.duplicated(subset=['Coordena_2', 'Coordena_3']).sum()
# no hay duplicados en las coordenadas

def get_Longitud(longitud):
    for i in range(len(df['Longitud'])) :
        longitud[i] = longitud[i].split(' ')[0]
        longitud[i] = longitud[i].replace('.', '')
        if len(longitud[i].split('-')) == 2:
            longitud[i] = int(longitud[i].split('-')[0] + longitud[i].split('-')[1]) / 2
    longitud = longitud.astype(int)
    return longitud

def menu():
    print("Actividades dispoñíbeis: ")
    print("1: Tomar o sol\n2: Nadar\n3: Surf\n4: Pasear\n5: Nudismo")
    choice = input("Escolla a súa actividade: ")
    return choice

def filtrado():
    df['longitud'] = get_Longitud(df['Longitud'])
    choice = int(menu())
    if choice == 1:
        df1 = df[df['Composici'] == 'Arena']
        df1 = df1[df1['Bandera_az'] == 'Sí']
    elif choice == 2:
        df1 = df[df['Condicione'] == 'Aguas tranquilas'] ### Pendentes de Carlos
        df1 = df1[(df1['Grado_ocup'] != 'Alto')]  # Revisar a ineficiencia
        df1 = df1[df1['Grado_ocup'] != 'Medio / Alto']
    elif choice == 3:
        df1 = df[df['Condicione'] != 'Aguas tranquilas'] ### Pendentes de Carlos
        df1 = df1[df1['Grado_ocup'] != 'Alto'] # Revisar a ineficiencia
        df1 = df1[df1['Grado_ocup'] != 'Medio / Alto']
        df1 = df1[df1['Forma_de_a'] != 'A pie difícil']
    elif choice == 4:
        df1 = df[df['Composici'] == 'Arena']
        df1 = df1[df1['Bandera_az'] == 'Sí']
        df1 = df1[df1['Longitud'] >= 300]
    elif choice == 5:
        df1 = df[df['Nudismo'] != 'No']

    return df1


if __name__ == "__main__":
    
    df = filtrado()[:5].reset_index()
    day = int(input("Cuando quieres ir a la playa?"))
    # lo mismo para la hora
    # preguntar tambien distancia en km
    print(table_processing(df, day, 17))

    
