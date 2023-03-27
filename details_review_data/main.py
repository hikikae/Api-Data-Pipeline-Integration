import os
import requests
from flask import jsonify
from google.cloud import storage
import json
import random 
import pandas as pd

#se agrega un random para cambiar un poco la longitud y latitud y asi obtener resultados distintos
def get_random_offset():
    return random.uniform(-0.01, 0.01)

def search_restaurants(request):
    locations = {
        "California": ["San Mateo","San Francisco", "Los Angeles", "San Diego", "Sacramento", "Santa Clara", "Fresno","Alameda", "Orange","Kern","Riverside", "San Joaquin","Contra Costa","Ventura"],
        "Texas": ["Harris","Dallas","Tarrant","Bexar","Travis","Collin","Denton","Hidalgo"," El Paso","Fort Bend","Montgomery","Williamson","Cameron","Nueces"],
        "Florida":["Miami-Dade","Broward","Palm Beach","Hillsborough","Orange","Pinellas","Duval","Lee","Polk","Brevard","Volusia","Pasco","Seminole","Sarasota"],
        "NuevaYork":["Kings","Queens","New York","Bronx","Richmond","Suffolk","Nassau","Westchester","Erie","Monroe","Onondaga","Orange","Rockland","Albany"],
        "Pensilvania":["Philadelphia","Allegheny","Delaware","Montgomery","Bucks","Lehigh","Lancaster","Chester","Northampton","Dauphin","Erie","Luzerne","York","Westmoreland"]
    }
    api_key = API_KEY
    
    for state, cities in locations.items():
        random.shuffle(cities)  # reordenamos las ciudades
        restaurant_data = []
        for city in cities:
            # se obtienen las coordenadas de las ciudades
            geocoding_url = f'https://maps.googleapis.com/maps/api/geocode/json?address={city},{state}&key={api_key}'
            geocoding_response = requests.get(geocoding_url)
            geocoding_result = geocoding_response.json()['results'][0]
            location_lat = geocoding_result['geometry']['location']['lat']+ get_random_offset()
            location_lng = geocoding_result['geometry']['location']['lng']+ get_random_offset()

            # parametros de busqueda
            query = 'restaurant'
            radius = 50000
            fields = 'name,rating,formatted_address,geometry,reviews'

            # buscamos con las coordenadas los restaurants en 50km 
            url = f'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={location_lat},{location_lng}&radius={radius}&type={query}&key={api_key}'

            # hacemos el request y obtenemos los resultados
            response = requests.get(url)
            results = response.json()['results']

            # para cada resultado se obtienen los detalles que se necesitan
            for result in results:
                place_id = result['place_id']
                details_url = f'https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields={fields}&key={api_key}'
                details_response = requests.get(details_url)
                details = details_response.json()['result']

                # Obteniendo los datos necesarios y agregandolos al diccionario
                restaurant = {
                    'name': details['name'],
                    'rating': details.get('rating', 'N/A'),
                    'address': details['formatted_address'],
                    'latitude': details['geometry']['location']['lat'],
                    'longitude': details['geometry']['location']['lng'],
                    'reviews': details.get('reviews', []),
                    'place_id': place_id
                }
                restaurant_data.append(restaurant)

        # se aplana el json 
        df = pd.json_normalize(restaurant_data)

        # de data lo convertimos a un diccionario
        restaurant_data_flat = df.to_dict('records') 

        # Guardar el archivo JSON
        storage_client = storage.Client()
        bucket_name = 'extra_sources'
        file_name = f"{state}.json"
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(f"Details-Api/{file_name}")
        blob.upload_from_string(json.dumps(restaurant_data_flat, indent=1, separators=(',', ': ')))

    # regresamos un mensaje 
    return 'Terminado'
