import sys
import os
import logging
from azure.cosmos import CosmosClient, exceptions
from dotenv import load_dotenv

load_dotenv()

accountName = os.getenv("accountName")
databaseName = os.getenv("databaseName")
containerName = os.getenv("collection")

def get_cosmosdb_info(credential, endpoint=f"https://{accountName}.documents.azure.com:443/", database_name=databaseName, container_name=containerName):
    """Get CosmosDB client, database and container objects"""
    endpoint = endpoint
    database_name = database_name
    container_name = container_name

    # Create a logger for the 'azure' SDK
    logger = logging.getLogger('azure')
    logger.setLevel(logging.DEBUG)

    # Configure a console output
    handler = logging.StreamHandler(stream=sys.stdout)
    logger.addHandler(handler)

    try:
        client = CosmosClient(endpoint, credential, logging_enable=True)
        database = client.get_database_client(database_name)
        container = database.get_container_client(container_name)
    except exceptions.CosmosHttpResponseError:
        raise
    
    return client, database, container

def get_items(container, query = "SELECT * FROM c"):
    """Get items from the container"""
    items = list(container.query_items(
        query=query,
        enable_cross_partition_query=True
    ))
    return items

def update_item(container, item):
    """Update an item in the container"""
    container.upsert_item(item)

def delete_item(container, item):
    """Delete an item from the container"""
    container.delete_item(item=item, partition_key=item['id'])

def create_item(container, item):
    """Create an item in the container"""
    container.create_item(item)

def insert_items(container, uuid="0"):
    """Insert items into the container"""
    container.upsert_item({
        "chat_history": [
            {
                "role": "user",
                "content": "write about zurich"
            },
            {
                "role": "assistant",
                "content": "Zurich, the largest city in Switzerland."
            },
            {
                "role": "user",
                "content": "About Zagreb"
            },
            {
                "role": "assistant",
                "content": "Zagreb, the capital of Croatia."
            }
        ],
        "id": uuid,
        "userId": uuid
    }
    )

def create_unique_id(credential):
    """Create a unique ID for the user"""
    import uuid
    import jwt

    token = credential.get_token("https://management.azure.com/.default")
    decoded_token = jwt.decode(token.token, options={"verify_signature": False})
    object_id = decoded_token.get('oid')
    guid = uuid.uuid5(uuid.NAMESPACE_DNS, object_id)
    return str(guid)

def main():
    client, database, container = get_cosmosdb_info(endpoint=f"https://{accountName}.documents.azure.com:443/", database_name=databaseName, container_name=containerName)
    insert_items(container)


if __name__ == '__main__':
    main()