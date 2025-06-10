import os
from google import genai
from google.genai import types

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

zsh_diff_output = os.getenv("ZSH_DIFF_OUTPUT")

#print(f"Diff output recieved from zsh script: {zsh_diff_output}")

prompt_one = f"""You are an expert in analyzing protobuf definitions and determining required implementations in a Viam robotics SDK. Your task is to analyze the changes in proto definitions and identify which methods need to be implemented across the component files.

Here is the diff from the proto files:
{zsh_diff_output}

For each changed/added RPC endpoint:
1. Identify the component type (e.g., Gripper, Arm, Camera etc.)
2. List which files need implementations:
   - Abstract method in <component>.py
   - Client implementation in client.py
   - Service implementation in service.py
3. Note the request/response message types and any special data types (e.g., bytes, enums)

Format your response as:

COMPONENT: <component_name>
NEW METHOD: <method_name>
FILES NEEDING IMPLEMENTATION:
- <file_path>: Abstract method
- <file_path>: Client implementation
- <file_path>: Service implementation
REQUEST TYPE: <request_message_type>
RESPONSE TYPE: <response_message_type>
SPECIAL TYPES: <list any special data types or enums used>

This output will be used to generate the actual implementations, so be precise about the types and paths.

Example outputs:

1. Simple boolean response example:
COMPONENT: Gripper
NEW METHOD: Grab
FILES NEEDING IMPLEMENTATION:
- src/viam/components/gripper/gripper.py: Abstract method
- src/viam/components/gripper/client.py: Client implementation
- src/viam/components/gripper/service.py: Service implementation
REQUEST TYPE: component.gripper.v1.gripper_pb2.GrabRequest
RESPONSE TYPE: component.gripper.v1.gripper_pb2.GrabResponse
SPECIAL TYPES: bool (success field)

2. Numeric parameter example:
COMPONENT: Motor
NEW METHOD: SetPower
FILES NEEDING IMPLEMENTATION:
- src/viam/components/motor/motor.py: Abstract method
- src/viam/components/motor/client.py: Client implementation
- src/viam/components/motor/service.py: Service implementation
REQUEST TYPE: component.motor.v1.motor_pb2.SetPowerRequest
RESPONSE TYPE: component.motor.v1.motor_pb2.SetPowerResponse
SPECIAL TYPES: float64 (power_pct field)
"""

p1_tokens = client.models.count_tokens(
    model="gemini-2.5-flash-preview-05-20",
    contents=prompt_one
)
print(f"Input tokens from first prompt: {p1_tokens}")

response_one = client.models.generate_content(
    model="gemini-2.5-flash-preview-05-20",
    contents= prompt_one
)

with open("diffparsertest.txt", 'w') as f:
    f.write(response_one.text)

prompt_two = f"""You are an expert Python developer implementing components for the Viam robotics SDK. You need to implement the following new method(s):

{response_one.text}

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

Task Review:
Generate the implementations of the method(s) specified at the start of the prompt:
1. Abstract method in {{component}}.py - Follow the docstring pattern showing examples
2. Client implementation in client.py - Include proper metadata and error handling
3. Service implementation in service.py - Follow the standard request validation pattern

The implementations should:
- Follow the same patterns and conventions as the example components
- Include proper type hints and docstrings (the docustrings do not need to be exhaustive, just follow the pattern. Additionally only the abstract method needs a docstring)
- Handle timeout and extra parameters consistently
- Follow error handling patterns
- Use appropriate assertions and validation
"""

p2_tokens = client.models.count_tokens(
    model="gemini-2.5-flash-preview-05-20",
    contents=prompt_two
)
print(f"Input tokens from second prompt: {p2_tokens}")

response_two = client.models.generate_content(
    model="gemini-2.5-flash-preview-05-20",
    contents= prompt_two
)

with open("funcgeneratortest.txt", 'w') as f:
    f.write(response_two.text)
