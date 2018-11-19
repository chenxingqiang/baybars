from copy import deepcopy

# 3rd Party
from azure.cosmosdb.table.tableservice import TableService
from azure.cosmosdb.table.tablebatch import TableBatch
from azure.cosmosdb.table.models import Entity


class PartitionKeyNotFoundError(Exception):
  pass

class ClusteringKeyNotFoundError(Exception):
  pass


class AzureTable(object):

  def __init__(self, account_name: str, 
                     account_key: str, 
                     table_name: str, 
                     partition_key_field: str,
                     clustering_key_field: str):
    self.table = TableService(account_name=account_name, 
                              account_key=account_key)
    self.table_name = self.table_name
    self.partition_key_field = partition_key_field
    self.clustering_key_field = clustering_key_field

  @property
  def partition_key_name(self) -> str:
    return 'PartitionKey'

  @property
  def clustering_key_name(self) -> str:
    return 'RowKey'

  def get_payload(self, payload: dict):
    output = None
    item = deepcopy(payload)
    partition_key = payload.get(self.partition_key_field) 
    clustering_key = payload.get(self.clustering_key_field)
    if partition_key is None:
      raise PartitionKeyNotFoundError('payload={} does not have a partition key')
    if clustering_key is None:
      raise ClusteringKeyNotFoundError('payload={} does not have a clustering key')
      
    item.update({self.partition_key_name: partition_key, 
                 self.clustering_key_name: clustering_key })

    return item

  def create(self):
    return self.table.create_table(self.table_name)

  def insert(self, item: dict):
    return self.table.insert_entity(self.table_name, self.get_payload(item)) 

  def update(self, item: dict):
    return self.table.update_entity(self.table_name, self.get_payload(item)) 

  def upsert(self, item: dict):
    return self.table.insert_or_replace_entity(self.table_name, self.get_payload(item)) 

  def insert_batch(self, items: list):
    batch = TableBatch()
    for item in items:
      batch.insert_entity(self.get_payload(item))

    return self.table.commit_batch(self.table_name, batch) 

  def get(self, partition_key: str, clustering_key: str):
    return self.table.get_entity(self.table_name, 
                                 partition_key, 
                                 clustering_key)
                              
  def get_by_partition(self, partition_key: str) -> list:
    return self.table.query_entities(self.table_name, 
                                     filter="{} eq '{}'".format(self.partition_key_name, partition_key))