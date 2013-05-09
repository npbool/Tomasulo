class Adder_unit:
    def __init__(self):
        self.reset()
    def reset(self):
        self.rs_id = -1 
        self.end_time = 0
        self.busy = False
        self.result = 0.0


class Multiplier_unit:
    def __init__(self):
        self.reset()
    def reset(self):
        self.rs_id = -1 
        self.end_time = 0
        self.busy = False
        self.result = 0.0

class Memory_unit:
    def __init__(self):
        self.reset()
    def reset(self):
        self.rs_id = -1 
        self.end_time = 0
        self.result = 0.0
