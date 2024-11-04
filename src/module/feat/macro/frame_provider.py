import abc


class FrameProvider(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_frame(self):
        return NotImplemented


