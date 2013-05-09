from data_type import *
from func_unit import *

import time


class Controller:
    def __init__(self):
        self.ins_list = list()
        self.ins_current_id = 0 # The next instruction to execute

        self.reg_size = 32
        self.mem_size = 4096
        self.registers = Reg(size=self.reg_size)
        self.memory = Mem(size=self.mem_size)

        # 0-2 load
        # 3-5 store
        # 6-8 adder
        # 9-10 mult
        self.rs_list = [RS() for i in range(12)]
        self.rs_map = {'LD':(1,4), 'ST':(4,7), 'ADDD':(7,10), 'SUBD':(7,10), 'MULD':(10,12), 'DIVD':(10,12)}

        # memory_unit
        self.mem_unit = Memory_unit()
        # adder_unit
        self.add_unit = Adder_unit()
        # multi_unit
        self.multi_unit = Multiplier_unit()

        self.memory_queue = list()

        # setup timer
        self.clock_now = 0
    def reset(self):
        # reset instructions' state
        for ins in self.ins_list:
            ins.reset()

        self.registers.reset()
        self.memory.reset()

        for rs in self.rs_list:
            rs.reset()

        self.mem_unit.reset()
        self.add_unit.reset()
        self.multi_unit.reset()

        self.memory_queue = list()

        self.clock_now = 0
    def read_ins(self,ins_text_data):
        ins_lines = ins_text_data.split('\n')
        ins_lines.remove('')
        for ins_line in ins_lines:
            self.ins_list.append(Ins.parse(ins_line))
    
    def write_memory(self, index, data):
        self.memory.set_item(index/4, data)
    def read_memory(self, index):
        return self.memory.get_item(index/4)

    def print_state(self):
        print 'Time: %d' % self.clock_now
        for ins in self.ins_list:
            if ins.op == 'LD' or ins.op == 'ST':
                print '%s F%d %d: %d' % (ins.op, ins.rd, ins.rs, ins.state)
            else:
                print '%s F%d F%d F%d: %d' % (ins.op, ins.rd, ins.rs, ins.rt, ins.state)
        print 

    def print_reg(self):
        for reg_id in range(self.reg_size):
            print 'Registers: Q[%d]: %d, Value[%d]: %f' % (reg_id, self.registers.qi[reg_id], reg_id, self.registers.val[reg_id])

    def print_rs(self):
        for rs_id in range(len(self.rs_list)):
            print 'RS #%d, Op: %s, Qj: %d, Qk: %d, Vj: %d, Vk: %d, busy: %d, A: %d' % (rs_id, self.rs_list[rs_id].op, self.rs_list[rs_id].qj, self.rs_list[rs_id].qk, self.rs_list[rs_id].vj, self.rs_list[rs_id].vk, self.rs_list[rs_id].busy, self.rs_list[rs_id].A)
    
    def print_units(self):
        print 'add unit: rs_id: %d, result: %f, busy: %d, end_time: %d ' % ( self.add_unit.rs_id, self.add_unit.result, self.add_unit.busy, self.add_unit.end_time)
        print 'mult unit: rs_id: %d, result: %f, busy: %d, end_time: %d ' % ( self.multi_unit.rs_id, self.multi_unit.result, self.multi_unit.busy, self.add_unit.end_time) 

    def done(self):
        for ins in self.ins_list:
            if ins.state <= 2:
                return False

        return True

    def run(self):
        while True:
            if self.done() == True:
                break

            self.step()
#            self.print_rs()
#            self.print_state()
#            self.print_units()

    def step(self):
        # increment clock 
        self.clock_now += 1

        # update
        self.update()

        # execute
        self.execute()

        # influx
        self.influx()

    def influx(self):
        if self.ins_current_id >= len(self.ins_list):
            return
        # check whether there is any vacant reservation stations
        current_ins = self.ins_list[self.ins_current_id]
        for i in range(self.rs_map[current_ins.op][0], self.rs_map[current_ins.op][1]):
            if self.rs_list[i].busy == False:
                current_ins.state = 1

                self.rs_list[i].op = current_ins.op
                self.rs_list[i].busy = True

                if current_ins.op == 'LD' or current_ins.op == 'ST':
                    # rs is for immediate
                    self.rs_list[i].A = current_ins.rs

                    # load
                    if current_ins.op == 'LD':
                        self.registers.qi[current_ins.rd] = i
                    # store
                    else:
                        # the register data is ready to store into memory
                        if self.registers.qi[current_ins.rd] == 0: 
                            self.rs_list[i].qj = 0
                            self.rs_list[i].vj = self.registers.val[current_ins.rd]
                        # not ready yet
                        else: 
                            self.rs_list[i].qj = self.registers.qi[current_ins.rd]
                    
                    self.memory_queue.append(i)

                else:
                    # rs
                    if self.registers.qi[current_ins.rs] == 0:
                        self.rs_list[i].qj = 0
                        self.rs_list[i].vj = self.registers.val[current_ins.rs]
                    else:
                        self.rs_list[i].qj = self.registers.qi[current_ins.rs]

                    # rt
                    if self.registers.qi[current_ins.rt] == 0:
                        self.rs_list[i].qk = 0
                        self.rs_list[i].vk = self.registers.val[current_ins.rt]
                    else:
                        self.rs_list[i].qk = self.registers.qi[current_ins.rt]
                    # destination register 
                    self.registers.qi[current_ins.rd] = i

                self.rs_list[i].ins = self.ins_list[self.ins_current_id]
                self.ins_current_id += 1
                break

    def execute(self):
        # load/store
        if len(self.memory_queue) > 0:
            rs_index = self.memory_queue[0]

            current_ins = self.rs_list[rs_index].ins;
            if current_ins.state < 2:
                if self.rs_list[rs_index].op == 'LD':
                    self.mem_unit.result = self.memory.get_item(self.rs_list[rs_index].A/4)
                    current_ins.state = 2

                    self.mem_unit.rs_id = rs_index
                    self.mem_unit.end_time = self.clock_now + 2
                else: # Store
                    if self.rs_list[rs_index].qj == 0:
                        self.mem_unit.result = self.rs_list[rs_index].vj

                        current_ins.state = 2

                        self.mem_unit.rs_id = rs_index
                        self.mem_unit.end_time = self.clock_now + 2
            else:
                pass

        # adder 
        if self.add_unit.busy == False:
            for i in range(self.rs_map['ADDD'][0], self.rs_map['ADDD'][1]):
                if self.rs_list[i].qj == 0 and self.rs_list[i].qk == 0 and self.rs_list[i].busy == True:
                    if self.rs_list[i].ins.op == 'ADDD':
                        self.add_unit.result = self.rs_list[i].vj + self.rs_list[i].vk
                        print 'Generating a add result: %f + %f = %f' % (self.rs_list[i].vj, self.rs_list[i].vk, self.multi_unit.result)
                    else:
                        self.add_unit.result = self.rs_list[i].vj - self.rs_list[i].vk
                        print 'Generating a sub result: %f - %f = %f' % (self.rs_list[i].vj, self.rs_list[i].vk, self.multi_unit.result)

                    self.rs_list[i].ins.state = 2

                    self.add_unit.rs_id = i
                    self.add_unit.end_time = self.clock_now + 2
                    self.add_unit.busy = True
                    break
        else: 
            pass


        # multiplier
        if self.multi_unit.busy == False:
            for i in range(self.rs_map['MULD'][0], self.rs_map['MULD'][1]):
                if self.rs_list[i].qj == 0 and self.rs_list[i].qk == 0 and self.rs_list[i].busy == True:
                    if self.rs_list[i].ins.op == 'MULD':
                        self.multi_unit.result = self.rs_list[i].vj * self.rs_list[i].vk
                        print 'Generating a mult result: %f * %f = %f' % (self.rs_list[i].vj, self.rs_list[i].vk, self.multi_unit.result)
                        self.multi_unit.end_time = self.clock_now + 10
                    else:
                        self.multi_unit.result = self.rs_list[i].vj / self.rs_list[i].vk
                        print 'Generating a divd result: %f / %f = %f' % (self.rs_list[i].vj, self.rs_list[i].vk, self.multi_unit.result)
                        self.multi_unit.end_time = self.clock_now + 40
                    self.rs_list[i].ins.state = 2

                    self.multi_unit.rs_id = i
                    self.multi_unit.busy = True
                    break
        else: 
            pass
                

    def update(self):
        # load/store
        if self.mem_unit.end_time == self.clock_now:
            rs_index = self.memory_queue[0]
            ins = self.rs_list[rs_index].ins
            if ins.op == 'LD': # Load
                self.registers.val[ins.rd] = self.mem_unit.result
                self.registers.qi[ins.rd] = 0

                for i in range(self.rs_map['LD'][0], self.rs_map['MULD'][1]):
                    if self.rs_list[i].qj == self.mem_unit.rs_id:
                        self.rs_list[i].qj = 0
                        self.rs_list[i].vj = self.mem_unit.result
                    if self.rs_list[i].qk == self.mem_unit.rs_id:
                        self.rs_list[i].qk = 0
                        self.rs_list[i].vk = self.mem_unit.result

            else: # Store
                self.memory.set_item(self.rs_list[rs_index].A/4, self.mem_unit.result) 

            assert(rs_index == self.mem_unit.rs_id)
            self.rs_list[rs_index].ins.state = 3
            self.rs_list[rs_index].busy = False

            self.memory_queue.remove(rs_index)
        # adder
        if self.add_unit.end_time == self.clock_now:
            for reg_id in range(self.reg_size):
                if self.registers.qi[reg_id] == self.add_unit.rs_id:
                    self.registers.qi[reg_id] = 0
                    self.registers.val[reg_id] = self.add_unit.result

            for i in range(self.rs_map['LD'][0], self.rs_map['MULD'][1]):
                if self.rs_list[i].qj == self.add_unit.rs_id:
                    self.rs_list[i].qj = 0
                    self.rs_list[i].vj = self.add_unit.result
                if self.rs_list[i].qk == self.add_unit.rs_id:
                    self.rs_list[i].qk = 0
                    self.rs_list[i].vk = self.add_unit.result

            self.rs_list[self.add_unit.rs_id].ins.state = 3
            self.rs_list[self.add_unit.rs_id].busy = False
            self.add_unit.busy = False

        # multiplier
        if self.multi_unit.end_time == self.clock_now:
            for reg_id in range(self.reg_size):
                if self.registers.qi[reg_id] == self.multi_unit.rs_id:
                    self.registers.qi[reg_id] = 0
                    self.registers.val[reg_id] = self.multi_unit.result

            for i in range(self.rs_map['LD'][0], self.rs_map['MULD'][1]):
                if self.rs_list[i].qj == self.multi_unit.rs_id:
                    self.rs_list[i].qj = 0
                    self.rs_list[i].vj = self.multi_unit.result
                if self.rs_list[i].qk == self.multi_unit.rs_id:
                    self.rs_list[i].qk = 0
                    self.rs_list[i].vk = self.multi_unit.result

            self.rs_list[self.multi_unit.rs_id].ins.state = 3
            self.rs_list[self.multi_unit.rs_id].busy = False
            self.multi_unit.busy = False

