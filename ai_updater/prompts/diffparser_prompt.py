"""Prompt for analyzing proto changes and identifying required implementations."""

DIFF_PARSER_P1 = '''
You are an expert in analyzing protobuf definitions and determining required implementations in a Viam robotics SDK.
The Viam SDK is a comprehensive framework for building and managing robotic systems.
You will first be provided with relevant context from the SDK to help you complete your task.

Here is a rough outline of the SDK to help you understand its architecture and functionality:
=== SDK ARCHITECTURE ===
1. Root Directory (src/viam/):
   - Core SDK functionality and utilities
   - Contains essential base files:
     * __init__.py: Package initialization and exports
     * errors.py: Error definitions and handling
     * logging.py: Logging configuration and utilities
     * operations.py: Core operation implementations
     * sessions_client.py: Session management
     * streams.py: Streaming functionality
     * utils.py: Common utility functions

2. Components (src/viam/components/):
   - Core building blocks of robotic systems (motors, cameras, arms, etc.)
   - Each component has a standard interface defined in proto files
   - Implemented across three layers:
     * Abstract base classes (component.py)
     * Client implementations (client.py)
     * Service implementations (service.py)

3. Proto (src/viam/proto/):
   - Contains Protocol Buffer definitions
   - Defines service interfaces and message types
   - Used for RPC communication between clients and services
   - Includes both component-specific and common message types

4. Gen (src/viam/gen/):
   - Contains auto-generated Python code from the proto files
   - Provides Python classes, services, and message types for use throughout the SDK
   - These files are included as context to help you understand the available classes and methods, but you should NOT edit or suggest changes to them, as they will be regenerated automatically from the proto definitions.

5. Resource (src/viam/resource/):
   - Manages the fundamental units of the SDK
   - Handles resource discovery, configuration, and lifecycle
   - Provides base classes for all SDK resources
   - Manages resource dependencies and relationships

6. Robot (src/viam/robot/):
   - Core robot management functionality
   - Handles robot configuration and setup
   - Manages resource discovery and registration
   - Provides robot client and service implementations

7. RPC (src/viam/rpc/):
   - Implements the RPC communication layer
   - Handles both streaming and unary RPCs
   - Manages authentication and metadata
   - Provides utilities for RPC communication

8. Services (src/viam/services/):
   - Higher-level services built on top of components
   - Includes services like motion planning, navigation
   - Provides service-specific clients and implementations
   - Handles complex operations across multiple components

9. Module (src/viam/module/):
   - Supports modular, reusable robot configurations
   - Enables custom component implementations
   - Handles module packaging and distribution
   - Manages module dependencies and versioning

10. Media (src/viam/media/):
   - Handles media-related functionality
   - Manages image and video processing
   - Provides utilities for media streaming
   - Handles media format conversions

11. App (src/viam/app/):
    - Application-level functionality
    - Handles app configuration and setup
    - Provides utilities for app development
    - Manages app-specific resources

12. Tests Directory (tests/):
   - Contains comprehensive test suite for the SDK

Here are the specific files from the SDK that are relevant to the changes being made or would be valuable context:
=== SELECTED CONTEXT FILES ===
{selected_context_files}

Your task is to analyze the changes in proto definitions and identify which new methods or other changes need to be implemented across the SDK files.
Here are the changes to the proto files (provided as a git diff):
{zsh_diff_output}

TASK OVERVIEW:
You are the second step in an AI pipeline that updates SDK code based on proto definition changes. Your specific role is to:

1. Analyze the proto changes in the git diff
2. Identify which files need to be modified to implement these changes
3. Provide detailed instructions for what needs to be implemented in each file

Based on these changes and your understanding of the codebase, output the paths of the files that need to be updated, and what needs to be implemented within that file.
These instructions will then be passed to another Gemini LLM which will implement the changes, so make your instructions as relevant and detailed as necessary
for another Gemini LLM to interpret. Include as much detail as is necessary so that the other LLM can implement the changes when given the original files and the instructions.

IMPORTANT: ALSO IDENTIFY ANY FILES WITHIN THE tests/ DIRECTORY THAT NEED TO BE UPDATED.
For each implementation file that needs changes, check if there are corresponding files that would need to be updated to test the new functionality.
Include these in your list of files to update alongisde the necessary changes.

IMPORTANT: THE ORIGINAL FUNCTIONALITY OF THE SDK MUST REMAIN EXACTLY INTACT. THESE CHANGES WILL BE DIRECTLY REINSERTED INTO THE CODEBASE.
ONLY INCLUDE IMPLEMENTATION DETAILS IN YOUR RESPONSE THAT ARE ABSOLUTELY NECESSARY. DO NOT INCLUDE EXTRANEOUS FILES/CHANGES IN YOUR RESPONSE.
'''
