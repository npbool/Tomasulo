from PyQt4 import QtCore,QtGui
import sys
from ui import ui_mainwindow
class MainWindow(QtGui.QMainWindow):
    def __init__(self,parent=None):
        QtGui.QMainWindow.__init__(self,parent)
        self.ui = ui_mainwindow.Ui_MainWindow()
        self.ui.setupUi(self)
        self.adjustUi()
    def adjustUi(self):
        self.adjustTable(self.ui.insTable)
        self.adjustTable(self.ui.loadBufferTable)
        self.adjustTable(self.ui.storeBufferTable)
        self.adjustTable(self.ui.rsTable)
        self.adjustTable(self.ui.lsQueueTable)
    def adjustTable(self,table):
        table.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)


if __name__=="__main__":
    app = QtGui.QApplication(sys.argv)
    wid = MainWindow()
    wid.show()
    sys.exit(app.exec_())

