#!/bin/bash

pyuic4 mainwindow.ui -o ui_mainwindow.py
pyrcc4 res.qrc -o res_rc.py
