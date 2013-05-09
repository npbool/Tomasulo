#-*- coding:utf-8 -*-
from PyQt4 import QtCore,QtGui
import sys
from ui import ui_mainwindow
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
        
        self.runTimer = QtCore.QTimer()

    def updateUI(self):
        pass
        
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
        ui.actMem.triggered.connect(self.editMem)
        
        ui.btnMemModify.clicked.connect(self.editMem)

    def loadFile(self):
        fname = QtGui.QFileDialog.getOpenFileName(self,u"载入文件")
        if fname!='':
            with open(fname) as ins_file:
                ins_str = ins_file.read()
            self.loadInstruction(ins_str)

    def inputInstruction(self):
        dlg = InsInputDialog(self)
        if dlg.exec_()==QtGui.QDialog.Accepted:
            self.loadInstruction(dlg.getIns())

    def loadInstruction(self,ins_str):
        pass

    def runStep(self):
        pass
    def runMultiStep(self):
        pass
    def run(self):
        pass
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


if __name__=="__main__":
    app = QtGui.QApplication(sys.argv)
    wid = MainWindow()
    wid.show()
    sys.exit(app.exec_())

