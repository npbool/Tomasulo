#-*- coding:utf-8 -*-
from PyQt4 import QtCore,QtGui
import sys
from ui import ui_mainwindow
import emulator.controller
class InsInputDialog(QtGui.QDialog):
    def __init__(self,parent=None):
        QtGui.QDialog.__init__(self,parent)

        self.setWindowTitle(u"输入指令")
        
        btnLayout = QtGui.QVBoxLayout()
        btnOk = QtGui.QPushButton(u"确认",self)
        btnCancel = QtGui.QPushButton(u"取消",self)
        btnLayout.addWidget(btnOk)
        btnLayout.addWidget(btnCancel)

        layout = QtGui.QHBoxLayout()
        self.edit = QtGui.QTextEdit(self)
        layout.addWidget(self.edit)
        layout.addLayout(btnLayout)
        
        self.setLayout(layout)

        btnOk.clicked.connect(self.accept)
        btnCancel.clicked.connect(self.reject)


    def getIns(self):
        return self.edit.toPlainText()

class MainWindow(QtGui.QMainWindow):
    def __init__(self,parent=None):
        QtGui.QMainWindow.__init__(self,parent)
        self.ui = ui_mainwindow.Ui_MainWindow()
        self.ui.setupUi(self)
        self.adjustUi()
        self.bindSignal()
        
        self.timer = QtCore.QTimer()
        
        self.emu = emulator.controller.Controller() 
        self.state = 0 #0:initial 1:loade 2:step 3:run

        self.ui.actMultStep.setEnabled(False)
        self.ui.actStep.setEnabled(False)
        self.ui.actRun.setEnabled(False)
        self.ui.actPause.setEnabled(False)
        self.ui.actRestart.setEnabled(False)
        self.ui.btnMemModify.setEnabled(False)

    def updateUI(self):
        ui = self.ui
        emu = self.emu
        # load ins table 
        checkIcon = QtGui.QIcon("ui/check.png")
        ui.insTable.setRowCount(len(emu.ins_list))
        for row in range(len(emu.ins_list)):
            ui.insTable.setItem(row,0,QtGui.QTableWidgetItem(str(emu.ins_list[row].op)))
            ui.insTable.setItem(row,1,QtGui.QTableWidgetItem("F"+str(emu.ins_list[row].rd)))
            if emu.ins_list[row].op in ['LD','ST']:
                ui.insTable.setItem(row,2,QtGui.QTableWidgetItem(str(emu.ins_list[row].rs)))
                ui.insTable.setItem(row,3,QtGui.QTableWidgetItem(''))
            else:
                ui.insTable.setItem(row,2,QtGui.QTableWidgetItem("F"+str(emu.ins_list[row].rs)))
                ui.insTable.setItem(row,3,QtGui.QTableWidgetItem("F"+str(emu.ins_list[row].rt)))
            for st_index in range(4,7):
                ui.insTable.setItem(row,st_index,QtGui.QTableWidgetItem(QtGui.QIcon(),''))
            if emu.ins_list[row].state>0:
                ui.insTable.setItem(row,emu.ins_list[row].state+3,QtGui.QTableWidgetItem(checkIcon,''))

        # load rs
        rs_display_map = [ ('op',1),('vj',2),('vk',3),('qj',4),('qk',5) ]
        for i in range(5):
            rs = emu.rs_list[i+7]
            if rs.busy:
                ui.rsTable.setItem(i,0,QtGui.QTableWidgetItem('Yes'))
                for col in rs_display_map:
                    ui.rsTable.setItem(i,col[1],QtGui.QTableWidgetItem(str(getattr(rs,col[0]))))
            else:
                ui.rsTable.setItem(i,0,QtGui.QTableWidgetItem('No'))
                for col in range(1,6):
                    ui.rsTable.setItem(i,col,QtGui.QTableWidgetItem(''))

        # load loadbuffer
        for i in range(3):
            rs = emu.rs_list[i+1]
            if rs.busy:
                ui.loadBufferTable.setItem(i,0,QtGui.QTableWidgetItem('Yes'))
                ui.loadBufferTable.setItem(i,1,QtGui.QTableWidgetItem(str(rs.A)))
            else:
                ui.loadBufferTable.setItem(i,0,QtGui.QTableWidgetItem('No'))
                ui.loadBufferTable.setItem(i,1,QtGui.QTableWidgetItem(''))
        
        # load storebuffer
        for i in range(3):
            rs = emu.rs_list[i+4]
            if rs.busy:
                ui.storeBufferTable.setItem(i,0,QtGui.QTableWidgetItem('Yes'))
                ui.storeBufferTable.setItem(i,1,QtGui.QTableWidgetItem(str(rs.A)))
                ui.storeBufferTable.setItem(i,2,QtGui.QTableWidgetItem(str(rs.qj)))
            else:
                ui.storeBufferTable.setItem(i,0,QtGui.QTableWidgetItem('No'))
                ui.storeBufferTable.setItem(i,1,QtGui.QTableWidgetItem(''))
                ui.storeBufferTable.setItem(i,2,QtGui.QTableWidgetItem(''))

        # load/store queue
        for i in range(6):
            if i<len(emu.memory_queue) :
                if emu.memory_queue[i] <=3:
                    ui.lsQueueTable.setItem(0,i,QtGui.QTableWidgetItem('Load'+str(emu.memory_queue[i])))
                else:
                    ui.lsQueueTable.setItem(0,i,QtGui.QTableWidgetItem('Store'+str(emu.memory_queue[i]-3)))
            else:
                ui.lsQueueTable.setItem(0,i,QtGui.QTableWidgetItem(''))

        # register table
        for i in range(11):
            ui.regTable.setItem(0,i,QtGui.QTableWidgetItem(str(emu.registers.qi[i])))
            ui.regTable.setItem(1,i,QtGui.QTableWidgetItem(str(emu.registers.val[i])))
        
        # memory
        ui.memTable.setRowCount(0) 
        cur_row = 0
        for mem_index in range(1024):
            if emu.memory.data[mem_index] != 0:
                if cur_row>=ui.memTable.rowCount():
                    ui.memTable.insertRow(cur_row)
                ui.memTable.setItem(cur_row,0,QtGui.QTableWidgetItem(str(mem_index*4)))
                ui.memTable.setItem(cur_row,1,QtGui.QTableWidgetItem(str(emu.memory.data[mem_index])))
                cur_row+=1
        
        ui.lblClock.setText(str(emu.clock_now))
        
    def adjustUi(self):
        self.adjustTable(self.ui.insTable)
        self.adjustTable(self.ui.loadBufferTable)
        self.adjustTable(self.ui.storeBufferTable)
        self.adjustTable(self.ui.rsTable)
        self.adjustTable(self.ui.lsQueueTable)
        self.adjustTable(self.ui.regTable)
        self.adjustTable(self.ui.memTable)
        
    def adjustTable(self,table):
        table.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)

    def bindSignal(self):
        ui = self.ui
        ui.actLoad.triggered.connect(self.loadFile)
        ui.actEdit.triggered.connect(self.inputInstruction)
        ui.actStep.triggered.connect(self.runStep)
        ui.actMultStep.triggered.connect(self.runMultiStep)
        ui.actRun.triggered.connect(self.run)
        ui.actRestart.triggered.connect(self.restart)
        ui.actPause.triggered.connect(self.pause) 
        
        ui.btnMemModify.clicked.connect(self.editMem)

    def loadFile(self):
        fname = QtGui.QFileDialog.getOpenFileName(self,u"载入文件")
        if fname!='':
            with open(fname) as ins_file:
                ins_str = ins_file.read()
                print ins_str
                self.loadInstruction(ins_str)

    def inputInstruction(self):
        dlg = InsInputDialog(self)
        if dlg.exec_()==QtGui.QDialog.Accepted:
            ins_str = str(dlg.getIns())
            if not ins_str.endswith('\n'):
                ins_str+='\n'
            self.loadInstruction(ins_str)

    def loadInstruction(self,ins_str):
        self.emu.read_ins(ins_str)
        self.updateUI()
        state = 1

        self.ui.actMultStep.setEnabled(True)
        self.ui.actStep.setEnabled(True)
        self.ui.actRun.setEnabled(True)
        self.ui.btnMemModify.setEnabled(True)

    def runStep(self):
        self.ui.btnMemModify.setEnabled(False)
        self.ui.actRestart.setEnabled(True)
        if self.emu.done():
            self.showFinishDialog()
        else:
            self.emu.step()
            self.updateUI()
            if self.emu.done():
                self.showFinishDialog()
                if self.timer.isActive():
                    self.timer.stop()

    def runMultiStep(self):
        self.ui.btnMemModify.setEnabled(False)
        self.ui.actRestart.setEnabled(False)
        self.ui.actStep.setEnabled(False)
        self.ui.actMultStep.setEnabled(False)
        self.ui.actRun.setEnabled(False)
        self.ui.actPause.setEnabled(True)

        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.runStep)
        self.timer.start()

    def pause(self):
        self.ui.actStep.setEnabled(True)
        self.ui.actMultStep.setEnabled(True)
        self.ui.actRun.setEnabled(True)
        self.ui.actPause.setEnabled(False)
        self.timer.stop()

    def run(self):
        self.ui.actRestart.setEnabled(True)
        self.ui.btnMemModify.setEnabled(False)
        while not self.emu.done():
            self.emu.step()
            print self.emu.clock_now
        self.updateUI()
        self.showFinishDialog()

    def restart(self):
        self.ui.btnMemModify.setEnabled(True)
        self.emu.reset()
        self.updateUI()
        self.ui.actStep.setEnabled(True)
        self.ui.actMultStep.setEnabled(True)
        self.ui.actRun.setEnabled(True)
        self.ui.btnMemModify.setEnabled(True)
        
        
    def editMem(self):
        addr = int(self.ui.edtMemAddr.text())
        value = float(self.ui.edtMemValue.text())
        self.setMemTableEntry(addr,value)

    def setMemTableEntry(self,addr,value):
        memTable = self.ui.memTable
        row = 0
        while row < memTable.rowCount():
            item = memTable.item(row,0)
            if int(item.text())==addr:
                memTable.item(row,1).setText(str(value))
                return
            elif int(item.text())>addr:
                break
            row += 1
        memTable.insertRow(row)
        newAddrItem=QtGui.QTableWidgetItem(str(addr))
        newValueItem=QtGui.QTableWidgetItem(str(value))
        memTable.setItem(row,0,newAddrItem)
        memTable.setItem(row,1,newValueItem)
        
        self.emu.memory.data[addr/4] = value
    def showFinishDialog(self):
        msg = QtGui.QMessageBox(QtGui.QMessageBox.Information,"Info",u"已执行完毕")
        msg.exec_()


if __name__=="__main__":
    app = QtGui.QApplication(sys.argv)
    wid = MainWindow()
    wid.show()
    sys.exit(app.exec_())

