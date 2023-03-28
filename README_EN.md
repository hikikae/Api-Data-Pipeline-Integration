# Api-Data-Pipeline-Integration
One of the main objectives of this project is the enrichment of static data from Google Maps and Yelp, through API.
<br>
<br>
<p align=center><img width="80%" src="https://github.com/hikikae/Api-Data-Pipeline-Integration/blob/main/images/ApiData-Pipeline-Integration.png"></p><br>

## ✨ Process Elements
- [Cloud Scheduler](#Scheduler)
- [Primer Cloud Function](#Primer)
- [Cloud Storage (Data Lake)](#Storage)
- [Segunda Cloud Function (ETL)](#Segunda)
- [Cloud Storage (Data Warehouse)](#Warehouse)
- [Slack API (Notificación)](#Slack)

### Cloud Scheduler
Cloud Scheduler is used to define a data update schedule for automatic loading of the data. An HTTP endpoint is called to execute the Cloud Function responsible for loading data from the API. The triggers section contains the URL for this purpose.

<p align=center><img width="50%" src="https://github.com/hikikae/Api-Data-Pipeline-Integration/blob/main/images/Cloud_Scheduler.gif"></p><br>

### <a href="https://github.com/hikikae/Api-Data-Pipeline-Integration/tree/main/details_review_data"> First Cloud Function </a>
The first Cloud Function obtains and stores relevant restaurant information. It uses the Geocoding API to obtain the coordinates of certain cities in the five most densely populated states in the United States. Then, the Places API extracts the restaurant data. 
<br>
<p align=center><img width="50%" src="https://github.com/hikikae/Api-Data-Pipeline-Integration/blob/main/images/details_review_data.gif"></p><br>

An HTTP request triggers the Cloud Function, and the data is stored in a Cloud Storage bucket that serves as a Data Lake.
<br>

<p align=center><img width="50%" src="https://github.com/hikikae/Api-Data-Pipeline-Integration/blob/main/images/details_review_data_trigger.png"></p><br>

It is important to note that both the Geocoding API and the Places API are provided by Google and require valid API credentials to function correctly.

### Cloud Storage 
Data is collected in a JSON format in its original form, without prior processing. This data is stored in a bucket that serves as a Data Lake within the Cloud Storage.
<br>
<p align=center><img width="50%" src="https://github.com/hikikae/Api-Data-Pipeline-Integration/blob/main/images/datalake.png"></p> <br>

### <a href="https://github.com/hikikae/Api-Data-Pipeline-Integration/tree/main/details_to_dw_function"> Second Cloud Function </a>
The second Cloud Function carries out the transformation, cleaning, and loading of the original data using the Pandas library. Once the process is complete, the data is sent to a Cloud Storage Bucket, and a notification is issued in Slack to inform about the completion of the process.
<br>
<p align=center><img width="50%" src="https://github.com/hikikae/Api-Data-Pipeline-Integration/blob/main/images/ETL_function.gif"></p> <br>

### Cloud Storage 
Once the data transformation processes are complete, the data is made available in a bucket that serves as a Data Warehouse. This approach facilitates collaboration and the sharing of valuable information between teams and contributes to making informed decisions based on accurate and up-to-date data.
<br>
<p align=center><img width="50%" src="https://github.com/hikikae/Api-Data-Pipeline-Integration/blob/main/images/datawarehouse.png"></p> <br>

## Slack API
The Slack integration is used to send a notification about the data upload process to avoid the need to constantly monitor the GCP platform. The URL of the webhook to execute the notification is unique and specific to each project.

<br>
<p align=center><img width="50%" src= "https://github.com/hikikae/Api-Data-Pipeline-Integration/blob/main/images/slack_api.gif"></p><br>

##  🛠️ Technologies 
- Google Cloud Plataform (GCP)
- Cloud Scheduler
- Cloud Function
- Cloud Storage
- Pandas
- Slack API
- Python

