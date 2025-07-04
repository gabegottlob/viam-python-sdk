from typing import Any, Dict, List, Mapping, Optional, Tuple

from grpclib.client import Channel

from viam.proto.common import DoCommandRequest, DoCommandResponse, Geometry, GetKinematicsRequest, GetKinematicsResponse
from viam.proto.component.gripper import (
    GrabRequest,
    GrabResponse,
    GripperServiceStub,
    IsHoldingSomethingRequest,
    IsHoldingSomethingResponse,
    IsMovingRequest,
    IsMovingResponse,
    OpenRequest,
    StopRequest,
)
from viam.resource.rpc_client_base import ReconfigurableResourceRPCClientBase
from viam.utils import ValueTypes, dict_to_struct, get_geometries, struct_to_dict

from . import KinematicsFileFormat
from .gripper import Gripper


class GripperClient(Gripper, ReconfigurableResourceRPCClientBase):
    """
    gRPC client for the Gripper component
    """

    def __init__(self, name: str, channel: Channel):
        self.channel = channel
        self.client = GripperServiceStub(channel)
        super().__init__(name)

    async def open(
        self,
        *,
        extra: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        **kwargs,
    ):
        md = kwargs.get("metadata", self.Metadata()).proto
        request = OpenRequest(name=self.name, extra=dict_to_struct(extra))
        await self.client.Open(request, timeout=timeout, metadata=md)

    async def grab(
        self,
        *,
        extra: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        **kwargs,
    ) -> bool:
        md = kwargs.get("metadata", self.Metadata()).proto
        request = GrabRequest(name=self.name, extra=dict_to_struct(extra))
        response: GrabResponse = await self.client.Grab(request, timeout=timeout, metadata=md)
        return response.success

    async def stop(
        self,
        *,
        extra: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        **kwargs,
    ):
        md = kwargs.get("metadata", self.Metadata()).proto
        request = StopRequest(name=self.name, extra=dict_to_struct(extra))
        await self.client.Stop(request, timeout=timeout, metadata=md)

    async def is_holding_something(
        self, *, extra: Optional[Dict[str, Any]] = None, timeout: Optional[float] = None, **kwargs
    ) -> Gripper.HoldingStatus:
        md = kwargs.get("metadata", self.Metadata()).proto
        request = IsHoldingSomethingRequest(name=self.name, extra=dict_to_struct(extra))
        response: IsHoldingSomethingResponse = await self.client.IsHoldingSomething(request, timeout=timeout, metadata=md)
        return Gripper.HoldingStatus(response.is_holding_something, meta=struct_to_dict(response.meta))

    async def is_moving(self, *, timeout: Optional[float] = None, **kwargs) -> bool:
        md = kwargs.get("metadata", self.Metadata()).proto
        request = IsMovingRequest(name=self.name)
        response: IsMovingResponse = await self.client.IsMoving(request, timeout=timeout, metadata=md)
        return response.is_moving

    async def do_command(
        self,
        command: Mapping[str, ValueTypes],
        *,
        timeout: Optional[float] = None,
        **kwargs,
    ) -> Mapping[str, ValueTypes]:
        md = kwargs.get("metadata", self.Metadata()).proto
        request = DoCommandRequest(name=self.name, command=dict_to_struct(command))
        response: DoCommandResponse = await self.client.DoCommand(request, timeout=timeout, metadata=md)
        return struct_to_dict(response.result)

    async def get_geometries(self, *, extra: Optional[Dict[str, Any]] = None, timeout: Optional[float] = None, **kwargs) -> List[Geometry]:
        md = kwargs.get("metadata", self.Metadata())
        return await get_geometries(self.client, self.name, extra, timeout, md)

    async def get_kinematics(
        self,
        *,
        extra: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        **kwargs,
    ) -> Tuple[KinematicsFileFormat.ValueType, bytes]:
        md = kwargs.get("metadata", self.Metadata()).proto
        request = GetKinematicsRequest(name=self.name, extra=dict_to_struct(extra))
        response: GetKinematicsResponse = await self.client.GetKinematics(request, timeout=timeout, metadata=md)
        return (response.format, response.kinematics_data)
