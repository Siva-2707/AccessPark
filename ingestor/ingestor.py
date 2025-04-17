import database as db
import halifax_ingestor as halifax
import toronto_ingestor as toronto
import hashlib
from util import safe_str

db.create_database_if_not_exist()
db.create_table_if_not_exist()

def insert_df_to_db(df):
    for _, row in df.iterrows():
        record_hash = hashlib.sha256(f"{row['CITY_LOT_ID']}{row['NAME']}".encode()).hexdigest()
        db.insert_into_accessibility_parking(
            record_hash=record_hash,
            city_lot_id=row['CITY_LOT_ID'],
            name=safe_str(row['NAME']),
            no_of_spots=row['NO_OF_SPOTS'],
            location=safe_str(row['LOCATION']),
            city=safe_str(row['CITY']),
            state=safe_str(row['STATE']),
            country=safe_str(row['COUNTRY'])
        )


def lambda_handler(event, context):
    # Get Halifax data & insert into DB
    insert_df_to_db(halifax.get_data())

    # Get Toronto data & insert into DB
    insert_df_to_db(toronto.get_data())
    return {
        'statusCode': 200,
        'body': 'Data ingestion completed successfully!'
    }

if __name__ == "__main__":
    lambda_handler(None, None)

