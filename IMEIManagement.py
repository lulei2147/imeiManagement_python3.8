from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeWidgetItem, QFileDialog, QMenu, QHeaderView, QPushButton, QWidget, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon
from MainUI import *
import sys
#import resrc_rc


class MainUI(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.pte_output.textChanged.connect(self.pte_output.ensureCursorVisible)
        self.treeWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treeWidget.customContextMenuRequested.connect(self.generateMenu)

        self.cbox_info_type.addItems(["单号", "IMEI"])
        self.cbox_dev_type.addItems(["压力", "液位"])
        self.cbox_input_mode.addItems(["自动", "手动"])

        # timer flag
        self.timer_flag_input_finished = False

        self.timer = QTimer()
        self.timer.timeout.connect(self.timer_timeout)
        self.timer.setSingleShot(True)

    def cbox_input_mode_currentIndexChanged(self):
        if self.le_input.text() != '':
            self.le_input.clear()

        if self.cbox_input_mode.currentText() == "手动":
            self.btn_add.setEnabled(True)
        else:
            self.btn_add.setEnabled(False)


    def timer_timeout(self):
        self.timer.stop()
        self.add_info2tree()

    def le_input_text_changed(self, str):
        if self.treeWidget.topLevelItemCount() == 0 and self.cbox_info_type.currentText() == 'IMEI':
            self.pte_output.insertPlainText("请先输入<单号>." + '\n')
            self.le_input.clear()
            return

        if self.le_input.text() != '' and self.cbox_input_mode.currentText() == "自动":
            self.timer.start(300)

    def cbox_info_type_currentIndexChanged(self, str):
        if str == "单号":
            self.cbox_dev_type.setEnabled(False)
        else:
            self.cbox_dev_type.setEnabled(True)

    def le_input_finished(self):
        if self.cbox_input_mode.currentText() == "手动":
            self.add_info2tree()
            self.le_input.setFocus()

    def add_info2tree(self):
        if self.cbox_info_type.currentText() == "单号":
            if self.le_input.text() == '':
                self.pte_output.insertPlainText("单号不能为空，请输入<单号>." + '\n')
            else:
                order_number = QTreeWidgetItem(self.treeWidget)
                order_number.setText(0, self.le_input.text())
                order_number.setCheckState(0, Qt.Checked)
                self.le_input.clear()
        else:
            if self.treeWidget.topLevelItem(0).checkState(0) == Qt.Checked:
                if self.le_input.text() == '':
                    self.pte_output.insertPlainText("请输入<IMEI>." + '\n')
                else:
                    node = QTreeWidgetItem(self.treeWidget.topLevelItem(0))
                    node.setText(0, self.cbox_dev_type.currentText())
                    node.setText(1, self.le_input.text())
                    self.le_input.clear()
                    self.treeWidget.scrollToBottom()
            else:
                self.pte_output.insertPlainText("请先选择<单号>." + '\n')

        self.treeWidget.expandAll()

    def item_clicked(self, item):
        if item.parent() == None and item.checkState(0) == Qt.Checked:
            self.pte_output.insertPlainText("当前<单号>： " + item.text(0) + '\n')
            self.pte_output.insertPlainText("设备总数：" + str(self.treeWidget.topLevelItem(self.treeWidget.indexOfTopLevelItem(item)).childCount()) + '\n')

    def btn_save_clicked(self):
        if self.treeWidget.topLevelItemCount() == 0:
            return

        if self.treeWidget.topLevelItem(0).checkState(0) == Qt.Checked and self.treeWidget.topLevelItem(0).childCount() != 0:
            file_dir = QFileDialog.getExistingDirectory(self, "文件路径", "./")
            if file_dir == '':
                return
            self.save2txt(file_dir)
        else:
            self.pte_output.insertPlainText("选择要保存的<单号>." + '\n')

    def save2txt(self, path):
        imei_list = []
        imei_list.append("<单号>" + self.treeWidget.topLevelItem(0).text(0) + ":\n")

        for i in range(self.treeWidget.topLevelItem(0).childCount()):
            item = self.treeWidget.topLevelItem(0).child(i)
            imei_list.append(item.text(0) + ': ' + item.text(1) + '\n')

        file_path = path + "/" + self.treeWidget.topLevelItem(0).text(0) + ".txt"
        file = open(file_path, "w")
        file.writelines(imei_list)
        file.close()
        self.pte_output.insertPlainText(file_path + "  保存成功!" + '\n')

    def generateMenu(self, pos):
        item = self.treeWidget.itemAt(pos)

        if item == None:
            return

        if item.parent() != None:
            menu = QMenu()
            delete_item = menu.addAction("删除")
            action = menu.exec_(self.treeWidget.mapToGlobal(pos))

            if action == delete_item:
                item.parent().removeChild(item)
        else:
            menu = QMenu()
            delete_item = menu.addAction("删除")
            imei_sum = menu.addAction("IMEI总数")
            action = menu.exec_(self.treeWidget.mapToGlobal(pos))

            if action == delete_item:
                self.treeWidget.takeTopLevelItem(self.treeWidget.indexOfTopLevelItem(item))
            elif action == imei_sum:
                self.pte_output.insertPlainText("IMEI总数： " + str(
                    self.treeWidget.topLevelItem(self.treeWidget.indexOfTopLevelItem(item)).childCount()) + '\n')
            else:
                pass

    def le_input_getFocus(self):
        self.le_input.setFocus()


if __name__ == '__main__':
    a = QApplication(sys.argv)
    mainUI = MainUI()
    mainUI.show()
    sys.exit(a.exec_())
