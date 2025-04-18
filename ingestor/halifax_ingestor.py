import pandas as pd
import requests
import logging
from logger_config import logger

logger = logging.getLogger(__name__)

def get_data():
  logger.info("Fetching data from Halifax...")
  URL = 'https://services2.arcgis.com/11XBiaBYA9Ep0yNJ/arcgis/rest/services/Accessible_Parking_Spots/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson'
  data = requests.get(URL).json()
  # print(json.dumps(data,indent=4))
  df = pd.DataFrame(data['features'])
  property_df = pd.DataFrame([row['properties'] for row in data['features']])
  coordinates_df = pd.DataFrame([row['geometry'] for row in data['features']])
  df = pd.concat([property_df,coordinates_df],axis=1)
  df.rename(columns={'ACCPRKID':'CITY_LOT_ID','STREET_NAME':'NAME','NUMSPOTS':'NO_OF_SPOTS','coordinates':'LOCATION'}, inplace=True)
  df = df[['CITY_LOT_ID','NAME','NO_OF_SPOTS','LOCATION']]
  df['CITY'] = 'Halifax'
  df['STATE'] = 'NS'
  df['COUNTRY'] = 'Canada'
  logger.info(f"Fetched {len(df)} records from Halifax")
  return df