from test import Parent

class Child1(Parent):
    def __init__(self, args, lanes):
        self.args = args
        self.lanes = lanes
        super().__init__(self.args, self.lanes)
        self.lanes.append("test-child1")
        print("Child2 init", self.args, self.lanes)
    
    def test(self):
        self.lanes.append("test-child1-test")
        print("Child1's test", self.args, self.lanes)

class Child2(Parent):
    def __init__(self, args, lanes):
        self.args = args
        self.lanes = lanes
        super().__init__(self.args, self.lanes)
        self.lanes.append("test-child2")
        print("Child2 init", self.args, self.lanes)
    
    def test(self):
        self.lanes.append("test-child2-test")
        print("Child2's test", self.args, self.lanes)

class Other():
    def __init__(self, lanes):
        self.lanes = lanes
        self.lanes.append("test-Other")
        print("Other init", self.lanes)

if __name__ == "__main__":
    lanes = []
    child1 = Child1("child1 args", lanes)
    child2 = Child2("child2 args", lanes)
    child1.test()
    child2.test()
    other = Other(lanes)
    print(lanes)