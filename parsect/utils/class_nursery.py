from parsect.utils.exceptions import ClassInNurseryError
import torch


class ClassNursery:
    class_nursery = {"Adam": torch.optim.Adam, "SGD": torch.optim.SGD}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.class_nursery.get(cls.__name__) is None:
            cls.class_nursery[cls.__name__] = cls.__module__
        else:
            raise ClassInNurseryError(
                f"Class {cls.__name__} present in Nursery."
                f"Please chose another class name"
            )
