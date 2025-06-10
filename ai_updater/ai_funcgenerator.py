import os
from google import genai
from google.genai import types

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

prompt = """You are an expert Python developer implementing components for the Viam robotics SDK. You need to implement a new GetKinematics method across three files for the Gripper component. Here is the relevant context:

1. Proto Definition:
The GetKinematics RPC is defined with endpoint: '/viam/api/v1/component/gripper/{name}/kinematics'
It uses common.v1.common_pb2.GetKinematicsRequest and GetKinematicsResponse messages.
The response contains a format field (KinematicsFileFormat enum) and kinematics_data field (bytes).

2. Example Implementation Pattern 1 - GetEndPosition from Arm Component:
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

3. Example Implementation Pattern 2 - GetPointCloud from Camera Component:
Shows handling of multiple return values and byte data:

Abstract Method:
@abc.abstractmethod
async def get_point_cloud(
    self, *, extra: Optional[Dict[str, Any]] = None, timeout: Optional[float] = None, **kwargs
) -> Tuple[bytes, str]:
    \"\"\"
    Get the point cloud data from a camera.
    Returns:
        Tuple[bytes, str]: A tuple containing two values; the first [0] the pointcloud data,
        and the second [1] the mimetype of the pointcloud (for example, PCD).
    \"\"\"
    ...

Mock Implementation:
async def get_point_cloud(
    self, *, extra: Optional[Dict[str, Any]] = None, timeout: Optional[float] = None, **kwargs
) -> Tuple[bytes, str]:
    self.extra = extra
    self.timeout = timeout
    return self.point_cloud, CameraMimeType.PCD

Service Implementation:
async def GetPointCloud(self, stream: Stream[GetPointCloudRequest, GetPointCloudResponse]) -> None:
    request = await stream.recv_message()
    assert request is not None
    camera = self.get_resource(request.name)
    timeout = stream.deadline.time_remaining() if stream.deadline else None
    pointcloud_data, mime_type = await camera.get_point_cloud(extra=struct_to_dict(request.extra), timeout=timeout)
    response = GetPointCloudResponse(pointCloud=pointcloud_data, mimeType=mime_type)
    await stream.send_message(response)(
    self, *, extra: Optional[Dict[str, Any]] = None, timeout: Optional[float] = None, **kwargs
) -> Tuple[KinematicsFileFormat.ValueType, bytes]:
    md = kwargs.get("metadata", self.Metadata()).proto
    request = GetKinematicsRequest(name=self.name, extra=dict_to_struct(extra))
    response: GetKinematicsResponse = await self.client.GetKinematics(request, timeout=timeout, metadata=md)
    return (response.format, response.kinematics_data)

Service Implementation:
async def GetKinematics(self, stream: Stream[GetKinematicsRequest, GetKinematicsResponse]) -> None:
    request = await stream.recv_message()
    assert request is not None
    arm = self.get_resource(request.name)
    timeout = stream.deadline.time_remaining() if stream.deadline else None
    format, kinematics_data = await arm.get_kinematics(extra=struct_to_dict(request.extra), timeout=timeout)
    response = GetKinematicsResponse(format=format, kinematics_data=kinematics_data)
    await stream.send_message(response)

Task:
Generate the GetKinematics implementations for the Gripper component across these three files:
1. Abstract method in gripper.py - Follow the docstring pattern showing examples
2. Client implementation in client.py - Include proper metadata and error handling
3. Service implementation in service.py - Follow the standard request validation pattern

The implementations should:
- Follow the same patterns and conventions as the example components
- Include proper type hints and docstrings (the docustrings do not need to be exhaustive, just follow the pattern. Additionally only the abstract method needs a docstring)
- Handle timeout and extra parameters consistently
- Follow error handling patterns
- Use appropriate assertions and validation
"""

# response = client.models.generate_content(
#     model="gemini-2.5-flash-preview-05-20",
#     contents=prompt
# )

# print("Generated Implementations:\n")
# print(response.text)

total_tokens = client.models.count_tokens(
    model="gemini-2.5-flash-preview-05-20",
    contents=prompt
)
print(f"Total tokens used: {total_tokens}")
