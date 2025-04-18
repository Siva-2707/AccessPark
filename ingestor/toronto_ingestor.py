import requests
import pandas as pd
import ast

import logging
from logger_config import logger

logger = logging.getLogger(__name__)

def get_data():
  logger.info("Fetching data from Toronto...")

  # Toronto Open Data is stored in a CKAN instance. It's APIs are documented here:
  # https://docs.ckan.org/en/latest/api/

  # To hit our API, you'll be making requests to:
  base_url = "https://ckan0.cf.opendata.inter.prod-toronto.ca"

  # Datasets are called "packages". Each package can contain many "resources"
  # To retrieve the metadata for this package and its resources, use the package name in this page's URL:
  url = base_url + "/api/3/action/package_show"
  params = { "id": "parking-lot-facilities"}
  package = requests.get(url, params = params).json()

  # To get resource data:
  for idx, resource in enumerate(package["result"]["resources"]):
        # To get metadata for non datastore_active resources:
        if 'readme' not in resource['name']  and not resource["datastore_active"]:
            url = base_url + "/api/3/action/resource_show?id=" + resource["id"]
            resource_metadata = requests.get(url).json()
            # print(json.dumps(resource_metadata,indent=4))
            # From here, you can use the "url" attribute to download this file

  toronto_data = pd.read_excel(resource_metadata['result']['url'])
  # print(f'Toronto data before filtering: {len(toronto_data)}')
  if not toronto_data.empty:
    toronto_data = toronto_data[(toronto_data['Access'].str.lower() == 'public') & (toronto_data['Handicap Parking Spaces'] > 0)]

  toronto_data = toronto_data.rename(columns={'Parking Lot Asset ID':'CITY_LOT_ID','Park Name':'NAME','Handicap Parking Spaces':'NO_OF_SPOTS','GIS Coordinate':'LOCATION'})
  toronto_data = toronto_data[['CITY_LOT_ID','NAME','NO_OF_SPOTS','LOCATION']]
  toronto_data['LOCATION'] = toronto_data['LOCATION'].apply(convert_to_list)
  toronto_data['CITY'] = 'Toronto'
  toronto_data['STATE'] = 'ON'
  toronto_data['COUNTRY'] = 'Canada'
  # print(f'Toronto data after filtering: {len(toronto_data)}')
  logger.info(f"Fetched {len(toronto_data)} records from Toronto")
  return toronto_data

def convert_to_list(coord_str):
    return list(ast.literal_eval(coord_str))