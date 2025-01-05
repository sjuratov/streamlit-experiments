import sys
import os
import logging
from azure.cosmos import CosmosClient, exceptions
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

load_dotenv()

accountName = os.getenv("accountName")
databaseName = os.getenv("databaseName")
containerName = os.getenv("collection")

def get_cosmosdb_info(endpoint=f"https://{accountName}.documents.azure.com:443/", database_name=databaseName, container_name=containerName):
    credential = DefaultAzureCredential()

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

def get_items(container):
    items = list(container.query_items(
        query="SELECT * FROM c",
        enable_cross_partition_query=True
    ))
    return items

def update_item(container, item):
    container.upsert_item(item)

def delete_item(container, item):
    container.delete_item(item=item, partition_key=item['id'])

def create_item(container, item):
    container.create_item(item)

def insert_items(container):
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
        "id": "0",
        "userId": "0"
    }
    )

def main():
    client, database, container = get_cosmosdb_info(endpoint=f"https://{accountName}.documents.azure.com:443/", database_name=databaseName, container_name=containerName)
    insert_items(container)


if __name__ == '__main__':
    main()