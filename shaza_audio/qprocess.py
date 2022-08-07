# -*- coding: utf-8 -*-
"""
Created on Tue Jun  1 12:37:28 2021

@author: sepehr ghaffarzadegan

"""


import sys

def main():
    from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QPlainTextEdit,
                                QVBoxLayout, QWidget)
    from PyQt5.QtCore import QProcess
    
    
    class MainWindow(QMainWindow):
    
        def __init__(self):
            super().__init__()
            title = "Shazam project"
      
            # set the title
            self.setWindowTitle(title)
            self.p = None
            self.commands = {
                    'record':'recognize-from-microphone.py', 
                    'collect': 'collect-fingerprints-of-songs.py',
                    'stats' : 'get-database-stat.py',
                    'reset' : 'reset-database.py'
                    }
            
            self.record_btn = QPushButton("Record")
            self.rest_btn = QPushButton("Reset Database")
            self.stats_btn = QPushButton("Database Stats")
            self.collect_btn = QPushButton("Collect Songs")

            self.record_btn.pressed.connect(lambda: self.start_process('record'))
            self.rest_btn.pressed.connect(lambda: self.start_process('reset'))
            self.stats_btn.pressed.connect(lambda: self.start_process('stats'))
            self.collect_btn.pressed.connect(lambda: self.start_process('collect'))

            self.text = QPlainTextEdit()
            self.text.setReadOnly(True)
            
            l = QVBoxLayout()
            l.addWidget(self.record_btn)
            l.addWidget(self.text)
            
            l.addWidget(self.collect_btn)
            l.addWidget(self.stats_btn)
            l.addWidget(self.rest_btn)
    
            w = QWidget()
            w.setLayout(l)
            self.setCentralWidget(w)
    
        def message(self, s):
            self.text.appendPlainText(s)
    
        def start_process(self, btn_command):
            if self.p is None:  # No process running.
                self.message("Start "+ btn_command)
                self.p = QProcess()  # Keep a reference to the QProcess (e.g. on self) while it's running.
                self.p.readyReadStandardOutput.connect(self.handle_stdout)
                self.p.readyReadStandardError.connect(self.handle_stderr)
                self.p.stateChanged.connect(self.handle_state)
                self.p.finished.connect(self.process_finished)  # Clean up once complete.
                self.p.start("python", [self.commands[btn_command]])
    
        def handle_stderr(self):
            data = self.p.readAllStandardError()
            stderr = bytes(data).decode("utf8")
            self.message(stderr)
    
        def handle_stdout(self):
            data = self.p.readAllStandardOutput()
            stdout = bytes(data).decode("utf8")
            self.message(stdout)
    
        def handle_state(self, state):
            states = {
                QProcess.NotRunning: 'Not running',
                QProcess.Starting: 'Starting',
                QProcess.Running: 'Running',
            }
            state_name = states[state]
            self.message(f"State changed: {state_name}")
    
        def process_finished(self):
            self.message("Recording finished.")
            self.p = None
    
    
    
    w = 500; h = 500

    app = QApplication(sys.argv)
    
    main = MainWindow()
    main.resize(w, h)

    main.show()
    QApplication.setQuitOnLastWindowClosed(True)
    app.exec_()
    app.quit()

if __name__ in ['__main__']:
    app = main()
