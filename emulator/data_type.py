class RS:
    def __init__(self):
        self.reset()
    def reset(self):
        self.op = ''
        self.qj = self.qk = 0
        self.vj = self.vk = 0
        self.A = 0
        self.busy = False
        self.ins = None 

class Ins:
    def __init__(self):
        # 0 not flow in
        # 1 influxed
        # 2 exec
        # 3 write result
        # 4 halt
        self.state = 0
        self.time_cost = 0
        self.op = ''
        # rd, rs, rt
        self.rs = self.rt = self.rd = 0

    def reset(self):
        self.state = 0
    
    @staticmethod
    def parse(ins_str):
        tmp_ins = Ins()

        ins_str = ins_str.replace(',',' ')
        ins_str_sp = ins_str.split()

        try:
            tmp_ins.op = ins_str_sp[0]
            if len(ins_str_sp) == 4: 
                tmp_ins.rd = int(ins_str_sp[1][1:])
                tmp_ins.rs = int(ins_str_sp[2][1:])
                tmp_ins.rt = int(ins_str_sp[3][1:])
                if tmp_ins.op == 'ADDD' or tmp_ins.op == 'SUBD':
                    tmp_ins.time_cost = 2
                elif tmp_ins.op == 'MULD':
                    tmp_ins.time_cost = 10
                elif tmp_ins.op == 'DIVD':
                    tmp_ins.time_cost = 40
                else:
                    print 'Instruction Bad Format: %s' % ins_str
                    exit(1)
            elif tmp_ins.op == 'LD' or tmp_ins.op == 'ST':
                tmp_ins.rd = int(ins_str_sp[1][1:])
                tmp_ins.rs = int(ins_str_sp[2])
                tmp_ins.time_cost = 2
            else:
                print 'Instruction Bad Format: %s' % ins_str
                exit(1)
        except IndexError:
            print 'Instruction Bad Format: %s' % ins_str
            exit(1)
        
        return tmp_ins

class Reg:
    def __init__(self, size=32):
        self.qi = [0 for i in range(size)]
        self.val = [0.0 for i in range(size)]
    def reset(self):
        self.qi = [0 for i in range(len(self.qi))]
        self.val = [0.0 for i in range(len(self.val))]

class Mem:
    def __init__(self, size=4096):
        self.data = [0.0 for i in range(size)]
    def get_item(self, index):
        return self.data[index]
    def set_item(self, index, _data):
        self.data[index] = _data
    def reset(self):
        self.data = [0.0 for i in range(len(self.data))]
