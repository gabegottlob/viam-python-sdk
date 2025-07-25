from io import IOBase
from typing import Any, Dict, List, Optional, Union

from grpclib.client import Channel
from viam.proto.app.data import (DataServiceStub, DeleteBinaryDataByFilterRequest, DeleteBinaryDataByIDsRequest,
                                  DeleteTabularDataByFilterRequest, DeleteTabularDataByIDsRequest,
                                  Filter, Order, TabularDataByFilterRequest, TabularDataByIDsRequest,
                                  UploadFileRequest, UploadMetadata)
from viam.proto.app.datasync import DataSyncServiceStub, UploadFileDataRequest
from viam.rpc.dial import DialOptions, _do_with_channel


class DataClient:
    """gRPC client for the Data Service."""

    def __init__(self, channel: Channel):
        self._channel = channel
        self._data_client = DataServiceStub(channel)
        self._data_sync_client = DataSyncServiceStub(channel)

    @classmethod
    async def from_dial_options(cls, dial_options: DialOptions):
        """Create a DataClient from dial options.

        Args:
            dial_options (DialOptions): The dial options to use.

        Returns:
            DataClient: The DataClient.
        """
        channel = await _do_with_channel(dial_options)
        return cls(channel)

    async def binary_data_capture_upload(
        self,
        component_name: str,
        type: str,
        method_name: str,
        data: bytes,
        tags: Optional[List[str]] = None,
        dataset_ids: Optional[List[str]] = None,
    ):
        """Upload binary data to the cloud.

        Args:
            component_name (str): Name of the component that captured the data.
            type (str): Type of the component that captured the data.
            method_name (str): Name of the method that captured the data.
            data (bytes): The binary data to upload.
            tags (Optional[List[str]]): Optional list of tags to allow for tag-based data filtering when retrieving data.
            dataset_ids (Optional[List[str]]): Optional list of dataset IDs to associate with the uploaded data.
        """
        metadata = UploadMetadata(
            component_name=component_name, type=type, method_name=method_name, tags=tags, dataset_ids=dataset_ids
        )
        request = UploadFileDataRequest(metadata=metadata, binary_data=data)
        await self._data_sync_client.UploadFileData(request)

    async def tabular_data_capture_upload(
        self,
        component_name: str,
        type: str,
        method_name: str,
        data: Dict[str, Any],
        tags: Optional[List[str]] = None,
        dataset_ids: Optional[List[str]] = None,
    ):
        """Upload tabular data to the cloud.

        Args:
            component_name (str): Name of the component that captured the data.
            type (str): Type of the component that captured the data.
            method_name (str): Name of the method that captured the data.
            data (Dict[str, Any]): The tabular data to upload.
            tags (Optional[List[str]]): Optional list of tags to allow for tag-based data filtering when retrieving data.
            dataset_ids (Optional[List[str]]): Optional list of dataset IDs to associate with the uploaded data.
        """
        metadata = UploadMetadata(
            component_name=component_name, type=type, method_name=method_name, tags=tags, dataset_ids=dataset_ids
        )
        request = UploadFileDataRequest(metadata=metadata, json_data=data)
        await self._data_sync_client.UploadFileData(request)

    async def streaming_data_capture_upload(
        self,
        component_name: str,
        type: str,
        method_name: str,
        data: bytes,
        tags: Optional[List[str]] = None,
        dataset_ids: Optional[List[str]] = None,
    ):
        """Upload streaming data to the cloud.

        Args:
            component_name (str): Name of the component that captured the data.
            type (str): Type of the component that captured the data.
            method_name (str): Name of the method that captured the data.
            data (bytes): The streaming data to upload.
            tags (Optional[List[str]]): Optional list of tags to allow for tag-based filtering when retrieving data.
            dataset_ids (Optional[List[str]]): Optional list of dataset IDs to associate with the uploaded data.
        """
        metadata = UploadMetadata(
            component_name=component_name, type=type, method_name=method_name, tags=tags, dataset_ids=dataset_ids
        )
        request = UploadFileDataRequest(metadata=metadata, binary_data=data)
        await self._data_sync_client.UploadFileData(request)

    async def file_upload(
        self,
        name: str,
        data: Union[IOBase, bytes],
        tags: Optional[List[str]] = None,
        dataset_ids: Optional[List[str]] = None,
    ):
        """Upload a file to the cloud.

        Args:
            name (str): Name of the file.
            data (Union[IOBase, bytes]): The file to upload.
            tags (Optional[List[str]]): Optional list of tags to allow for tag-based filtering when retrieving data.
            dataset_ids (Optional[List[str]]): Optional list of dataset IDs to associate with the uploaded data.
        """
        metadata = UploadMetadata(file_name=name, tags=tags, dataset_ids=dataset_ids)
        if isinstance(data, IOBase):
            data = data.read()
        request = UploadFileRequest(metadata=metadata, file_contents=data)
        await self._data_client.UploadFile(request)

    async def file_upload_from_path(
        self,
        path: str,
        tags: Optional[List[str]] = None,
        dataset_ids: Optional[List[str]] = None,
    ):
        """Upload a file to the cloud from a path.

        Args:
            path (str): Path to the file.
            tags (Optional[List[str]]): Optional list of tags to allow for tag-based filtering when retrieving data.
            dataset_ids (Optional[List[str]]): Optional list of dataset IDs to associate with the uploaded data.
        """
        with open(path, "rb") as f:
            data = f.read()
        name = path.split("/")[-1]
        metadata = UploadMetadata(file_name=name, tags=tags, dataset_ids=dataset_ids)
        request = UploadFileRequest(metadata=metadata, file_contents=data)
        await self._data_client.UploadFile(request)

    async def delete_binary_data_by_filter(self, filter: Filter):
        """Delete binary data by filter.

        Args:
            filter (Filter): Filter to delete data by.
        """
        request = DeleteBinaryDataByFilterRequest(filter=filter)
        await self._data_client.DeleteBinaryDataByFilter(request)

    async def delete_binary_data_by_ids(self, ids: List[str]):
        """Delete binary data by IDs.

        Args:
            ids (List[str]): IDs of the data to delete.
        """
        request = DeleteBinaryDataByIDsRequest(ids=ids)
        await self._data_client.DeleteBinaryDataByIDs(request)

    async def delete_tabular_data_by_filter(self, filter: Filter):
        """Delete tabular data by filter.

        Args:
            filter (Filter): Filter to delete data by.
        """
        request = DeleteTabularDataByFilterRequest(filter=filter)
        await self._data_client.DeleteTabularDataByFilter(request)

    async def delete_tabular_data_by_ids(self, ids: List[str]):
        """Delete tabular data by IDs.

        Args:
            ids (List[str]): IDs of the data to delete.
        """
        request = DeleteTabularDataByIDsRequest(ids=ids)
        await self._data_client.DeleteTabularDataByIDs(request)

    async def tabular_data_by_filter(self, filter: Filter, order: Optional[Order] = None, page_size: Optional[int] = None, page_token: Optional[str] = None):
        """Get tabular data by filter.

        Args:
            filter (Filter): Filter to get data by.
            order (Optional[Order]): Order to sort data by.
            page_size (Optional[int]): Number of items to return per page.
            page_token (Optional[str]): Token to retrieve the next page of results.

        Returns:
            TabularDataByFilterResponse: The tabular data.
        """
        request = TabularDataByFilterRequest(filter=filter, order=order, page_size=page_size, page_token=page_token)
        response = await self._data_client.TabularDataByFilter(request)
        return response

    async def tabular_data_by_ids(self, ids: List[str]):
        """Get tabular data by IDs.

        Args:
            ids (List[str]): IDs of the data to get.

        Returns:
            TabularDataByIDsResponse: The tabular data.
        """
        request = TabularDataByIDsRequest(ids=ids)
        response = await self._data_client.TabularDataByIDs(request)
        return response
