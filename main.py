from climate_data import table_processing 
import pandas as pd
import json



def get_Longitud(longitud):
    for i in range(len(df['Longitud'])) :
        longitud[i] = longitud[i].split(' ')[0]
        longitud[i] = longitud[i].replace('.', '')
        if len(longitud[i].split('-')) == 2:
            longitud[i] = int(longitud[i].split('-')[0] + longitud[i].split('-')[1]) / 2
    return longitud

def menu():
    print("Actividades disponibles: ")
    print("1: Tomar el sol\n2: Nadar\n3: Surf\n4: Pasear\n5: Nudismo\n6: Deporte pelota")
    choice = int(input("Escoja su actividad: "))

    if choice == 1:
        return("sol")
    elif choice == 2:
        return("nadar")
    elif choice == 3:
        return("surf")
    elif choice == 4:
        return("pasear")
    elif choice == 5:
        return("nudismo")
    elif choice == 6:
        return("deporte_pelota")


def filter1(df, activity):

    with open('activities.json') as file:
        activities = json.load(file)
    
    filters = activities[activity]["filtrado1"]
    for filter in filters.keys():
        if filters[filter] == "NULL":
            continue
        elif filter == "Longitud":
            min, max = filters[filter].split(",")
            df = df[df['Longitud'].astype(int) >= float(min)]
            df = df[df['Longitud'].astype(int) <= float(max)]
        else:
            column = filter
            value = filters[filter]
            if filter == "Grado_ocup" or filter == "Nudismo":
                df = df[df[column].isin(value)]
            elif filter == "Forma_de_a":
                df = df[~df[column].isin(value)]
            else:
                df = df[df[column] == value]

    return df


def filter2(df, activity):
    
    with open('activities.json') as file:
        activities = json.load(file)

    filters = activities[activity]["filtrado2"]
    final_columns = ["Nombre", "Coordena_2", "Coordena_3"]
    for filter in filters.keys():
        if filters[filter] == "True" :
            final_columns.append(filter)

    return df[final_columns]

    



def order_dataframe(df, activity):
    #loc = input("Indícame en qué ayuntamiento vas a estar: ")    SI HACE FALTA
    rankDict = dict()
    for d in df.iloc[:, 3:]:
        if d == 'waves':
            if activity == 'surf':
                order = False
            else:
                order = True
        elif d == 'wind' or d == 'cloud':
            order = True
        else:
            order = False
        
        df_order = df.sort_values(by=[d], ascending=order) ## intentar quedarse solo con la columna d y la que tiene los nombres de las playas, por eficiencia --> df[nombres]
        print(df_order)
    for NombrePlaya in df["Nombre"]:
        index = df_order[df_order["Nombre"] == NombrePlaya].index
        if NombrePlaya not in rankDict:
            rankDict[NombrePlaya] = index
        else:
            rankDict[NombrePlaya] += index

    #best = sorted(rankDict.values()) ####################################
    print(rankDict)




if __name__ == "__main__":


    df = pd.read_csv("playas.csv")
    df = df[["Nombre", "Longitud", "Grado_ocup", "Nudismo", "Bandera_az", "Auxilio_y_", "Forma_de_a",
            "Acceso_dis", "Autobús", "Aseos", "Zona_infan", "Submarinis", "Coordena_2", "Coordena_3"]]
    df['Longitud'] = get_Longitud(df['Longitud'])
    activity = menu()
    df_filtered1 = filter1(df, activity).reset_index()
    df_raw_clima = table_processing(df_filtered1[:5], 0, 17)
    df_filtered2 = filter2(df_raw_clima, activity)

    print(df_filtered2)
    order_dataframe(df_filtered2, activity)






