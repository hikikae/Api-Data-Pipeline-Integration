import pandas as pd
from textblob import TextBlob
import datetime
from google.cloud import bigquery
from pandas.io import gbq
import re
import os
from google.cloud import storage

# Function to classify comments
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
    # Leer el archivo JSON y guardarlo en un DataFrame
    file_name = event['name']
    print(file_name)
    df = pd.read_json(f"gs://{event['bucket']}/{file_name}")
    
    # Cambiar el nombre de la columna 'rating' a 'rating_avg'
    df= df.rename(columns={'rating':'rating_avg'})
    print(df.head(2))
    
    # Dropear las columnas que no tienen rating 
    df = df.drop(df.loc[df['rating_avg'] == 'N/A'].index)
    
    #agregando la columna dependiendo del estado
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

     # Agregar la columna "state" al DataFrame
    df['state'] = state_mapping.get(filename)
    
    # Desanidar la columna 'reviews'
    df_expanded = df.explode('reviews').reset_index(drop=True)

    # Filtrar solo los elementos de la columna 'reviews' que son diccionarios
    df_expanded = df_expanded[df_expanded['reviews'].apply(lambda x: isinstance(x, dict))]

    # Normalizar la columna 'reviews'
    reviews_df = pd.json_normalize(df_expanded['reviews'])
    reviews_df = reviews_df.add_prefix('reviews.')

    # Unir el DataFrame original con el DataFrame de reviews normalizado
    df_data = pd.concat([df_expanded.drop('reviews', axis=1), reviews_df], axis=1)

    #Cambiando el formato de reviews.time
    #df_data['reviews.time'] = pd.to_datetime(df_data['reviews.time'], unit='s').dt.strftime('%Y-%m-%d %H:%M:%S.%f')

    #haciendo las modificaciones en el campo de userid
    new=df_data['reviews.author_url'].str.split(pat='/', n=6,expand=True)
    df_data['user_id']=new[5]
    df_data['user_id'] = df_data['user_id'].astype(str)

    #añadiendo lo del sentimiento 
    df_data['feeling'] = df_data['reviews.text'].apply(lambda x: classify_comment2(x) if pd.notnull(x) else 'No message')
    
    #agregando las columnas necesarias
    df_data['main_category']='food services'
    df_data['num_of_reviews']= 0
    df_data['platform']='detailsApi'
    df_data['resp']= "No response"
    #df_data['resp'] = df_data['resp'].astype(str)

    #cambiando nombres para que coincidan en la tabla
    df_data = df_data.rename(columns={'reviews.rating': 'rating','reviews.time':'date','reviews.text': 'opinion', 'place_id':'business_id','name':'local_name'})
    df_data = df_data[['user_id','business_id','local_name','latitude','longitude','num_of_reviews','state','main_category','date','rating','resp','opinion','feeling','platform']]
   
    #intentando limpiar las comillas en la columna opinion por emojis y caracteres extraños-----------------
    df_data['opinion'] = df_data['opinion'].str.replace('"', '')
    df_data['opinion'] = df_data['opinion'].apply(lambda x: x.encode('unicode-escape').decode('utf-8'))
    
    #eliminando duplicados
    df_data.drop_duplicates(inplace=True)

    #Paulo
    df_data.to_csv('gs://' + 'datasets-pg' + '/' + 'Details-Api' + '/' + filename + '.csv',index=False)

    return 'done'