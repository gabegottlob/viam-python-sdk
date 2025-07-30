from typing import Sequence, Optional
from viam.proto.app.data import (
    DataPipeline,
    DataPipelineRun,
    CreateDataPipelineRequest,
    CreateDataPipelineResponse,
    TabularDataSourceType,
)
from viam.services.data import DataPipelinesServiceBase
from grpclib.server import Stream


class MockDataPipelines(DataPipelinesServiceBase):
    def __init__(self, create_response: str, list_response: Sequence[DataPipeline], runs_response: Sequence[DataPipelineRun]):
        self.create_response = create_response
        self.list_response = list_response
        self.runs_response = runs_response
        self.enable_backfill: Optional[bool] = None
        self.data_source_type: Optional[TabularDataSourceType.ValueType] = None

    async def CreateDataPipeline(self, stream: Stream[CreateDataPipelineRequest, CreateDataPipelineResponse]) -> None:
        request = await stream.recv_message()
        assert request is not None
        self.name = request.name
        self.mql_binary = request.mql_binary
        self.schedule = request.schedule
        self.org_id = request.organization_id
        self.enable_backfill = request.enable_backfill if request.HasField("enable_backfill") else None
        self.data_source_type = request.data_source_type if request.HasField("data_source_type") else None
        await stream.send_message(CreateDataPipelineResponse(id=self.create_response))

    async def ListDataPipelines(self, stream: Stream[object, Sequence[DataPipeline]]) -> None:
        request = await stream.recv_message()
        assert request is not None
        await stream.send_message(self.list_response)

    async def DeleteDataPipeline(self, stream: Stream[object, object]) -> None:
        request = await stream.recv_message()
        assert request is not None
        await stream.send_message(None)

    async def ListDataPipelineRuns(self, stream: Stream[object, Sequence[DataPipelineRun]]) -> None:
        request = await stream.recv_message()
        assert request is not None
        await stream.send_message(self.runs_response)

    async def DeleteDataPipelineRun(self, stream: Stream[object, object]) -> None:
        request = await stream.recv_message()
        assert request is not None
        await stream.send_message(None)

    async def UpdateDataPipeline(self, stream: Stream[object, object]) -> None:
        request = await stream.recv_message()
        assert request is not None
        await stream.send_message(None)
