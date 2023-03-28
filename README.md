# Api-Data-Pipeline-Integration
Uno de los principales objetivos para este proyecto es el enriquecimiento de los datos estáticos de Google Maps y Yelp, por medio de API´s.
<br>
<br>
<p align=center><img width="80%" src="https://github.com/hikikae/Api-Data-Pipeline-Integration/blob/main/_src/API-Data-Pipeline-Integration.png"></p><br>

## ✨ Elementos del Proceso
- [Cloud Scheduler](#Scheduler)
- [Cloud Function (Get_API_Data)](#Get)
- [Cloud Storage (Data Lake)](#Storage)
- [Segunda Cloud Function (ETL_API_Function)](#Segunda)
- [Cloud Scheduler](#Scheduler)
- [Cloud Storage (Data Warehouse)](#Warehouse)
- [Slack API (Notificación)](#Slack)

### Cloud Scheduler
El proceso comienza definiendo un horario de actualización de los datos para que la carga sea de forma automática, para ello se utilizó Cloud Scheduler, este llama a un endpoint HTTP que ejecuta al Cloud Function que carga los datos de las API's.La URL se encuentra en la sección de activadores.

<br>
<p align=center><img width="80%" src="https://github.com/hikikae/Api-Data-Pipeline-Integration/blob/main/_src/Cloud_Scheduler.gif"></p><br>


### <a href="https://github.com/hikikae/Api-Data-Pipeline-Integration/tree/main/details_review_data"> Cloud Function (Get_API_Data)</a>
El flujo de trabajo de la primer Cloud Function es obtener y almacenar la información relevante de los restaurantes. Para ello, se obtienen primero las coordenadas de ciertas ciudades dentro de los cinco estados con mayor densidad poblacional de los Estados Unidos, mediante Geocoding API. Posteriormente, se utiliza Places API para extraer los datos de restaurantes.

<br>
<p align=center><img width="80%" src="https://github.com/hikikae/Api-Data-Pipeline-Integration/blob/main/_src/details_review_data.gif"></p><br>

Cloud Function es activada mediante una solicitud de HTTP. 

<br>
<p align=center><img width="80%" src="https://github.com/hikikae/Api-Data-Pipeline-Integration/blob/main/_src/details_review_data_trigger.png"></p><br>

Es importante mencionar que tanto la Geocoding API como la Places API son proporcionadas por Google y requieren credenciales de API válidas para su correcto funcionamiento.
<br>

### Cloud Storage (Data Lake) 
Los datos se recolectan en su forma original, sin procesamiento previo, en un formato JSON y son almacenados junto con la data estática en el bucket de Cloud Storage, es decir el Data Lake.  

<br>
<p align=center><img width="80%" src="https://github.com/hikikae/Api-Data-Pipeline-Integration/blob/main/_src/datalake.png"></p> <br>

### <a href="https://github.com/hikikae/Api-Data-Pipeline-Integration/tree/main/details_to_dw_function"> Cloud Function (ETL_API_Function) </a>
En esta Cloud Function se llevó a cabo la transformación, limpieza y carga de los datos originales mediante la biblioteca de Pandas. Una vez completado el proceso, los datos se envían a un Bucket de Cloud Storage y se emite una notificación en Slack para informar sobre la finalización del mismo.

<br>
<p align=center><img width="80%" src="https://github.com/hikikae/Api-Data-Pipeline-Integration/blob/main/_src/ETL_function.gif"></p> <br>

### Cloud Scheduler
Una hora después del proceso de ETL se ejecuta una query para añadir esa nueva data a la tabla principal que contiene ya, la data estática.

<br>
<p align=center><img width="80%" src="https://github.com/hikikae/Api-Data-Pipeline-Integration/blob/main/_src/scheduler_query.png"></p> <br>

### Cloud Storage (Data Warehouse)
Una vez que se han llevado a cabo los procesos de transformación de los datos, éstos se ponen a disposición en el bucket del proyecto que es nuestro Datawarehouse. De esta forma, tanto el departamento de Data Analytics como el de Data Science pueden acceder a ellos y utilizarlos para sus respectivos análisis y proyectos. Este enfoque facilita la colaboración y el intercambio de información valiosa entre los equipos y contribuye a la toma de decisiones informadas basadas en datos precisos y actualizados.

<br>
<p align=center><img width="80%" src="https://github.com/hikikae/Api-Data-Pipeline-Integration/blob/main/_src/datawarehouse.png"></p> <br>

### Slack API
La finalidad de la integración con Slack es enviar una notificación acerca del proceso de carga de datos, con el propósito de evitar la necesidad de estar monitorizando constantemente la plataforma de GCP.
La URL del webhook para ejecutar la notificación es única y específica para cada proyecto.

<br>
<p align=center><img width="80%" src= "https://github.com/hikikae/Api-Data-Pipeline-Integration/blob/main/_src/slack_api.gif"></p><br>

##  🛠️ Tecnologías 
- Google Cloud Plataform (GCP)
- Cloud Scheduler
- Cloud Function
- Cloud Storage
- Pandas
- Slack API
- Python

