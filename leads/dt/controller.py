from typing import override as _override, overload as _overload

from leads.dt.device import Device


class Controller(Device):
    @_overload
    def __init__(self, *args, **kwargs) -> None:  # real signature unknown
        ...

    def __init__(self) -> None:
        super().__init__()
        self._devices: dict[str, Device] = {}

    def level(self) -> int:
        return len(self._parent_tags)

    def _attach_device(self, tag: str, device: Device) -> None:
        self._devices[tag] = device
        device.tag(tag)

    def devices(self) -> list[Device]:
        """
        :return: the device list
        """
        return list(self._devices.values())

    def device(self, tag: str, device: Device | None = None) -> Device | None:
        """
        Set or get a device by tag. The device's tag will be overwritten.
        ```python
        device(a_tag, a_device) # set a device
        device(a_tag) # get the device
        ```
        :param tag: tag of the device (it shares the global namespace)
        :param device: the device or None if getter mode
        :return: the device or None if setter mode
        """
        if device is None:
            return self._devices[tag]
        self._attach_device(tag, device)

    @_override
    def initialize(self, *parent_tags: str) -> None:
        for device in self._devices.values():
            device.initialize(*self._parent_tags, self._tag)
