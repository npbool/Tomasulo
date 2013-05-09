from controller import *

ctrl = Controller()

ins_fd = open('instructions.txt')

ctrl.read_ins(ins_fd.read())
ctrl.write_memory(1024, 4.0)
ctrl.write_memory(1028, 3.0)
ctrl.run()
print 'Memory: #0: a = %f' % ctrl.read_memory(0)
print 'Memory: #4: b = %f' % ctrl.read_memory(4)
print 'Memory: #8: 4+3=%f' % ctrl.read_memory(8)
print 'Memory: #12: 4-3=%f' % ctrl.read_memory(12)
print 'Memory: #16: 4*3=%f' % ctrl.read_memory(16)
print 'Memory: #20: 4/3=%f' % ctrl.read_memory(20)
