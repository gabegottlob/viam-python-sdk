import abc
from logging import Logger
from typing import TYPE_CHECKING, Any, ClassVar, Dict, List, Mapping, Optional, SupportsBytes, SupportsFloat, Tuple, Union, cast

from typing_extensions import Self

from viam.errors import MethodNotImplementedError
from viam.logging import getLogger
from viam.proto.common import Geometry, KinematicsFileFormat
from viam.resource.base import ResourceBase

if TYPE_CHECKING:
    from viam.resource.types import API
    from viam.robot.client import RobotClient


ValueTypes = Union[bool, SupportsBytes, SupportsFloat, List, Mapping, str, None]


class ComponentBase(abc.ABC, ResourceBase):
    """
    Base component.
    All components must inherit from this class.
    """

    API: ClassVar["API"]

    def __init__(self, name: str, *, logger: Optional[Logger] = None):
        self.name = name
        self.logger = logger if logger is not None else getLogger(f"{self.API}.{name}")

    @classmethod
    def from_robot(cls, robot: "RobotClient", name: str) -> Self:
        """Get the component named ``name`` from the provided robot.

        Args:
            robot (RobotClient): The robot
            name (str): The name of the component

        Returns:
            Self: The component, if it exists on the robot
        """
        component = robot.get_component(cls.get_resource_name(name))
        return cast(cls, component)  # type: ignore

    async def do_command(self, command: Mapping[str, ValueTypes], *, timeout: Optional[float] = None, **kwargs) -> Mapping[str, ValueTypes]:
        raise NotImplementedError()

    async def get_geometries(self, *, extra: Optional[Dict[str, Any]] = None, timeout: Optional[float] = None) -> List[Geometry]:
        """
        Get all geometries associated with the component, in their current configuration, in the
        `frame <https://docs.viam.com/operate/mobility/define-geometry/>`__ of the component.

        ::

            geometries = await component.get_geometries()

            if geometries:
                # Get the center of the first geometry
                print(f"Pose of the first geometry's centerpoint: {geometries[0].center}")

        Returns:
            List[Geometry]: The geometries associated with the Component.
        """
        raise MethodNotImplementedError("get_geometries")

    @abc.abstractmethod
    async def get_kinematics(
        self,
        *,
        extra: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
        **kwargs,
    ) -> Tuple[KinematicsFileFormat.ValueType, bytes]:
        """
        Get the kinematics information associated with the component.

        ::

            my_component = MyComponent.from_robot(robot=machine, name="my_component")

            # Get the kinematics information associated with the component.
            kinematics = await my_component.get_kinematics()

            # Get the format of the kinematics file.
            k_file = kinematics[0]

            # Get the byte contents of the file.
            k_bytes = kinematics[1]

        Returns:
            Tuple[KinematicsFileFormat.ValueType, bytes]: A tuple containing two values; the first [0] value represents the format of the
            file, either in URDF format (``KinematicsFileFormat.KINEMATICS_FILE_FORMAT_URDF``) or
            Viam's kinematic parameter format (spatial vector algebra) (``KinematicsFileFormat.KINEMATICS_FILE_FORMAT_SVA``),
            and the second [1] value represents the byte contents of the file.
        """
        raise MethodNotImplementedError("get_kinematics")