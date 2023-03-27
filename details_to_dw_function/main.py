import pandas as pd
from textblob import TextBlob
import datetime
from google.cloud import bigquery
from pandas.io import gbq
import re
import os
from google.cloud import storage

# Funcion que clasifica los sentimientos 
def classify_comment2(comment):
    if comment is None:
        return 'No message'
    else:
        sentiment = TextBlob(comment).sentiment.polarity
        if sentiment > 0:
            return 'Positive'
        elif sentiment < 0:
            return 'Negative'
        else:
            return 'Neutral'


def procesar_datos_json(event, context):
    # Lee el archivo JSON y lo guarda en un DataFrame
    file_name = event['name']
    print(file_name)
    df = pd.read_json(f"gs://{event['bucket']}/{file_name}")
    
    # Cambia el nombre de la columna 'rating' a 'rating_avg'
    df= df.rename(columns={'rating':'rating_avg'})
    print(df.head(2))
    
    # Dropea las columnas que no tienen rating 
    df = df.drop(df.loc[df['rating_avg'] == 'N/A'].index)
    
    # Agrega la columna 'state' dependiendo del estado
    filename = os.path.splitext(os.path.basename(event['name']))[0]
    print(filename)
    
    # Mapear el nombre del archivo a un estado
    state_mapping = {
        'California': 'CA',
        'Texas': 'TX',
        'Pensilvania': 'PA',
        'Florida': 'FL',
        'NuevaYork': 'NY'
    }

     # Agrega la columna "state" al DataFrame
    df['state'] = state_mapping.get(filename)
    
    # Desanida la columna 'reviews'
    df_expanded = df.explode('reviews').reset_index(drop=True)

    # Filtra solo los elementos de la columna 'reviews' que son diccionarios
    df_expanded = df_expanded[df_expanded['reviews'].apply(lambda x: isinstance(x, dict))]

    # Normaliza la columna 'reviews'
    reviews_df = pd.json_normalize(df_expanded['reviews'])
    reviews_df = reviews_df.add_prefix('reviews.')

    # Une el DataFrame original con el DataFrame de reviews normalizado
    df_data = pd.concat([df_expanded.drop('reviews', axis=1), reviews_df], axis=1)

    # Obtiene el user_id que se encuentra en la columna de reviews.author_id
    new=df_data['reviews.author_url'].str.split(pat='/', n=6,expand=True)
    df_data['user_id']=new[5]
    df_data['user_id'] = df_data['user_id'].astype(str)

    # Añade la columna donde revisa que tipo de opinion se da 'sentimiento', positivo, negativo o neutral 
    df_data['feeling'] = df_data['reviews.text'].apply(lambda x: classify_comment2(x) if pd.notnull(x) else 'No message')
    
    # Agrega las columnas necesarias para que coincidan con las tablas creadas en el data warehouse
    df_data['main_category']='food services'
    df_data['num_of_reviews']= 0
    df_data['platform']='detailsApi'
    df_data['resp']= "No response"
    #df_data['resp'] = df_data['resp'].astype(str)

    # Renombra los nombres para que coincidan en la tabla
    df_data = df_data.rename(columns={'reviews.rating': 'rating','reviews.time':'date','reviews.text': 'opinion', 'place_id':'business_id','name':'local_name'})
    df_data = df_data[['user_id','business_id','local_name','latitude','longitude','num_of_reviews','state','main_category','date','rating','resp','opinion','feeling','platform']]
   
    # Elimina los emojis o caracteres extraños de la columna de 'opinion'
    df_data['opinion'] = df_data['opinion'].str.replace('"', '')
    df_data['opinion'] = df_data['opinion'].apply(lambda x: x.encode('unicode-escape').decode('utf-8'))
    
    # Elimina duplicados
    df_data.drop_duplicates(inplace=True)

    # Envia los datos ya procesados al datawarehouse
    df_data.to_csv('gs://' + 'datasets-pg' + '/' + 'Details-Api' + '/' + filename + '.csv',index=False)

    return 'done'