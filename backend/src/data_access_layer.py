import mongoengine
from src.utils.config import config 

print("hello")

def connect_to_db():
    try:
        connection = mongoengine.connect(db=config.db_name, host=config.connection_string)
        
        db = connection.get_database(config.db_name)
        print("We're connected to MongoDB:", db.name)
    except Exception as err:
        print("Error connecting to MongoDB:", err)
