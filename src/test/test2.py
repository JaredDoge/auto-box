from PyQt5 import QtWidgets
import sys

app = QtWidgets.QApplication(sys.argv)

Form = QtWidgets.QWidget()
Form.setWindowTitle('oxxo.studio')
Form.resize(300, 200)

label = QtWidgets.QLabel(Form)
label.setGeometry(0,0,100,30)

def key(self):
    keycode = self.key()         # 取得該按鍵的 keycode
    label.setText(str(keycode))  # QLabel 印出 keycode

Form.keyPressEvent = key         # 建立按下鍵盤事件，對應到 key 函式

Form.show()
sys.exit(app.exec_())