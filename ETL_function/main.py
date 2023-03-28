import pandas as pd
from textblob import TextBlob
import datetime
from google.cloud import bigquery
from pandas.io import gbq
import re
import os
from google.cloud import storage
import json
import requests
from urllib.request import Request


# funcion para enviar un mensaje en el canal de slack mencionando que terminó
def enviar_mensaje_slack(request):
    webhook_url = 'https://hooks.slack.com/services/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'
    mensaje = 'Los datos de details api se ha terminado'
    headers = {'Content-type': 'application/json'}
    payload = {'text': mensaje}
    response = requests.post(webhook_url, headers=headers, data=json.dumps(payload))
    print('Mensaje enviado:', response.status_code, response.text)
    return 'Mensaje enviado'

# Función para clasificar los comentarios
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


def procesar_datos_json(event, context, request):
    # Lee el archivo JSON y guardarlo en un DataFrame
    file_name = event['name']
    print(file_name)
    df = pd.read_json(f"gs://{event['bucket']}/{file_name}")
    
    # Cambia el nombre de la columna 'rating' a 'rating_avg'
    df= df.rename(columns={'rating':'rating_avg'})
    print(df.head(2))
    
    # Dropea las columnas que no tienen rating 
    df = df.drop(df.loc[df['rating_avg'] == 'N/A'].index)
    
    # Agrega la columna dependiendo del estado
    filename = os.path.splitext(os.path.basename(event['name']))[0]
    print(filename)
    
    # Mapea el nombre del archivo a un estado
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

    # Extra el user_id de la columna de reviews.author_url
    new=df_data['reviews.author_url'].str.split(pat='/', n=6,expand=True)
    df_data['user_id']=new[5]
    df_data['user_id'] = df_data['user_id'].astype(str)

    # Añade una columna con el sentimiento 
    df_data['feeling'] = df_data['reviews.text'].apply(lambda x: classify_comment2(x) if pd.notnull(x) else 'No message')
    
    # Agrega las columnas para que tenga el mismo formato que los demas datos de las plataformas
    df_data['main_category']='food services'
    df_data['num_of_reviews']= 0
    df_data['platform']='detailsApi'
    df_data['resp']= "No response"

    # Renombra algunas columnas
    df_data = df_data.rename(columns={'reviews.rating': 'rating','reviews.time':'date','reviews.text': 'opinion', 'place_id':'business_id','name':'local_name'})
    df_data = df_data[['user_id','business_id','local_name','latitude','longitude','num_of_reviews','state','main_category','date','rating','resp','opinion','feeling','platform']]
   
    # Elimina los emojis y caracteres extraños de la columna opinion 
    df_data['opinion'] = df_data['opinion'].str.replace('"', '')
    df_data['opinion'] = df_data['opinion'].apply(lambda x: x.encode('unicode-escape').decode('utf-8'))
    
    # Elimina duplicados
    df_data.drop_duplicates(inplace=True)

    # Envia los datos al data warehouse en formato csv
    df_data.to_csv('gs://' + 'datasets-pg' + '/' + 'Details-Api' + '/' + filename + '.csv',index=False)
    
    # Envia el mensaje de termino al grupo de slack 
    enviar_mensaje_slack()

    return 'done'