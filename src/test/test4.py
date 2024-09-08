import sys
from PyQt5.QtWidgets import QApplication, QListWidget, QListWidgetItem, QVBoxLayout, QWidget


class DragDropListWidget(QListWidget):
    def __init__(self, data_array):
        super().__init__()

        self.data_array = data_array

        # 允许拖放操作
        self.setDragDropMode(self.InternalMove)
        self.setSelectionMode(self.ExtendedSelection)

        # 添加数据数组中的项到 QListWidget
        for item in self.data_array:
            self.addItem(QListWidgetItem(item))

        # 连接拖放信号到槽函数
        self.model().rowsMoved.connect(self.update_data_array)

    def update_data_array(self, parent, start, end, destination, row):
        # 更新数据数组的顺序
        if start < row:
            self.data_array.insert(row, self.data_array.pop(start))
        else:
            self.data_array.insert(row, self.data_array.pop(start))

        # 打印更新后的数据数组
        print("Updated Data Array:", self.data_array)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 创建一个包含一些数据的数组
    data_array = ["Item 0", "Item 1", "Item 2", "Item 3", "Item 4", "Item 5", "Item 6", "Item 7"]

    # 创建窗口和布局
    window = QWidget()
    layout = QVBoxLayout()

    # 创建自定义 DragDropListWidget，并传入数据数组
    list_widget = DragDropListWidget(data_array)
    layout.addWidget(list_widget)

    window.setLayout(layout)
    window.setWindowTitle('QListWidget 拖曳排序同步数据示例')
    window.resize(300, 200)
    window.show()

    sys.exit(app.exec_())
