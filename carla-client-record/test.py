from abc import ABC, abstractclassmethod
from settings.globals import lanes

class Parent(ABC):
    def __init__(self, args, lanes):
        self.lanes = lanes
        lanes.append("test-parent")
        print("Parents init", self.args, self.lanes)
    
    @abstractclassmethod
    def test(self) -> None:
        print("This should not be visible")