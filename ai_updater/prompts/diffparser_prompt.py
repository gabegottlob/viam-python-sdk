"""Prompt for analyzing proto changes and identifying required implementations."""

DIFF_PARSER_PROMPT = '''
You are an expert in analyzing protobuf definitions and determining required implementations in a Viam robotics SDK. The Viam SDK is a comprehensive framework for building and managing robotic systems, with the following rough architecture:

Here is a rough outline of the SDK as well as full included files so you can understand its architecture and functionality:
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
   Full files from this directory for context and structure:
   {root_context}

2. Components (src/viam/components/):
   - Core building blocks of robotic systems (motors, cameras, arms, etc.)
   - Each component has a standard interface defined in proto files
   - Implemented across three layers:
     * Abstract base classes (component.py)
     * Client implementations (client.py)
     * Service implementations (service.py)
   Full files from this subdirectory for context and structure:
   {components_context}

3. Proto (src/viam/proto/):
   - Contains Protocol Buffer definitions
   - Defines service interfaces and message types
   - Used for RPC communication between clients and services
   - Includes both component-specific and common message types
   These files are automatically generated and should not be modified manually, so you should not need to reference them for context, although they may choose to be included:
   {proto_context}

4. Gen (src/viam/gen/):
   - Contains auto-generated Python code from the proto files
   - Provides Python classes, services, and message types for use throughout the SDK
   - These files are included as context to help you understand the available classes and methods, but you should NOT edit or suggest changes to them, as they will be regenerated automatically from the proto definitions.
   Full files from this subdirectory for context and structure:
   {gen_context}

5. Resource (src/viam/resource/):
   - Manages the fundamental units of the SDK
   - Handles resource discovery, configuration, and lifecycle
   - Provides base classes for all SDK resources
   - Manages resource dependencies and relationships
   Full files from this subdirectory for context and structure:
   {resource_context}

6. Robot (src/viam/robot/):
   - Core robot management functionality
   - Handles robot configuration and setup
   - Manages resource discovery and registration
   - Provides robot client and service implementations
   Full files from this subdirectory for context and structure:
   {robot_context}

7. RPC (src/viam/rpc/):
   - Implements the RPC communication layer
   - Handles both streaming and unary RPCs
   - Manages authentication and metadata
   - Provides utilities for RPC communication
   Full files from this subdirectory for context and structure:
   {rpc_context}

8. Services (src/viam/services/):
   - Higher-level services built on top of components
   - Includes services like motion planning, navigation
   - Provides service-specific clients and implementations
   - Handles complex operations across multiple components
   Full files from this subdirectory for context and structure:
   {services_context}

9. Module (src/viam/module/):
   - Supports modular, reusable robot configurations
   - Enables custom component implementations
   - Handles module packaging and distribution
   - Manages module dependencies and versioning
   Full files from this subdirectory for context and structure:
   {module_context}

10. Media (src/viam/media/):
   - Handles media-related functionality
   - Manages image and video processing
   - Provides utilities for media streaming
   - Handles media format conversions
   Full files from this subdirectory for context and structure:
   {media_context}

11. App (src/viam/app/):
    - Application-level functionality
    - Handles app configuration and setup
    - Provides utilities for app development
    - Manages app-specific resources
    Full files from this subdirectory for context and structure:
    {app_context}

Your task is to analyze the changes in proto definitions and identify which new methods or other changes need to be implemented across the SDK files.
Here are the changes to the proto files (provided as a git diff):
{zsh_diff_output}

Based on these changes and your understanding of the codebase, output the paths of the files that need to be updated (you will never
need to create entirely new files), and what needs to be implemented within that file. These instructions will then be passed to another
Gemini LLM which will implement the changes, so make your instructions as relevant and detailed as necessary for another Gemini LLM to interpret. Include
as much detail as is necessary so that the other LLM can implement the changes when given the original files and the instructions.

IMPORTANT: THE ORIGINAL FUNCTIONALITY OF THE SDK MUST REMAIN EXACTLY INTACT. THESE CHANGES WILL BE DIRECTLY REINSERTED INTO THE CODEBASE.
ONLY INCLUDE IMPLEMENTATION DETAILS IN YOUR RESPONSE THAT ARE ABSOLUTELY NECESSARY. DO NOT INCLUDE EXTRANEOUS FILES/CHANGES IN YOUR RESPONSE.
'''
