# Api-Data-Pipeline-Integration
Uno de los principales objetivos para este proyecto es el enriquecimiento de los datos estáticos de Google Maps y Yelp, por medio de API´s.
<br>
<br>
<p align=center><img width="80%" src="https://github.com/hikikae/Api-Data-Pipeline-Integration/blob/main/images/ApiData-Pipeline-Integration.png"></p><br>

# Proceso
El proceso comienza definiendo un horario de actualización de los datos para que la carga sea de forma automática, para ello se utilizó Cloud Scheduler que llama a un extremo HTTP que se ejecuta en Cloud Function.

<p align=center><img width="50%" src="https://github.com/hikikae/Api-Data-Pipeline-Integration/blob/main/images/Cloud_Scheduler.gif"></p><br>

El flujo de trabajo de la primer Cloud Function es obtener y almacernar la información relevante de los restaurantes. Para ello, se obtienen primero las coordenadas de ciertas ciudades dentro de los cinco estados conmayor densidad poblacional de los Estados Unidos, mediante Geocoding API. Posteriormente, se utiliza Places API para extraer los datos de restaurantes.

Cloud Function es activada mediante una solicitud de HTTP y los datos son almacenados en un bucket de Cloud Storage que funge como Data Lake. 

Es importante mencionar que tanto la Geocoding API como la Places API son proporcionadas por Google y requieren credenciales de API válidas para su correcto funcionamiento. Además, el almacenamiento de los datos obtenidos en un Cloud Storage también requiere de credenciales válidas y autorizaciones adecuadas.
