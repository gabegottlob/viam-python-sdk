"""Prompt for generating function implementations."""

FUNCTION_GENERATOR_P1 = '''
You are an expert Python developer implementing components for the Viam robotics SDK. You need to implement the following new method(s):

{implementation_details}

Here are some examples of already existing methods from within the codebase to provide you with relevant context:

EXAMPLE IMPLEMENTATION PATTERN 1 - GetEndPosition from Arm Component:
Shows basic request/response pattern with proper error handling:

Example Implementation:
async def get_end_position(self, *, extra: Optional[Dict[str, Any]] = None, timeout: Optional[float] = None, **kwargs) -> Pose:
    md = kwargs.get("metadata", self.Metadata()).proto
    request = GetEndPositionRequest(name=self.name, extra=dict_to_struct(extra))
    response: GetEndPositionResponse = await self.client.GetEndPosition(request, timeout=timeout, metadata=md)
    return response.pose

Service Implementation:
async def GetEndPosition(self, stream: Stream[GetEndPositionRequest, GetEndPositionResponse]) -> None:
    request = await stream.recv_message()
    assert request is not None
    name = request.name
    arm = self.get_resource(name)
    timeout = stream.deadline.time_remaining() if stream.deadline else None
    position = await arm.get_end_position(extra=struct_to_dict(request.extra), timeout=timeout, metadata=stream.metadata)
    response = GetEndPositionResponse(pose=position)
    await stream.send_message(response)

EXAMPLE IMPLEMENTATION PATTERN 2 - GetPointCloud from Camera Component:
Shows handling of multiple return values and byte data:

Abstract Method:
async def get_point_cloud(self, *, extra: Optional[Dict[str, Any]] = None, timeout: Optional[float] = None, **kwargs) -> Tuple[bytes, str]:
    \"\"\"
    Get the next point cloud from the camera. This will be
    returned as bytes with a mimetype describing
    the structure of the data. The consumer of this call
    should encode the bytes into the formatted suggested
    by the mimetype.

    To deserialize the returned information into a numpy array, use the Open3D library.

    ::

        import numpy as np
        import open3d as o3d

        my_camera = Camera.from_robot(robot=machine, name="my_camera")

        data, _ = await my_camera.get_point_cloud()

        # write the point cloud into a temporary file
        with open("/tmp/pointcloud_data.pcd", "wb") as f:
            f.write(data)
        pcd = o3d.io.read_point_cloud("/tmp/pointcloud_data.pcd")
        points = np.asarray(pcd.points)

    Returns:
        Tuple[bytes, str]: A tuple containing two values; the first [0] the pointcloud data,
        and the second [1] the mimetype of the pointcloud (for example, PCD).
    \"\"\"
    ...

Client Implementation:
async def get_point_cloud(self, *, extra: Optional[Dict[str, Any]] = None, timeout: Optional[float] = None, **kwargs) -> Tuple[bytes, str]:
    md = kwargs.get("metadata", self.Metadata()).proto
    request = GetPointCloudRequest(name=self.name, mime_type=CameraMimeType.PCD, extra=dict_to_struct(extra))
    response: GetPointCloudResponse = await self.client.GetPointCloud(request, timeout=timeout, metadata=md)
    return (response.point_cloud, response.mime_type)

Service Implementation:
async def GetPointCloud(self, stream: Stream[GetPointCloudRequest, GetPointCloudResponse]) -> None:
    request = await stream.recv_message()
    assert request is not None
    name = request.name
    camera = self.get_resource(name)
    timeout = stream.deadline.time_remaining() if stream.deadline else None
    pc, mimetype = await camera.get_point_cloud(timeout=timeout, extra=struct_to_dict(request.extra), metadata=stream.metadata)
    response = GetPointCloudResponse(mime_type=mimetype, point_cloud=pc)
    await stream.send_message(response)

I will now give you the existing files from the codebase that you need to add your new methods or edits to:
'''

FUNCTION_GENERATOR_P2 = '''
Task Review:
For each file that needs to be modified, regenerate the complete file contents for all required files.
WHEN REGENERATING THE FILES, ONLY ADD YOUR NEWLY CREATED METHODS OR NECESSARY EDITS. DO NOT MODIFY THE EXISTING FILES IN ANY UNNECESSARY WAYS.
THE FILES YOU ARE EDITING WILL BE REINSERTED INTO THE CODEBASE AND MUST MAINTAIN THEIR EXACT ORIGINAL FUNCTIONALITY. THIS IS VERY IMPORTANT.

For each file, provide that files filepath (so it can be reinserted into the existing codebase), as well as the newly generated contents.

Your output should:
- Follow the same patterns and conventions as the examples and original files
- Maintain all existing functionality while adding new methods
- Include all necessary imports in the relevant file
'''
