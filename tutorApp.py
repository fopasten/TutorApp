"""This module manages selenium scripts backend for TutorApp"""

import locale
import logging
import sys

from ctypes import windll
from json import dump, load
from time import sleep

from PyQt5.QtCore import QRunnable, QThreadPool, Qt, pyqtSlot
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QLabel,
    QLineEdit,
    QTabWidget,
    QApplication,
    QComboBox,
    QTextEdit,
    QPushButton,
    QHBoxLayout,
    QFileDialog,
)

from selenium_scripts import BbScripts

default_lan = windll.kernel32
gui_language = locale.windows_locale[default_lan.GetUserDefaultUILanguage()]

logging.basicConfig(
    filename="./log.txt", level=logging.INFO, format="%(asctime)s - %(message)s"
)

es_ES = {
    "select_lms": "Selecciona Plataforma: ",
    "select_script": "Selecciona Acción:",
    "run": "EJECUTAR",
    "user": "Credenciales",
    "files": "Archivos",
    "about": "Sobre la App",
    "about_content": {
        "tabs_names": {1: "Instrucciones", 2: "Tipos de Archivos"},
        "tab1": "<h3>Instrucciones de uso</h3>"
                "<p>Esta aplicación procesa archivos planos (.txt) para ejecutar acciones "
                "automatizadas en un navegador de manera de evitar el trabajo repetitivo. Es "
                "importante que se carguen los archivos con la estructura correcta y que no se "
                "manipule el navegador mientras se ejecuta el proceso.</p>"
                "<h3>Cómo armar un archivo</h3>"
                "<p>La forma más sencilla es armar directamente un archivo en Excel con la "
                "información correspondiente en cada columna, sin encabezados.</p><p>Luego "
                "se debe copiar la información a un archivo en block de notas y guardarlo "
                'como archivo ".txt".</p><p>Se puede consultar la pestaña de '
                "<b>Formato de Archivos</b> "
                "para conocer más detalles de lo necesario para cada función.</p>",
        "tab2": "<h3>Formato de Archivos</h3>"
                "<h4>Cambio de Rol</h4>"
                "<p>Para los archivos de cambio de rol se debe usar cualquiera de los siguientes "
                "separadores:</p> "
                "<p>ID_CURSO;ID_USUARIO;ROL      (Punto y Coma)<br>"
                "ID_CURSO|ID_USUARIO|ROL     (Pipe)<br>"
                "ID_CURSO&emsp;ID_USUARIO&emsp;ROL       (Tabulación)</p>"
                "<h4>Ajustar Listas</h4>"
                "<p>Para Ajustar listas basta con el NRC del curso en cada linea:</p>"
                "<p>ID_CURSO_1<br>ID_CURSO_2<br>...</p>"
                "<h4>Ajustar Cierre de Curso</h4>"
                "<p>Para ajustar el cierre del curso se debe indicar el NRC del curso y el "
                "indicador de apertura (Y) o cierre (N)</p> "
                "<p>ID_CURSO_1   Y<br>ID_CURSO_2   N</p>",
    },
    "script_options": {
        0: "",
        1: "Cambiar Rol en Curso",
        2: "Ajustar Listas",
        3: "Ajustar Cierre de Curso",
        4: "Enviar Anuncios",
        5: "Contacto Tutoría"
    },
    "bb_user": "Blackboard",
    "bb_user_label": "Ingresa tu usuario y contraseña:",
    "csv_file": "Ruta de Archivo .TXT",
    "browse": "Buscar",
    "select_file": "Seleccionar Archivo",
    "accepted_files": "Archivos soportados (*.txt)",
}

en_US = {
    "select_lms": "Select LMS: ",
    "select_script": "Select Script:",
    "run": "RUN",
    "user": "Credentials",
    "files": "Files",
    "about": "About",
    "about_content": {
        "tabs_names": {1: "Instructions", 2: "File Types"},
        "tab1": "<h3>Usage Instructions</h3>"
                "<p>This app processes flat files (.txt) in order to execute scripts "
                "made to reduce time spent doing repetitive tasks. It's important that the files "
                "that are loaded have the right structure relating to the script that is going to "
                "run and that the browser remains untouched while the script runs.</p>"
                "<h3>How to make a file</h3>"
                "<p>The easiest way to make a file is to put the data in a Excel sheet ensuring "
                "correspondence to each column, without headers</p><p>Once all the data is there "
                'it must be copied into Notepad and saved as ".txt" file.</p>'
                "<p>There's more detail in the <b>File Formatting</b> tab, on how to make "
                "these files.</p>",
        "tab2": "<h3>File Formatting</h3>"
                "<h4>Change Course Role</h4>"
                "<p>For these files any of the following delimiters can be used:</p> "
                "<p>COURSE_ID;USER_ID;ROLE      (Dot and Comma)<br>"
                "COURSE_ID|USER_ID|ROLE     (Pipe)<br>"
                "COURSE_ID&emsp;USER_ID&emsp;ROLE       (Tab)</p>"
                "<h4>Adjust Lists</h4>"
                "<p>In order to Adjust Blackboard list with Banner information only the COURSE_ID "
                "is required:</p> "
                "<p>COURSE_ID_1<br>COURSE_ID_2<br>...</p>"
                "<h4>Adjust Course Closing Date</h4>"
                "<p>To adjust de end date of a course it is required to enter the course_id and "
                "indicate if it must be open (Y) or closed (N)</p>"
                "<p>COURSE_ID_1   Y<br>COURSE_ID_2   N</p>",
    },
    "script_options": {
        0: "",
        1: "Change Course Role",
        2: "Adjust List",
        3: "Adjust Course Ending",
        4: "Post Announcements",
        5: "Post Tutor Info"
    },
    "bb_user": "Blackboard",
    "bb_user_label": "Enter User and Password:",
    "csv_file": "File Path .TXT",
    "browse": "Browse",
    "select_file": "Choose File",
    "accepted_files": "Supported Files (*.txt)",
}


class UNABScripts(QMainWindow):
    """Main Application Window

    Defines shape, icon, name and closing method

    Args:
        QMainWindow ([]): Inherits from QMainWindow Class
    """
    def __init__(self):
        super().__init__()
        self.setGeometry(300, 200, 350, 600)
        self.setFixedSize(350, 600)

        self.setWindowTitle("App Tutores v1.0.4")

        self.setWindowIcon(QIcon("./icon.png"))

        self.threadpool = QThreadPool()

        if gui_language == "en_US":
            self.lang_dict = en_US
        else:
            self.lang_dict = es_ES

        data = None

        try:
            with open("savefile.json", "r") as file:
                data = load(
                    file,
                    object_hook=lambda d: {
                        int(k) if k.lstrip("-").isdigit() else k: v
                        for k, v in d.items()
                    },
                )
        except IOError:
            logging.info("No Such File, creating one at exit")

        self.tabs_widget = TabsWidget(self, data)
        self.setCentralWidget(self.tabs_widget)

        self.show()

    def closeEvent(self, *args, **kwargs):
        """closeEvent overloading to save config data
        """
        data = self.tabs_widget.save_data()
        with open("savefile.json", "w") as file:
            dump(data, file)
        self.threadpool.clear()


class TabsWidget(QWidget):
    """Main Widget

    Args:
        QWidget ([type]): Inherits from QWidget Class
    """
    def __init__(self, parent, savefile=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)

        # Tabs

        self.tabs = QTabWidget()
        self.tab1 = QWidget(self)
        self.tab2 = QWidget(self)
        self.tab3 = QWidget(self)
        self.tab4 = QWidget(self)

        self.threadpool = parent.threadpool

        self.lang_dict = parent.lang_dict

        self.tabs.addTab(self.tab1, "Home")
        self.tabs.addTab(self.tab2, self.lang_dict["user"])
        self.tabs.addTab(self.tab3, self.lang_dict["files"])
        self.tabs.addTab(self.tab4, self.lang_dict["about"])

        self.tab1.layout = QVBoxLayout(self)
        self.tab1.layout.setAlignment(Qt.AlignTop)

        self.tab2.layout = QVBoxLayout(self)
        self.tab2.layout.setAlignment(Qt.AlignTop)

        self.tab3.layout = QVBoxLayout(self)
        self.tab3.layout.setAlignment(Qt.AlignTop)

        self.tab4.layout = QVBoxLayout(self)
        self.tab4.layout.setAlignment(Qt.AlignTop)

        # Set Tab 1

        # Set Logo

        self.banner1 = QLabel(self)
        image_unab = QPixmap("./banner.png")
        self.banner1.setPixmap(image_unab)
        self.banner1.setAlignment(Qt.AlignCenter)
        self.tab1.layout.addWidget(self.banner1, alignment=Qt.AlignTop)

        # CBOX LMS

        self.cboxLMSlayout = QWidget(self)
        self.cboxLMSlayout.layout = QHBoxLayout(self)
        self.cboxLMSLabel = QLabel(self.lang_dict["select_lms"], self)
        self.cboxLMSLabel.setFixedWidth(len(self.lang_dict["select_lms"]) * 6)
        self.cboxLMS = QComboBox(self)
        self.cboxLMS.addItems(["", "Blackboard"])
        self.cboxLMSlayout.layout.addWidget(self.cboxLMSLabel)
        self.cboxLMSlayout.layout.addWidget(self.cboxLMS)
        self.cboxLMSlayout.setLayout(self.cboxLMSlayout.layout)

        self.tab1.layout.addWidget(self.cboxLMSlayout)

        # Connect ComboBox

        self.cboxLMS.currentTextChanged.connect(self.cb_lms_option)

        # CBOX Scripts

        self.cboxScriptlayout = QWidget(self)
        self.cboxScriptlayout.layout = QHBoxLayout(self)
        self.cboxScriptLabel = QLabel(self.lang_dict["select_script"], self)
        self.cboxScriptLabel.setFixedWidth(
            len(self.lang_dict["select_script"]) * 6)
        self.cboxScript = QComboBox(self)
        self.cboxScriptlayout.layout.addWidget(self.cboxScriptLabel)
        self.cboxScriptlayout.layout.addWidget(self.cboxScript)
        self.cboxScriptlayout.setLayout(self.cboxScriptlayout.layout)
        self.tab1.layout.addWidget(self.cboxScriptlayout)
        self.cboxScript.setEnabled(False)

        # Connect ComboBox

        self.cboxScript.currentTextChanged.connect(self.run_script_btn)

        # Output Box

        self.output_box = QTextEdit(self.tab1)
        self.output_box.setReadOnly(True)
        self.output_box.setTextInteractionFlags(Qt.NoTextInteraction)
        self.tab1.layout.addWidget(self.output_box)

        # QPUSH Run
        self.runbtn = QPushButton(self.lang_dict["run"], self)
        self.runbtn.setFixedSize(80, 40)
        self.runbtn.setEnabled(False)

        self.runbtn.pressed.connect(self.exec_script)

        self.tab1.setLayout(self.tab1.layout)

        # Set Tab 2

        self.user_tabs = QTabWidget(self.tab2)
        self.user_tabs.setGeometry(5, 5, 320, 500)

        self.user_bb = QWidget(self.user_tabs)
        self.user_bb.layout = QVBoxLayout(self.user_bb)
        self.user_bb.layout.setAlignment(Qt.AlignTop)

        self.user_tabs.addTab(self.user_bb, self.lang_dict["bb_user"])

        self.tab2.layout.addWidget(self.user_tabs)
        self.tab2.setLayout(self.tab2.layout)

        # Set QLineEdits and QLabels

        self.bb_username_label = QLabel(self.lang_dict["bb_user_label"])
        self.bb_username = QLineEdit(self.user_bb)
        self.bb_pass = QLineEdit(self.user_bb)
        self.bb_pass.setEchoMode(QLineEdit.Password)

        # Set Pass button
        self.bb_pass_btn = QPushButton("👁", self.user_bb)

        self.bb_pass_btn.pressed.connect(self.see_pass)
        self.bb_pass_btn.released.connect(self.hide_pass)

        # Add widgets to layout
        self.user_bb.layout.addWidget(self.bb_username_label)
        self.user_bb.layout.addWidget(self.bb_username)
        self.user_bb.layout.addWidget(self.bb_pass)
        self.user_bb.layout.addWidget(
            self.bb_pass_btn, alignment=Qt.AlignRight)

        # Set layout

        self.user_bb.setLayout(self.user_bb.layout)

        # Set Tab 3

        self.csv_path_lb = QLabel(self.lang_dict["csv_file"], self.tab3)
        self.csv_path = QLineEdit(self.tab3)
        self.csv_path_btn = QPushButton(self.lang_dict["browse"], self.tab3)

        self.tab3.layout.addWidget(self.csv_path_lb)
        self.tab3.layout.addWidget(self.csv_path)
        self.tab3.layout.addWidget(self.csv_path_btn, alignment=Qt.AlignRight)

        self.tab3.setLayout(self.tab3.layout)

        self.csv_path_btn.pressed.connect(self.csv_path_get)

        # self.pack_path_lb = QLabel("Packages Directory:", self.tab3)
        # self.pack_path = QLineEdit(self.tab4)
        # self.pack_path_btn = QPushButton("Browse", self.tab3)
        #
        # self.tab3.layout.addWidget(self.pack_path_lb)
        # self.tab3.layout.addWidget(self.pack_path)
        # self.tab3.layout.addWidget(self.pack_path_btn, alignment=Qt.AlignRight)
        #
        # self.pack_path_btn.pressed.connect(self.pack_path_get)
        #
        # self.dlwd_path_lb = QLabel("Downloads Directory:", self.tab3)
        # self.dlwd_path = QLineEdit(self.tab3)
        # self.dlwd_path_btn = QPushButton("Browse", self.tab3)
        #
        # self.tab3.layout.addWidget(self.dlwd_path_lb)
        # self.tab3.layout.addWidget(self.dlwd_path)
        # self.tab3.layout.addWidget(self.dlwd_path_btn, alignment=Qt.AlignRight)
        #
        # self.dlwd_path_btn.pressed.connect(self.dlwd_path_get)

        # Set Tab 4

        self.tab4.setGeometry(5, 5, 300, 600)

        self.about_tabs = QTabWidget(self.tab4)
        self.about_tabs.setGeometry(5, 5, 320, 500)

        self.about_tab1 = QWidget(self.about_tabs)
        self.about_tab1.layout = QVBoxLayout(self.about_tab1)
        self.about_tab1.layout.setAlignment(Qt.AlignTop)
        self.about_tab2 = QWidget(self.about_tabs)
        self.about_tab2.layout = QVBoxLayout(self.about_tab2)
        self.about_tab2.layout.setAlignment(Qt.AlignTop)

        self.about_tab1_body = QLabel(
            self.lang_dict["about_content"]["tab1"], self.about_tab1
        )
        self.about_tab1_body.setWordWrap(True)
        self.about_tab1_body.setAlignment(Qt.AlignTop)
        self.about_tab1_body.setFixedHeight(600)

        self.about_tab2_body = QLabel(
            self.lang_dict["about_content"]["tab2"], self.about_tab2
        )
        self.about_tab2_body.setWordWrap(True)
        self.about_tab2_body.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.about_tab2_body.setAlignment(Qt.AlignTop)
        self.about_tab2_body.setFixedHeight(600)

        self.about_tab1.layout.addWidget(
            self.about_tab1_body, alignment=Qt.AlignTop)
        self.about_tab1.setLayout(self.about_tab1.layout)
        self.about_tab2.layout.addWidget(
            self.about_tab2_body, alignment=Qt.AlignTop)
        self.about_tab2.setLayout(self.about_tab2.layout)

        self.about_tabs.addTab(
            self.about_tab1, self.lang_dict["about_content"]["tabs_names"][1]
        )
        self.about_tabs.addTab(
            self.about_tab2, self.lang_dict["about_content"]["tabs_names"][2]
        )

        self.tab4.layout.addWidget(self.about_tabs)
        self.tab4.setLayout(self.tab4.layout)

        # Set global Layout

        self.layout.addWidget(self.tabs)
        self.layout.addWidget(self.runbtn, alignment=Qt.AlignRight)

        if savefile is not None:
            self.load_data(savefile)

        self.setLayout(self.layout)

    def cb_lms_option(self, text):
        if text == "Blackboard":
            self.cboxScript.clear()
            self.cboxScript.addItems(self.lang_dict["script_options"].values())
        # elif text == "Moodle":
        #     self.cboxScript.clear()
        #     self.cboxScript.addItems(["", "Download MBZ"])
        else:
            self.cboxScript.clear()
        self.cboxScript.setEnabled(True)

    def run_script_btn(self, text):
        if text == "":
            self.runbtn.setEnabled(False)
        else:
            self.runbtn.setEnabled(True)

    def send_output(self, text):
        self.output_box.insertPlainText(text + "\n")

    def see_pass(self):
        self.bb_pass.setEchoMode(QLineEdit.Normal)

    def hide_pass(self):
        self.bb_pass.setEchoMode(QLineEdit.Password)

    def csv_path_get(self):
        self.csv_path.setText(
            str(
                QFileDialog.getOpenFileName(
                    self.csv_path,
                    self.lang_dict["select_file"],
                    filter=self.lang_dict["accepted_files"],
                    options=QFileDialog.ShowDirsOnly,
                )[0]
            )
        )
        self.csv_path.setToolTip(str(self.csv_path.text()))

    # def pack_path_get(self):
    #     self.pack_path.setText(str(QFileDialog.getExistingDirectory(self.pack_path, "Select Directory")))
    #     self.pack_path.setToolTip(str(self.pack_path.text()))
    #
    # def dlwd_path_get(self):
    #     self.dlwd_path.setText(str(QFileDialog.getExistingDirectory(self.dlwd_path, "Select Directory")))
    #     self.dlwd_path.setToolTip(str(self.dlwd_path.text()))

    def exec_script(self):
        btn_ctrl = Worker(self.wait_click)
        self.threadpool.start(btn_ctrl)
        if (
            self.bb_username.text() == ""
            or self.bb_pass.text() == ""
            or self.csv_path.text() == ""
        ):
            self.send_output(
                "No se ha introducido credenciales o dirección de archivo."
            )
            return
        if self.cboxLMS.currentText() == "Blackboard":
            username = self.bb_username.text()
            password = self.bb_pass.text()
        if self.cboxScript.currentText() == self.lang_dict["script_options"][1]:
            worker = Worker(
                BbScripts,
                username,
                password,
                path=self.csv_path.text(),
                func=1,
                logger=logging,
                output=self.send_output,
            )
        elif self.cboxScript.currentText() == self.lang_dict["script_options"][2]:
            worker = Worker(
                BbScripts,
                username,
                password,
                path=self.csv_path.text(),
                func=2,
                logger=logging,
                output=self.send_output,
            )
        elif self.cboxScript.currentText() == self.lang_dict["script_options"][3]:
            worker = Worker(
                BbScripts,
                username,
                password,
                path=self.csv_path.text(),
                func=3,
                logger=logging,
                output=self.send_output,
            )
        elif self.cboxScript.currentText() == self.lang_dict["script_options"][4]:
            worker = Worker(
                BbScripts,
                username,
                password,
                path=self.csv_path.text(),
                func=4,
                logger=logging,
                output=self.send_output,
            )
        elif self.cboxScript.currentText() == self.lang_dict["script_options"][5]:
            worker = Worker(
                BbScripts,
                username,
                password,
                path=self.csv_path.text(),
                func=5,
                logger=logging,
                output=self.send_output,
            )
        self.threadpool.start(worker)

    def save_data(self):
        return {
            "user": self.bb_username.text(),
            "pass": self.bb_pass.text(),
            "path": self.csv_path.text(),
            "lms": self.cboxLMS.currentText(),
            "script": self.cboxScript.currentText(),
        }

    def load_data(self, file):
        self.bb_username.setText(file["user"])
        self.bb_pass.setText(file["pass"])
        self.csv_path.setText(file["path"])
        self.cboxLMS.setCurrentText(file["lms"])
        self.cboxScript.setCurrentText(file["script"])

    def wait_click(self):
        self.runbtn.setDisabled(True)
        text = self.runbtn.text()
        total = 5
        for number in range(6):
            self.runbtn.setText(text + " (0.{})".format(total - number))
            sleep(0.1)
        self.runbtn.setText(text)
        self.runbtn.setEnabled(True)


class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.function = fn
        self.args = args
        self.kwargs = kwargs
        self.setAutoDelete(True)

    @pyqtSlot()
    def run(self):
        self.function(*self.args, **self.kwargs)
        self.autoDelete()

if __name__ == "__main__":
    app = QApplication([])
    frame = UNABScripts()
    sys.exit(app.exec_())
