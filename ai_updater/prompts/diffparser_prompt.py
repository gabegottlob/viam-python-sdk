"""Prompt for analyzing proto changes and identifying required implementations."""

DIFF_PARSER_PROMPT = '''
Your task is to analyze the changes in proto definitions and identify which methods need to be implemented across the component files.
Here are the changes to the proto files (provided as a git diff):
{zsh_diff_output}

For each changed/added RPC endpoint:
1. Identify the component type (e.g., Gripper, Arm, Camera etc.)
2. List which files need added implementations:
   - Abstract method in <component>.py
   - Client implementation in client.py
   - Service implementation in service.py
   - Necessary imports in __init__.py
3. Note the request/response message types and any special data types (e.g., bytes, enums)

In your response provide the following:

=== FILES_TO_UPDATE ===
- src/viam/components/<component>/<component>.py
- src/viam/components/<component>/client.py
- src/viam/components/<component>/service.py
- src/viam/components/<component>/__init__.py

=== IMPLEMENTATION_DETAILS ===
COMPONENT: <component_name>
NEW METHOD: <method_name>
FILES NEEDING IMPLEMENTATION:
- <file_path>: Abstract method
- <file_path>: Client implementation
- <file_path>: Service implementation
- <file_path>: Export in __init__.py
REQUEST TYPE: <request_message_type>
RESPONSE TYPE: <response_message_type>
SPECIAL TYPES: <list any special data types or enums used>

Here are examples of responses corresponding to existing implementations to help identify patterns:

Example 1 - Simple boolean response (Gripper):
=== FILES_TO_UPDATE ===
- src/viam/components/gripper/gripper.py
- src/viam/components/gripper/client.py
- src/viam/components/gripper/service.py
- src/viam/components/gripper/__init__.py

=== IMPLEMENTATION_DETAILS ===
COMPONENT: Gripper
NEW METHOD: Grab
FILES NEEDING IMPLEMENTATION:
- src/viam/components/gripper/gripper.py: Abstract method
- src/viam/components/gripper/client.py: Client implementation
- src/viam/components/gripper/service.py: Service implementation
- src/viam/components/gripper/__init__.py: Relevant imports
REQUEST TYPE: component.gripper.v1.gripper_pb2.GrabRequest
RESPONSE TYPE: component.gripper.v1.gripper_pb2.GrabResponse
SPECIAL TYPES: bool (success field)

Example 2 - Numeric parameter (Motor):
=== FILES_TO_UPDATE ===
- src/viam/components/motor/motor.py
- src/viam/components/motor/client.py
- src/viam/components/motor/service.py
- src/viam/components/motor/__init__.py

=== IMPLEMENTATION_DETAILS ===
COMPONENT: Motor
NEW METHOD: SetPower
FILES NEEDING IMPLEMENTATION:
- src/viam/components/motor/motor.py: Abstract method
- src/viam/components/motor/client.py: Client implementation
- src/viam/components/motor/service.py: Service implementation
- src/viam/components/motor/__init__.py: Relevant imports
REQUEST TYPE: component.motor.v1.motor_pb2.SetPowerRequest
RESPONSE TYPE: component.motor.v1.motor_pb2.SetPowerResponse
SPECIAL TYPES: float64 (power_pct field)

Example 3 - Complex return type (Camera):
=== FILES_TO_UPDATE ===
- src/viam/components/camera/camera.py
- src/viam/components/camera/client.py
- src/viam/components/camera/service.py
- src/viam/components/camera/__init__.py

=== IMPLEMENTATION_DETAILS ===
COMPONENT: Camera
NEW METHOD: GetPointCloud
FILES NEEDING IMPLEMENTATION:
- src/viam/components/camera/camera.py: Abstract method
- src/viam/components/camera/client.py: Client implementation
- src/viam/components/camera/service.py: Service implementation
- src/viam/components/camera/__init__.py: Relevant imports
REQUEST TYPE: component.camera.v1.camera_pb2.GetPointCloudRequest
RESPONSE TYPE: component.camera.v1.camera_pb2.GetPointCloudResponse
SPECIAL TYPES: bytes (point_cloud field), string (mime_type field)

Example 4 - Multiple return values (Arm):
=== FILES_TO_UPDATE ===
- src/viam/components/arm/arm.py
- src/viam/components/arm/client.py
- src/viam/components/arm/service.py
- src/viam/components/arm/__init__.py

=== IMPLEMENTATION_DETAILS ===
COMPONENT: Arm
NEW METHOD: GetJointPositions
FILES NEEDING IMPLEMENTATION:
- src/viam/components/arm/arm.py: Abstract method
- src/viam/components/arm/client.py: Client implementation
- src/viam/components/arm/service.py: Service implementation
- src/viam/components/arm/__init__.py: Relevant imports
REQUEST TYPE: component.arm.v1.arm_pb2.GetJointPositionsRequest
RESPONSE TYPE: component.arm.v1.arm_pb2.GetJointPositionsResponse
SPECIAL TYPES: JointPositions (positions field)
'''
