from io import IOBase
from typing import List, Optional

from grpclib.client import Channel
from viam.proto.app.data import (DataServiceStub, UploadBinaryDataRequest, UploadFileRequest, UploadMetadata, UploadTabularDataRequest)
from viam.proto.app.datasync import DataSyncServiceStub, UploadStreamingDataRequest
from viam.utils import Value


class DataClient:
    """gRPC client for the Data Service."""

    def __init__(self, channel: Channel, app_id: str):
        self._client = DataServiceStub(channel)
        self._data_sync_client = DataSyncServiceStub(channel)
        self._app_id = app_id

    async def binary_data_capture_upload(
        self,
        component_name: str,
        type: str,
        binary: bytes,
        file_extension: str,
        organization_id: str,
        location_id: str,
        robot_id: str,
        part_id: str,
        capture_time: float,
        tags: Optional[List[str]] = None,
        sensor_name: Optional[str] = None,
        method_name: Optional[str] = None,
        method_parameters: Optional[Value] = None,
        dataset_ids: Optional[List[str]] = None,
    ):
        """Upload binary data to the cloud.

        Args:
            component_name (str): Name of the component
            type (str): Type of the component
            binary (bytes): Binary data
            file_extension (str): File extension of the binary data
            organization_id (str): Organization ID
            location_id (str): Location ID
            robot_id (str): Robot ID
            part_id (str): Part ID
            capture_time (float): Capture time of the data
            tags (Optional[List[str]]): Tags to associate with the data
            sensor_name (Optional[str]): Name of the sensor
            method_name (Optional[str]): Name of the method
            method_parameters (Optional[Value]): Method parameters
            dataset_ids (Optional[List[str]]): Optional list of dataset IDs to associate with the uploaded data.
        """
        metadata = UploadMetadata(
            component_name=component_name,
            type=type,
            organization_id=organization_id,
            location_id=location_id,
            robot_id=robot_id,
            part_id=part_id,
            capture_time=capture_time,
            tags=tags,
            sensor_name=sensor_name,
            method_name=method_name,
            method_parameters=method_parameters,
            dataset_ids=dataset_ids,
        )
        request = UploadBinaryDataRequest(binary=binary, file_extension=file_extension, metadata=metadata)
        await self._client.UploadBinaryData(request)

    async def tabular_data_capture_upload(
        self,
        component_name: str,
        type: str,
        data: Value,
        organization_id: str,
        location_id: str,
        robot_id: str,
        part_id: str,
        capture_time: float,
        tags: Optional[List[str]] = None,
        sensor_name: Optional[str] = None,
        method_name: Optional[str] = None,
        method_parameters: Optional[Value] = None,
        dataset_ids: Optional[List[str]] = None,
    ):
        """Upload tabular data to the cloud.

        Args:
            component_name (str): Name of the component
            type (str): Type of the component
            data (Value): Tabular data
            organization_id (str): Organization ID
            location_id (str): Location ID
            robot_id (str): Robot ID
            part_id (str): Part ID
            capture_time (float): Capture time of the data
            tags (Optional[List[str]]): Tags to associate with the data
            sensor_name (Optional[str]): Name of the sensor
            method_name (Optional[str]): Name of the method
            method_parameters (Optional[Value]): Method parameters
            dataset_ids (Optional[List[str]]): Optional list of dataset IDs to associate with the uploaded data.
        """
        metadata = UploadMetadata(
            component_name=component_name,
            type=type,
            organization_id=organization_id,
            location_id=location_id,
            robot_id=robot_id,
            part_id=part_id,
            capture_time=capture_time,
            tags=tags,
            sensor_name=sensor_name,
            method_name=method_name,
            method_parameters=method_parameters,
            dataset_ids=dataset_ids,
        )
        request = UploadTabularDataRequest(data=data, metadata=metadata)
        await self._client.UploadTabularData(request)

    async def streaming_data_capture_upload(
        self,
        component_name: str,
        type: str,
        data: bytes,
        organization_id: str,
        location_id: str,
        robot_id: str,
        part_id: str,
        capture_time: float,
        tags: Optional[List[str]] = None,
        sensor_name: Optional[str] = None,
        method_name: Optional[str] = None,
        method_parameters: Optional[Value] = None,
        dataset_ids: Optional[List[str]] = None,
    ):
        """Upload streaming data to the cloud.

        Args:
            component_name (str): Name of the component
            type (str): Type of the component
            data (bytes): Streaming data
            organization_id (str): Organization ID
            location_id (str): Location ID
            robot_id (str): Robot ID
            part_id (str): Part ID
            capture_time (float): Capture time of the data
            tags (Optional[List[str]]): Tags to associate with the data
            sensor_name (Optional[str]): Name of the sensor
            method_name (Optional[str]): Name of the method
            method_parameters (Optional[Value]): Method parameters
            dataset_ids (Optional[List[str]]): Optional list of dataset IDs to associate with the uploaded data.
        """
        metadata = UploadMetadata(
            component_name=component_name,
            type=type,
            organization_id=organization_id,
            location_id=location_id,
            robot_id=robot_id,
            part_id=part_id,
            capture_time=capture_time,
            tags=tags,
            sensor_name=sensor_name,
            method_name=method_name,
            method_parameters=method_parameters,
            dataset_ids=dataset_ids,
        )
        request = UploadStreamingDataRequest(data=data, metadata=metadata)
        await self._data_sync_client.UploadStreamingData(request)

    async def file_upload(
        self,
        file: IOBase,
        file_name: str,
        organization_id: str,
        location_id: str,
        robot_id: str,
        part_id: str,
        capture_time: float,
        tags: Optional[List[str]] = None,
        sensor_name: Optional[str] = None,
        method_name: Optional[str] = None,
        method_parameters: Optional[Value] = None,
        dataset_ids: Optional[List[str]] = None,
    ):
        """Upload a file to the cloud.

        Args:
            file (IOBase): File to upload
            file_name (str): Name of the file
            organization_id (str): Organization ID
            location_id (str): Location ID
            robot_id (str): Robot ID
            part_id (str): Part ID
            capture_time (float): Capture time of the data
            tags (Optional[List[str]]): Tags to associate with the data
            sensor_name (Optional[str]): Name of the sensor
            method_name (Optional[str]): Name of the method
            method_parameters (Optional[Value]): Method parameters
            dataset_ids (Optional[List[str]]): Optional list of dataset IDs to associate with the uploaded data.
        """
        metadata = UploadMetadata(
            organization_id=organization_id,
            location_id=location_id,
            robot_id=robot_id,
            part_id=part_id,
            capture_time=capture_time,
            tags=tags,
            sensor_name=sensor_name,
            method_name=method_name,
            method_parameters=method_parameters,
            dataset_ids=dataset_ids,
        )
        request = UploadFileRequest(file_name=file_name, upload_metadata=metadata)
        request.file_contents = file.read()
        await self._client.UploadFile(request)

    async def file_upload_from_path(
        self,
        file_path: str,
        organization_id: str,
        location_id: str,
        robot_id: str,
        part_id: str,
        capture_time: float,
        tags: Optional[List[str]] = None,
        sensor_name: Optional[str] = None,
        method_name: Optional[str] = None,
        method_parameters: Optional[Value] = None,
        dataset_ids: Optional[List[str]] = None,
    ):
        """Upload a file to the cloud from a path.

        Args:
            file_path (str): Path to the file
            organization_id (str): Organization ID
            location_id (str): Location ID
            robot_id (str): Robot ID
            part_id (str): Part ID
            capture_time (float): Capture time of the data
            tags (Optional[List[str]]): Tags to associate with the data
            sensor_name (Optional[str]): Name of the sensor
            method_name (Optional[str]): Name of the method
            method_parameters (Optional[Value]): Method parameters
            dataset_ids (Optional[List[str]]): Optional list of dataset IDs to associate with the uploaded data.
        """
        with open(file_path, "rb") as f:
            await self.file_upload(
                file=f,
                file_name=f.name,
                organization_id=organization_id,
                location_id=location_id,
                robot_id=robot_id,
                part_id=part_id,
                capture_time=capture_time,
                tags=tags,
                sensor_name=sensor_name,
                method_name=method_name,
                method_parameters=method_parameters,
                dataset_ids=dataset_ids,
            )
