import unittest
from unittest.mock import Mock

from google.protobuf.timestamp_pb2 import Timestamp

from viam.components.data import DataClient
from viam.proto.app.data import (
    DataPipelineConfig,
    DataPipelineList,
    DataPipeline,
    LogSchema,
    LogSchemaField,
    LogSchemaFieldType,
    MQLQuery,
    MQLQueryResponse,
    MQLQueryResponseRow,
    TabularDataSourceType,
)
from viam.utils import timestamp_to_proto

# Mock service for DataPipelines
class MockDataPipelines:
    def __init__(self):
        self.name = ""
        self.org_id = ""
        self.schedule = ""
        self.mql_binary = []
        self.enable_backfill = False
        self.data_source_type = TabularDataSourceType.TABULAR_DATA_SOURCE_TYPE_UNSPECIFIED

    async def CreateDataPipeline(self, name: str, org_id: str, schedule: str, mql_binary: list[str], enable_backfill: bool, data_source_type: TabularDataSourceType) -> str:
        self.name = name
        self.org_id = org_id
        self.schedule = schedule
        self.mql_binary = mql_binary
        self.enable_backfill = enable_backfill
        self.data_source_type = data_source_type
        return ID

    async def DeleteDataPipeline(self, id: str, org_id: str):
        pass

    async def ListDataPipelines(self, org_id: str) -> DataPipelineList:
        return DataPipelineList(
            pipelines=[
                DataPipeline(
                    id=ID,
                    name=NAME,
                    organization_id=ORG_ID,
                    schedule=SCHEDULE,
                    mql_binary=MQL_BINARY,
                    enabled=True,
                    created_on=TIMESTAMP_PROTO,
                    updated_at=TIMESTAMP_PROTO,
                    data_source_type=DATA_SOURCE_TYPE,
                )
            ]
        )

    async def UpdateDataPipeline(self, id: str, org_id: str, name: str, schedule: str, mql_binary: list[str], enable_backfill: bool, data_source_type: TabularDataSourceType):
        self.name = name
        self.org_id = org_id
        self.schedule = schedule
        self.mql_binary = mql_binary
        self.enable_backfill = enable_backfill
        self.data_source_type = data_source_type

    async def GetMQLQueryResponse(self, org_id: str, query: MQLQuery) -> MQLQueryResponse:
        return MQLQueryResponse(
            rows=[
                MQLQueryResponseRow(
                    values=[
                        "test",
                        1,
                        True,
                    ]
                )
            ]
        )

    async def GetLogSchema(self, org_id: str) -> LogSchema:
        return LogSchema(
            fields=[
                LogSchemaField(
                    name="test",
                    type=LogSchemaFieldType.LOG_SCHEMA_FIELD_TYPE_STRING,
                )
            ]
        )

# Mock channel for testing
class ChannelFor:
    def __init__(self, services):
        self.services = services

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

# Constants
ID = "test-id"
NAME = "test-name"
ORG_ID = "test-org-id"
SCHEDULE = "test-schedule"
TIMESTAMP = 1678886400
TIMESTAMP_PROTO = timestamp_to_proto(TIMESTAMP)
MQL_BINARY = []
ENABLE_BACKFILL = True
DATA_SOURCE_TYPE = TabularDataSourceType.TABULAR_DATA_SOURCE_TYPE_UNSPECIFIED
STANDARD_DATA_SOURCE_TYPE = TabularDataSourceType.TABULAR_DATA_SOURCE_TYPE_STANDARD

DATA_SOURCE_TYPE = TabularDataSourceType.TABULAR_DATA_SOURCE_TYPE_STANDARD
ENABLE_BACKFILL = True

PROTO_DATA_PIPELINE = DataPipeline(
    id=ID,
    name=NAME,
    organization_id=ORG_ID,
    schedule=SCHEDULE,
    mql_binary=MQL_BINARY,
    enabled=True,
    created_on=TIMESTAMP_PROTO,
    updated_at=TIMESTAMP_PROTO,
    data_source_type=DATA_SOURCE_TYPE,
)
DATA_PIPELINE = DataClient.DataPipeline.from_proto(PROTO_DATA_PIPELINE)

DATA_SERVICE_METADATA = {"test": "test"}


class TestDataPipelines(unittest.TestCase):
    async def test_create_data_pipeline(self, service: MockDataPipelines):
        async with ChannelFor([service]) as channel:
            client = DataClient(channel, DATA_SERVICE_METADATA)
            id = await client.create_data_pipeline(ORG_ID, NAME, MQL_BINARY, SCHEDULE, ENABLE_BACKFILL, DATA_SOURCE_TYPE)
            assert id == ID
            assert service.name == NAME
            assert service.org_id == ORG_ID
            assert service.schedule == SCHEDULE
            assert service.mql_binary == MQL_BINARY
            assert service.enable_backfill == ENABLE_BACKFILL
            assert service.data_source_type == DATA_SOURCE_TYPE

    async def test_delete_data_pipeline(self, service: MockDataPipelines):
        async with ChannelFor([service]) as channel:
            client = DataClient(channel, DATA_SERVICE_METADATA)
            await client.delete_data_pipeline(ID, ORG_ID)

    async def test_list_data_pipelines(self, service: MockDataPipelines):
        async with ChannelFor([service]) as channel:
            client = DataClient(channel, DATA_SERVICE_METADATA)
            pipelines = await client.list_data_pipelines(ORG_ID)
            assert len(pipelines) == 1
            assert pipelines[0] == DATA_PIPELINE

    async def test_update_data_pipeline(self, service: MockDataPipelines):
        async with ChannelFor([service]) as channel:
            client = DataClient(channel, DATA_SERVICE_METADATA)
            await client.update_data_pipeline(ID, ORG_ID, NAME, SCHEDULE, MQL_BINARY, ENABLE_BACKFILL, DATA_SOURCE_TYPE)
            assert service.name == NAME
            assert service.org_id == ORG_ID
            assert service.schedule == SCHEDULE
            assert service.mql_binary == MQL_BINARY
            assert service.enable_backfill == ENABLE_BACKFILL
            assert service.data_source_type == DATA_SOURCE_TYPE

    async def test_get_mql_query_response(self, service: MockDataPipelines):
        async with ChannelFor([service]) as channel:
            client = DataClient(channel, DATA_SERVICE_METADATA)
            query = MQLQuery(query="test query")
            response = await client.get_mql_query_response(ORG_ID, query)
            assert response.rows[0].values == ["test", 1, True]

    async def test_get_log_schema(self, service: MockDataPipelines):
        async with ChannelFor([service]) as channel:
            client = DataClient(channel, DATA_SERVICE_METADATA)
            schema = await client.get_log_schema(ORG_ID)
            assert schema.fields[0].name == "test"
            assert schema.fields[0].type == LogSchemaFieldType.LOG_SCHEMA_FIELD_TYPE_STRING


if __name__ == "__main__":
    unittest.main()
