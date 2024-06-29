from abc import ABCMeta as _ABCMeta, abstractmethod as _abstractmethod

from leads.logger import L
from .._computational import ndarray as _ndarray


class JarvisBackend(object, metaclass=_ABCMeta):
    @_abstractmethod
    def predict(self, x: _ndarray, visual: _ndarray) -> tuple[float, float, float]:
        """
        :param x: the input data
        :param visual: the visual data
        :return: [throttle, brake, steer]
        """
        raise NotImplementedError


class Jarvis(object):
    def __init__(self, backend: JarvisBackend) -> None:
        self.backend: JarvisBackend = backend
        L.info("Jarvis is enabled\n"
               "Before proceeding, you must read the following Terms and Conditions carefully:\n"
               "Jarvis is a deep learning model that aims to provide the optimal operation based on limited inputs.\n"
               "The user must be aware of the limitations of Jarvis and always drive with caution.\n"
               "The user must pay attention to the road at all times and follow the actual situation.\n"
               "The user must not blindly trust the instructions given by Jarvis.\n"
               "Local laws and regulations unconditionally take precedence over instructions given by Jarvis.\n"
               "Any personal injury caused by erroneous instructions shall be borne by the user.")
