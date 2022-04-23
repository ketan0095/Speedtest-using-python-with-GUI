from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal, QObject, pyqtSlot, QThread
import subprocess, json, os, csv
from csv import DictWriter


installation_path = os.getcwd()
json_path = os.path.join(installation_path, "output.json")  # to show output to GUI
report_path = os.path.join(
    installation_path, "report.csv"
)  # for user to have detailed report


def dict_to_json(json_path, dict, ind):
    """
    create json file using dict
    """
    with open(json_path, "w") as outfile:
        json.dump(dict, outfile, indent=ind)


def json_to_dict(json_path):
    """
    read any json file as a dict
    """
    with open(json_path) as json_file:
        return json.load(json_file)


if os.path.exists(json_path) == False:
    data_ = {}
    data_["Server ID"] = ""
    data_["Sponsor"] = ""
    data_["Server Name"] = ""
    data_["Timestamp"] = ""
    data_["Distance"] = ""
    data_["Ping"] = ""
    data_["Download"] = ""
    data_["Upload"] = ""
    data_["Share"] = ""
    data_["IP Address"] = ""
    data_["Refresh"] = 5

    dict_to_json(json_path, data_, 4)

# read output json
output = json_to_dict(json_path)

# -----------------------------------
# For CSV file
# -----------------------------------
field_names = [
    "Server ID",
    "Sponsor",
    "Server Name",
    "Timestamp",
    "Distance",
    "Ping",
    "Download",
    "Upload",
    "Share",
    "IP Address",
    "Refresh",
]

if os.path.exists(report_path) == False:
    # open CSV file and assign header
    with open(report_path, "w") as file:
        dw = csv.DictWriter(file, delimiter=",", fieldnames=field_names)
        dw.writeheader()


class WorkerSignals(QtWidgets.QWidget):  ######## channel to handle signals
    complete = pyqtSignal(str)


# Using a worker thread so that GUI doesnot become unresponsive
class Worker_deepN(QObject):  #
    def __init__(self, val):
        super(Worker_deepN, self).__init__()
        self.signals = WorkerSignals()
        self.ref = val

    @pyqtSlot()
    def run(self):
        try:
            print("Thread started...")
            returned_text = subprocess.check_output(
                "speedtest-cli --csv", shell=True, universal_newlines=True
            ).strip()
            all_ = returned_text.split(",")

            output["Server ID"] = all_[0]
            output["Sponsor"] = all_[1]
            output["Server Name"] = all_[2]
            output["Timestamp"] = all_[3]
            output["Distance"] = all_[4]
            output["Ping"] = all_[5]
            output["Download"] = round(float(all_[6]) / 10**6, 2)
            output["Upload"] = round(float(all_[7]) / 10**6, 2)
            output["Share"] = all_[8]
            output["IP Address"] = all_[9]
            output["Refresh"] = int(self.ref)
            print("Current status : ", output)

            # updating json file to GUI
            dict_to_json(json_path, output, 4)
            o_ = json_to_dict(json_path)

            # updating to csv file for user
            with open(report_path, "a") as f_object:
                # Pass the file object and a list
                # of column names to DictWriter()
                # You will get a object of DictWriter
                dictwriter_object = DictWriter(f_object, fieldnames=field_names)
                # Pass the dictionary as an argument to the Writerow()
                dictwriter_object.writerow(o_)
                # Close the file object
                f_object.close()
            # send signal to stop the thread
            self.signals.complete.emit("200")
        except:
            # handle error if internet is not working
            output["Server ID"] = ""
            output["Sponsor"] = ""
            output["Server Name"] = ""
            output["Timestamp"] = ""
            output["Distance"] = ""
            output["Ping"] = ""
            output["Download"] = 0
            output["Upload"] = 0
            output["Share"] = ""
            output["IP Address"] = ""
            output["Refresh"] = int(self.ref)
            print("Current status : ", output)
            dict_to_json(json_path, output, 4)
            o_ = json_to_dict(json_path)
            with open(report_path, "a") as f_object:
                # Pass the file object and a list
                # of column names to DictWriter()
                # You will get a object of DictWriter
                dictwriter_object = DictWriter(f_object, fieldnames=field_names)
                # Pass the dictionary as an argument to the Writerow()
                dictwriter_object.writerow(o_)
                # Close the file object
                f_object.close()
            # send signal to stop the thread
            self.signals.complete.emit("200")


# Flag to start the thread
running_flag = False


class Ui_Form(QtWidgets.QWidget):
    def verify1(self, res):
        global running_flag
        running_flag = False
        output = json_to_dict(json_path)
        self.label_23.setText("Thread started....")
        self.label_2.setText(output["Server Name"])
        self.label_6.setText(output["Sponsor"])
        self.label_8.setText("{} ms".format(output["Ping"]))
        self.label_10.setText(output["IP Address"])
        self.label_16.setText(str(output["Upload"]))
        self.label_20.setText(str(output["Download"]))
        self.lineEdit.setText(str(output["Refresh"]))
        self.threadpool6.quit()
        self.label_23.setText("SpeedTest Complete.")

    def line_text(self):
        global running_flag
        if not running_flag:
            self.label_23.setText("Thread started....")
            running_flag = True
            get = int(self.lineEdit.text())
            self.worker1 = Worker_deepN(get)
            self.worker1.signals.complete.connect(self.verify1)
            self.worker1.moveToThread(self.threadpool6)
            self.threadpool6.started.connect(self.worker1.run)
            self.threadpool6.start()

    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(700, 550)
        Form.setMinimumSize(QtCore.QSize(700, 550))
        Form.setMaximumSize(QtCore.QSize(700, 550))
        self.frame = QtWidgets.QFrame(Form)
        self.frame.setGeometry(QtCore.QRect(0, 0, 701, 551))
        self.frame.setStyleSheet("background-color: rgb(56, 56, 56);")
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.frame_2 = QtWidgets.QFrame(self.frame)
        self.frame_2.setGeometry(QtCore.QRect(10, 10, 211, 91))
        self.frame_2.setStyleSheet("border:3px dashed green;\n" "border-radius:6px;")
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.label = QtWidgets.QLabel(self.frame_2)
        self.label.setGeometry(QtCore.QRect(35, 10, 141, 31))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setStyleSheet("border:none;\n" "color:white;")
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.frame_2)
        self.label_2.setGeometry(QtCore.QRect(35, 50, 141, 31))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setStyleSheet("border:none;\n" "color:yellow;")
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.frame_3 = QtWidgets.QFrame(self.frame)
        self.frame_3.setGeometry(QtCore.QRect(270, 10, 401, 91))
        self.frame_3.setStyleSheet("border:3px dashed green;\n" "border-radius:6px;")
        self.frame_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")
        self.label_5 = QtWidgets.QLabel(self.frame_3)
        self.label_5.setGeometry(QtCore.QRect(10, 10, 381, 31))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.label_5.setFont(font)
        self.label_5.setStyleSheet("border:none;\n" "color:white;")
        self.label_5.setAlignment(QtCore.Qt.AlignCenter)
        self.label_5.setIndent(-5)
        self.label_5.setObjectName("label_5")
        self.label_6 = QtWidgets.QLabel(self.frame_3)
        self.label_6.setGeometry(QtCore.QRect(10, 50, 381, 31))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label_6.setFont(font)
        self.label_6.setStyleSheet("border:none;\n" "color:yellow;")
        self.label_6.setAlignment(QtCore.Qt.AlignCenter)
        self.label_6.setObjectName("label_6")
        self.frame_4 = QtWidgets.QFrame(self.frame)
        self.frame_4.setGeometry(QtCore.QRect(10, 110, 211, 91))
        self.frame_4.setStyleSheet("border:3px dashed green;\n" "border-radius:6px;")
        self.frame_4.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_4.setObjectName("frame_4")
        self.label_7 = QtWidgets.QLabel(self.frame_4)
        self.label_7.setGeometry(QtCore.QRect(35, 10, 141, 31))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.label_7.setFont(font)
        self.label_7.setStyleSheet("border:none;\n" "color:white;")
        self.label_7.setAlignment(QtCore.Qt.AlignCenter)
        self.label_7.setObjectName("label_7")
        self.label_8 = QtWidgets.QLabel(self.frame_4)
        self.label_8.setGeometry(QtCore.QRect(55, 50, 121, 31))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label_8.setFont(font)
        self.label_8.setStyleSheet("border:none;\n" "color:yellow;")
        self.label_8.setAlignment(QtCore.Qt.AlignCenter)
        self.label_8.setObjectName("label_8")
        self.frame_5 = QtWidgets.QFrame(self.frame)
        self.frame_5.setGeometry(QtCore.QRect(365, 110, 211, 91))
        self.frame_5.setStyleSheet("border:3px dashed green;\n" "border-radius:6px;")
        self.frame_5.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_5.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_5.setObjectName("frame_5")
        self.label_9 = QtWidgets.QLabel(self.frame_5)
        self.label_9.setGeometry(QtCore.QRect(35, 10, 141, 31))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.label_9.setFont(font)
        self.label_9.setStyleSheet("border:none;\n" "color:white;")
        self.label_9.setAlignment(QtCore.Qt.AlignCenter)
        self.label_9.setObjectName("label_9")
        self.label_10 = QtWidgets.QLabel(self.frame_5)
        self.label_10.setGeometry(QtCore.QRect(35, 50, 141, 31))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label_10.setFont(font)
        self.label_10.setStyleSheet("border:none;\n" "color:yellow;")
        self.label_10.setAlignment(QtCore.Qt.AlignCenter)
        self.label_10.setObjectName("label_10")
        self.label_11 = QtWidgets.QLabel(self.frame)
        self.label_11.setGeometry(QtCore.QRect(90, 240, 200, 200))
        self.label_11.setStyleSheet(
            "border:2px solid green;\n" "border-radius:100px;\n" ""
        )
        self.label_11.setText("")
        self.label_11.setObjectName("label_11")
        self.label_12 = QtWidgets.QLabel(self.frame)
        self.label_12.setGeometry(QtCore.QRect(360, 240, 200, 200))
        self.label_12.setStyleSheet(
            "border:2px solid green;\n" "border-radius:100px;\n" ""
        )
        self.label_12.setText("")
        self.label_12.setObjectName("label_12")
        self.label_13 = QtWidgets.QLabel(self.frame)
        self.label_13.setGeometry(QtCore.QRect(100, 250, 180, 180))
        self.label_13.setStyleSheet(
            "border:2px solid white;\n" "border-radius:90px;\n" ""
        )
        self.label_13.setText("")
        self.label_13.setObjectName("label_13")
        self.label_14 = QtWidgets.QLabel(self.frame)
        self.label_14.setGeometry(QtCore.QRect(370, 250, 180, 180))
        self.label_14.setStyleSheet(
            "border:2px solid white;\n" "border-radius:90px;\n" ""
        )
        self.label_14.setText("")
        self.label_14.setObjectName("label_14")
        self.label_15 = QtWidgets.QLabel(self.frame)
        self.label_15.setGeometry(QtCore.QRect(140, 280, 91, 31))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.label_15.setFont(font)
        self.label_15.setStyleSheet("border:none;\n" "color:white;")
        self.label_15.setAlignment(QtCore.Qt.AlignCenter)
        self.label_15.setObjectName("label_15")
        self.label_16 = QtWidgets.QLabel(self.frame)
        self.label_16.setGeometry(QtCore.QRect(120, 330, 141, 31))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(75)
        self.label_16.setFont(font)
        self.label_16.setStyleSheet("border:none;\n" "color:yellow;")
        self.label_16.setAlignment(QtCore.Qt.AlignCenter)
        self.label_16.setObjectName("label_16")
        self.label_17 = QtWidgets.QLabel(self.frame)
        self.label_17.setGeometry(QtCore.QRect(140, 380, 91, 31))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.label_17.setFont(font)
        self.label_17.setStyleSheet("border:none;\n" "color:white;")
        self.label_17.setAlignment(QtCore.Qt.AlignCenter)
        self.label_17.setObjectName("label_17")
        self.label_18 = QtWidgets.QLabel(self.frame)
        self.label_18.setGeometry(QtCore.QRect(410, 380, 101, 31))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.label_18.setFont(font)
        self.label_18.setStyleSheet("border:none;\n" "color:white;")
        self.label_18.setAlignment(QtCore.Qt.AlignCenter)
        self.label_18.setObjectName("label_18")
        self.label_19 = QtWidgets.QLabel(self.frame)
        self.label_19.setGeometry(QtCore.QRect(410, 280, 101, 31))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.label_19.setFont(font)
        self.label_19.setStyleSheet("border:none;\n" "color:white;")
        self.label_19.setAlignment(QtCore.Qt.AlignCenter)
        self.label_19.setObjectName("label_19")
        self.label_20 = QtWidgets.QLabel(self.frame)
        self.label_20.setGeometry(QtCore.QRect(380, 330, 161, 31))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(75)
        self.label_20.setFont(font)
        self.label_20.setStyleSheet("border:none;\n" "color:yellow;")
        self.label_20.setAlignment(QtCore.Qt.AlignCenter)
        self.label_20.setObjectName("label_20")
        self.label_21 = QtWidgets.QLabel(self.frame)
        self.label_21.setGeometry(QtCore.QRect(500, 490, 71, 31))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label_21.setFont(font)
        self.label_21.setStyleSheet("border:none;\n" "color:white;")
        self.label_21.setAlignment(QtCore.Qt.AlignCenter)
        self.label_21.setObjectName("label_21")

        self.label_23 = QtWidgets.QLabel(self.frame)
        self.label_23.setGeometry(QtCore.QRect(60, 490, 291, 31))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label_23.setFont(font)
        self.label_23.setStyleSheet("border:none;\n" "color:white;")
        self.label_23.setAlignment(QtCore.Qt.AlignCenter)
        self.label_23.setObjectName("label_23")

        self.lineEdit = QtWidgets.QLineEdit(self.frame)
        self.lineEdit.setGeometry(QtCore.QRect(580, 485, 41, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.lineEdit.setFont(font)
        self.lineEdit.setStyleSheet(
            "border:none;\n"
            "color: rgb(255, 255, 255);\n"
            "border-bottom:1px solid white;"
        )
        self.lineEdit.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit.setObjectName("lineEdit")
        self.label_22 = QtWidgets.QLabel(self.frame)
        self.label_22.setGeometry(QtCore.QRect(620, 485, 41, 31))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.label_22.setFont(font)
        self.label_22.setStyleSheet("border:none;\n" "color:white;")
        self.label_22.setAlignment(QtCore.Qt.AlignCenter)
        self.label_22.setObjectName("label_22")

        self.retranslateUi(Form)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.line_text)
        self.timer.start(output["Refresh"] * 1000)

        self.threadpool6 = QThread()

        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "SpeedTest"))
        self.label.setText(_translate("Form", "Server Name "))
        self.label_2.setText(_translate("Form", output["Server Name"]))
        self.label_5.setText(_translate("Form", "Sponsor"))
        self.label_6.setText(_translate("Form", output["Sponsor"]))
        self.label_7.setText(_translate("Form", "Ping"))
        self.label_8.setText(_translate("Form", "{} ms".format(output["Ping"])))
        self.label_9.setText(_translate("Form", "IP Address"))
        self.label_10.setText(_translate("Form", output["IP Address"]))
        self.label_15.setText(_translate("Form", "Upload"))
        self.label_16.setText(_translate("Form", str(output["Upload"])))
        self.label_17.setText(_translate("Form", "Mb"))
        self.label_18.setText(_translate("Form", "Mb"))
        self.label_19.setText(_translate("Form", "Download"))
        self.label_20.setText(_translate("Form", str(output["Download"])))
        self.label_21.setText(_translate("Form", "Refresh"))
        self.label_23.setText(_translate("Form", "Loading ......"))
        self.lineEdit.setText(_translate("Form", str(output["Refresh"])))
        self.label_22.setText(_translate("Form", "Secs"))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
