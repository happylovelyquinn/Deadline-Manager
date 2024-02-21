import os
import pygame
from PyQt5 import QtCore, QtGui, QtWidgets
import sys
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi
from PyQt5.QtGui import QColor, QBrush, QFont
from db_controller import Dataset
from chart import gantt
from main_window_layout import Ui_MainWindow
from datetime import datetime
import sqlite3
from round import *

# create the main window class
class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        # show the menu bar
        self.menuBar.setNativeMenuBar(False)
        # link 3 buttons to their functions
        self.pushButton_add.clicked.connect(self.add_task)
        self.pushButton_delete.clicked.connect(self.delete_task)
        self.pushButton_complete.clicked.connect(self.mark_task)
        # set the default time for dateTimeEdit widget
        self.dateTimeEdit_start.setDateTime(QtCore.QDateTime.currentDateTime())
        self.dateTimeEdit_end.setDateTime(QtCore.QDateTime.currentDateTime().addSecs(80))

        self.showSadAction = QAction()

        # self.tableWidget_1.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # self.tableWidget_2.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # self.tableWidget_3.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # self.tableWidget_4.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # create a timer
        timer = QtCore.QTimer(self)
        # link the timer to the update function
        timer.timeout.connect(self.deadline_is_coming)
        timer.start(1000)
        self.deadline_is_coming()

        # initialize canvas for round progress bar
        self.percent = PaintVar.percent
        self.percent2 = PaintVar.percent2
        canvas = QtGui.QPixmap(480, 281)
        # set the background color of round progress bar to the same colour as the main window
        canvas.fill(QColor("#DDEDED"))
        self.label_2.setPixmap(canvas)

        # connect to database to get percent data
        dataset = Dataset()
        res = dataset.getPercent()
        PaintVar.percent = res[0] * 100
        PaintVar.percent2 = res[1] * 100
        # execute setPercent function to update present percentage
        self.setPercent()
        dataset.close()

    # define a function to update present percentage
    def setPercent(self):
        self.update()
        self.percent = PaintVar.percent
        self.percent2 = PaintVar.percent2

    # define a function to draw the round progress bar according to present percentage
    # reference: https://blog.csdn.net/weixin_41611054/article/details/103660845
    def paintEvent(self, event):
        rotateAngle = 360 * self.percent / 100
        rotateAngle2 = 360 * self.percent2 / 100
        painter = QtGui.QPainter(self.label_2.pixmap())
        painter.eraseRect(0, 0, 480, 281)
        painter.setRenderHints(QtGui.QPainter.Antialiasing)
        # customize the brush parameters
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QBrush(QColor("#DDEDEE")))
        painter.drawRect(0, 0, 480, 281)
        painter.setBrush(QBrush(QColor("#5F89FF")))
        painter.drawEllipse(PaintVar.left, PaintVar.top, PaintVar.progressR,
                            PaintVar.progressR)
        # Draw the outer circle
        painter.drawEllipse(PaintVar.left + 230, PaintVar.top, PaintVar.progressR, PaintVar.progressR)
        painter.setBrush(QBrush(QColor("#e3ebff")))
        painter.drawEllipse(PaintVar.left + 2, PaintVar.top + 2, PaintVar.progressR - 4,
                            PaintVar.progressR - 4)
        # Draw inner circle
        painter.drawEllipse(PaintVar.left + 232, PaintVar.top + 2, PaintVar.progressR - 4, PaintVar.progressR - 4)
        gradient = QConicalGradient(50, 50, 91)
        gradient.setColorAt(0, QColor("#95BBFF"))
        gradient.setColorAt(1, QColor("#5C86FF"))
        self.pen = QPen()
        self.pen.setBrush(gradient)
        # Set the gradient effect
        self.pen.setWidth(8)
        self.pen.setCapStyle(Qt.RoundCap)
        painter.setPen(self.pen)
        # plot the progresses according to the percentage of completed and overdue respectively
        painter.drawArc(QtCore.QRectF(PaintVar.left + 1, PaintVar.top + 1, PaintVar.progressR - 2, PaintVar.progressR - 2),(90 - 0) * 16, -rotateAngle * 16)
        painter.drawArc(QtCore.QRectF(PaintVar.left + 231, PaintVar.top + 1, PaintVar.progressR - 2, PaintVar.progressR - 2),(90 - 0) * 16, -rotateAngle2 * 16)
        font = QtGui.QFont()
        font.setFamily("Optima")
        font.setPointSize(13)
        painter.setFont(font)
        painter.setPen(QColor("#5481FF"))
        painter.drawText(
            QtCore.QRectF(PaintVar.left + 1, PaintVar.top + 1, PaintVar.progressR - 4, PaintVar.progressR - 4),
            Qt.AlignCenter,
            "%d%%" % self.percent)
        # Show current progress
        painter.drawText(
            QtCore.QRectF(PaintVar.left + 1, PaintVar.top + 120, PaintVar.progressR - 4, PaintVar.progressR - 4),
            Qt.AlignCenter,
            "Successfully \n completed")
        # progress name
        painter.drawText(
            QtCore.QRectF(PaintVar.left + 231, PaintVar.top + 1, PaintVar.progressR - 4, PaintVar.progressR - 4),
            Qt.AlignCenter,
            "%d%%" % self.percent2)
        # Show current progress
        painter.drawText(
            QtCore.QRectF(PaintVar.left + 231, PaintVar.top + 120, PaintVar.progressR - 4, PaintVar.progressR - 4),
            Qt.AlignCenter,
            "Fail to complete \n on time")

        self.update()
        painter.end()

    # update the status to 1 (successful completion) when marking as completed if the task is not overdue
    def mark_task(self):

        playsound('voice/rick-congrats.wav')

        if self.tableWidget_1.selectedItems() != []:
            # get the selected information
            task_info = self.tableWidget_1.selectedItems()[0].text()
            start_date = self.tableWidget_1.selectedItems()[1].text()
            end_date = self.tableWidget_1.selectedItems()[2].text()
            # update status in the database
            dataset = Dataset()
            dataset.update_status(task_info, start_date, end_date)
            dataset.close()
            # remove the task that has been completed from the to-do list
            self.tableWidget_1.removeRow(self.tableWidget_1.currentRow())

        # the same for the other 3 table widgets

        elif self.tableWidget_2.selectedItems() != []:
            task_info = self.tableWidget_2.selectedItems()[0].text()
            start_date = self.tableWidget_2.selectedItems()[1].text()
            end_date = self.tableWidget_2.selectedItems()[2].text()
            dataset = Dataset()
            dataset.update_status(task_info, start_date, end_date)
            dataset.close()
            self.tableWidget_2.removeRow(self.tableWidget_2.currentRow())
        elif self.tableWidget_3.selectedItems() != []:
            task_info = self.tableWidget_3.selectedItems()[0].text()
            start_date = self.tableWidget_3.selectedItems()[1].text()
            end_date = self.tableWidget_3.selectedItems()[2].text()
            dataset = Dataset()
            dataset.update_status(task_info, start_date, end_date)
            dataset.close()
            self.tableWidget_3.removeRow(self.tableWidget_3.currentRow())
        elif self.tableWidget_4.selectedItems() != []:
            task_info = self.tableWidget_4.selectedItems()[0].text()
            start_date = self.tableWidget_4.selectedItems()[1].text()
            end_date = self.tableWidget_4.selectedItems()[2].text()
            dataset = Dataset()
            dataset.update_status(task_info, start_date, end_date)
            dataset.close()
            self.tableWidget_4.removeRow(self.tableWidget_4.currentRow())

        # update the round progress bar in the overview section to reflect the completion rate
        dataset = Dataset()
        res = dataset.getPercent()
        PaintVar.percent = res[0] * 100
        PaintVar.percent2 = res[1] * 100
        self.setPercent()
        dataset.close()

    # initialize the interface and display the data
    def show_data(self):
        # update the round progress after login
        if(PaintVar.userLogin):
            # set the parameters needed for the round progress bar function
            dataset = Dataset()
            res = dataset.getPercent()
            PaintVar.percent = res[0] * 100
            PaintVar.percent2 = res[1] * 100
            # update percentages needed
            self.setPercent()
            dataset.close()
            # execute only once after login
            PaintVar.userLogin=False

        # update the to-do list
        dataset = Dataset()
        item_list = dataset.read()
        # execute when user's task list isn't empty
        if(item_list!=None):
            for item in item_list:
                # get task items in item_list
                item_class, item_task, item_start, item_end, status = item[1], item[2], item[3], item[4], item[5]
                # display task items in to-do list with the corresponding priority
                if item_class == 1:
                    row = self.tableWidget_1.rowCount()
                    self.tableWidget_1.insertRow(row)
                    item = QTableWidgetItem(item_task)
                    self.tableWidget_1.setItem(row, 0, item)
                    item = QTableWidgetItem(item_start)
                    self.tableWidget_1.setItem(row, 2, item)
                    item = QTableWidgetItem(item_end)
                    self.tableWidget_1.setItem(row, 3, item)

                # the same for the other 3 table widgets
                elif item_class == 2:
                    row = self.tableWidget_2.rowCount()
                    self.tableWidget_2.insertRow(row)
                    item = QTableWidgetItem(item_task)
                    self.tableWidget_2.setItem(row, 0, item)
                    item = QTableWidgetItem(item_start)
                    self.tableWidget_2.setItem(row, 2, item)
                    item = QTableWidgetItem(item_end)
                    self.tableWidget_2.setItem(row, 3, item)
                elif item_class == 3:
                    row = self.tableWidget_3.rowCount()
                    self.tableWidget_3.insertRow(row)
                    item = QTableWidgetItem(item_task)
                    self.tableWidget_3.setItem(row, 0, item)
                    item = QTableWidgetItem(item_start)
                    self.tableWidget_3.setItem(row, 2, item)
                    item = QTableWidgetItem(item_end)
                    self.tableWidget_3.setItem(row, 3, item)
                else:
                    row = self.tableWidget_4.rowCount()
                    self.tableWidget_4.insertRow(row)
                    item = QTableWidgetItem(item_task)
                    self.tableWidget_4.setItem(row, 0, item)
                    item = QTableWidgetItem(item_start)
                    self.tableWidget_4.setItem(row, 2, item)
                    item = QTableWidgetItem(item_end)
                    self.tableWidget_4.setItem(row, 3, item)
            print()

    # define the add task function
    def add_task(self):

        # get user entered item
        item_task = self.lineEdit_task.text()
        priority = self.comboBox_priority.currentText()
        start_date_q = self.dateTimeEdit_start.dateTime()
        end_date_q = self.dateTimeEdit_end.dateTime()

        # convert the time to string to store in the database
        item_start = start_date_q.toString('yyyy-MM-dd hh:mm:ss')
        item_end = end_date_q.toString('yyyy-MM-dd hh:mm:ss')

        # convert the QDateTime type in PyQt5 to integer
        # it is the number of seconds of the period from 1970-1-1 00:00:00 to the time point)
        pro_min = start_date_q.toTime_t()
        pro_max = end_date_q.toTime_t()
        # get current datetime
        now_q = QtCore.QDateTime.currentDateTime()
        now_int = now_q.toTime_t()

        # set up the progress bar
        time_used_visualisation = QtWidgets.QProgressBar(self.centralwidget)
        # the min value is the start time and the max value is the deadline
        time_used_visualisation.setRange(pro_min, pro_max)
        # let the progress bar shows how much has been used (from start time to current time)
        time_used_visualisation.setProperty("value", now_int)

        # add entered item in the table with the corresponding priority
        if priority == '1 (Important & Urgent)':
            row = self.tableWidget_1.rowCount()
            self.tableWidget_1.insertRow(row)
            item = QTableWidgetItem(item_task)
            self.tableWidget_1.setItem(row, 0, item)
            item = QTableWidgetItem(item_start)
            self.tableWidget_1.setItem(row, 2, item)
            item = QTableWidgetItem(item_end)
            self.tableWidget_1.setItem(row, 3, item)
            self.tableWidget_1.setCellWidget(row, 1, time_used_visualisation)

            # add into the database
            item_class = 1
            dataset = Dataset()
            dataset.insert(item_class, item_task, item_start, item_end)
            dataset.close()

        # the same for the other 3 table widgets
        elif priority == "2 (Important & Not Urgent)":
            row = self.tableWidget_2.rowCount()
            self.tableWidget_2.insertRow(row)
            item = QTableWidgetItem(item_task)
            self.tableWidget_2.setItem(row, 0, item)
            item = QTableWidgetItem(item_start)
            self.tableWidget_2.setItem(row, 2, item)
            item = QTableWidgetItem(item_end)
            self.tableWidget_2.setItem(row, 3, item)
            self.tableWidget_2.setCellWidget(row, 1, time_used_visualisation)

            item_class = 2
            dataset = Dataset()
            dataset.insert(item_class, item_task, item_start, item_end)
            dataset.close()

        elif priority == "3 (Not Important & Urgent)":
            row = self.tableWidget_3.rowCount()
            self.tableWidget_3.insertRow(row)
            item = QTableWidgetItem(item_task)
            self.tableWidget_3.setItem(row, 0, item)
            item = QTableWidgetItem(item_start)
            self.tableWidget_3.setItem(row, 2, item)
            item = QTableWidgetItem(item_end)
            self.tableWidget_3.setItem(row, 3, item)
            self.tableWidget_3.setCellWidget(row, 1, time_used_visualisation)

            item_class = 3
            dataset = Dataset()
            dataset.insert(item_class, item_task, item_start, item_end)
            dataset.close()

        else:
            row = self.tableWidget_4.rowCount()
            self.tableWidget_4.insertRow(row)
            item = QTableWidgetItem(item_task)
            self.tableWidget_4.setItem(row, 0, item)
            item = QTableWidgetItem(item_start)
            self.tableWidget_4.setItem(row, 2, item)
            item = QTableWidgetItem(item_end)
            self.tableWidget_4.setItem(row, 3, item)
            self.tableWidget_4.setCellWidget(row, 1, time_used_visualisation)

            item_class = 4
            dataset = Dataset()
            dataset.insert(item_class, item_task, item_start, item_end)
            dataset.close()

        # update the round progress bar in the overview section
        dataset = Dataset()
        res = dataset.getPercent()
        PaintVar.percent = res[0] * 100
        PaintVar.percent2 = res[1] * 100
        self.setPercent()
        dataset.close()
        # clear item entry
        item = self.lineEdit_task.setText("")

    # define the delete task function
    def delete_task(self):
        if self.tableWidget_1.selectedItems() != []:
            # get user deleted item
            task_info = self.tableWidget_1.selectedItems()[0].text()
            dataset = Dataset()
            # delete the record form the database
            dataset.delete(task_info)
            dataset.close()

        # the same for the other 3 table widgets
        elif self.tableWidget_2.selectedItems() != []:
            task_info = self.tableWidget_2.selectedItems()[0].text()
            dataset = Dataset()
            dataset.delete(task_info)
            dataset.close()
        elif self.tableWidget_3.selectedItems() != []:
            task_info = self.tableWidget_3.selectedItems()[0].text()
            dataset = Dataset()
            dataset.delete(task_info)
            dataset.close()
        elif self.tableWidget_4.selectedItems() != []:
            task_info = self.tableWidget_4.selectedItems()[0].text()
            dataset = Dataset()
            dataset.delete(task_info)
            dataset.close()

        # remove the task from the to-do list table
        self.tableWidget_1.removeRow(self.tableWidget_1.currentRow())
        self.tableWidget_2.removeRow(self.tableWidget_2.currentRow())
        self.tableWidget_3.removeRow(self.tableWidget_3.currentRow())
        self.tableWidget_4.removeRow(self.tableWidget_4.currentRow())

        # update the round progress bar in the overview section
        dataset = Dataset()
        res=dataset.getPercent()
        dataset.close()
        PaintVar.percent=res[0]*100
        PaintVar.percent2=res[1]*100
        self.setPercent()
        print("update")

    # define the update function
    def deadline_is_coming(self):
        # update the gantt chart
        gantt()
        pixmap = QPixmap('./images/gantt.jpeg')
        self.label_gantt_chart.setPixmap(pixmap)
        self.label_gantt_chart.setScaledContents(True)
        # update each task record
        number_of_rows1 = self.tableWidget_1.rowCount()
        for row in range(number_of_rows1):
            # get the existing information
            task_info =self.tableWidget_1.item(row, 0).text()
            start = self.tableWidget_1.item(row, 2).text()
            # convert string type to datetime type
            start_time = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
            end = self.tableWidget_1.item(row, 3).text()
            end_time = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
            now_q = QtCore.QDateTime.currentDateTime()
            now = now_q.toString('yyyy-MM-dd hh:mm:ss')
            now_time = datetime.strptime(now, '%Y-%m-%d %H:%M:%S')

            # calculate the percentage of time used
            percent_used = (now_time - start_time).total_seconds() / (end_time - start_time).total_seconds()

            # create a progress bar with range form 1 to 100
            time_used_visualisation = QtWidgets.QProgressBar(self.centralwidget)
            time_used_visualisation.setRange(1, 100)

            if end_time == now_time:
                playsound('voice/rick-sad.wav')
                self.showSadAction.activate(QtWidgets.QAction.Trigger)
            # judge whether the task is overdue
            if percent_used <= 1:
                # update the progress bar
                time_used_visualisation.setProperty("value", percent_used*100)
                self.tableWidget_1.setCellWidget(row, 1, time_used_visualisation)
                # make the words of task description become redder as the deadline approaches to remind the user
                self.tableWidget_1.item(row, 0).setForeground(QBrush(QColor(230*percent_used, 50, 50)))
                # make the words of task description become larger as the deadline approaches to remind the user
                self.tableWidget_1.item(row, 0).setFont(QFont('Optima', 11 + 7 * percent_used))
            elif percent_used > 1:
                # set the value for the progress as 100% (all time has been used up)
                time_used_visualisation.setProperty("value", 100)
                self.tableWidget_1.setCellWidget(row, 1, time_used_visualisation)
                # set the font of task description as the reddest and largest
                self.tableWidget_1.item(row, 0).setForeground(QBrush(QColor(230, 50, 50)))
                self.tableWidget_1.item(row, 0).setFont(QFont('Optima', 11 + 7))
                # update the status as 2 (overdue and uncompleted)
                dataset = Dataset()
                dataset.update_status_overdue(task_info, start, end)
                # update the round progress bar in the overview section to reflect the increased failure rate
                res = dataset.getPercent()
                PaintVar.percent = res[0] * 100
                PaintVar.percent2 = res[1] * 100
                self.setPercent()
                dataset.close()

        # the same for the other 3 table widgets
        number_of_rows2 = self.tableWidget_2.rowCount()
        for row in range(number_of_rows2):
            task_info = self.tableWidget_2.item(row, 0).text()
            start = self.tableWidget_2.item(row, 2).text()
            start_time = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
            end = self.tableWidget_2.item(row, 3).text()
            end_time = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
            now_q = QtCore.QDateTime.currentDateTime()
            now = now_q.toString('yyyy-MM-dd hh:mm:ss')
            now_time = datetime.strptime(now, '%Y-%m-%d %H:%M:%S')
            percent_used = (now_time - start_time).total_seconds() / (end_time - start_time).total_seconds()
            time_used_visualisation = QtWidgets.QProgressBar(self.centralwidget)
            time_used_visualisation.setRange(1, 100)
            if end_time == now_time:
                playsound('voice/rick-sad.wav')
                self.showSadAction.activate(QtWidgets.QAction.Trigger)
            if percent_used <= 1:
                time_used_visualisation.setProperty("value", percent_used * 100)
                self.tableWidget_2.setCellWidget(row, 1, time_used_visualisation)
                self.tableWidget_2.item(row, 0).setForeground(QBrush(QColor(230 * percent_used, 50, 50)))
                self.tableWidget_2.item(row, 0).setFont(QFont('Optima', 11 + 7 * percent_used))
            else:
                time_used_visualisation.setProperty("value", 100)
                self.tableWidget_2.setCellWidget(row, 1, time_used_visualisation)
                self.tableWidget_2.item(row, 0).setForeground(QBrush(QColor(230, 50, 50)))
                self.tableWidget_2.item(row, 0).setFont(QFont('Optima', 11 + 7))
                dataset = Dataset()
                dataset.update_status_overdue(task_info, start, end)
                res = dataset.getPercent()
                PaintVar.percent = res[0] * 100
                PaintVar.percent2 = res[1] * 100
                self.setPercent()
                dataset.close()

        number_of_rows3 = self.tableWidget_3.rowCount()
        for row in range(number_of_rows3):
            task_info = self.tableWidget_3.item(row, 0).text()
            start = self.tableWidget_3.item(row, 2).text()
            start_time = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
            end = self.tableWidget_3.item(row, 3).text()
            end_time = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
            now_q = QtCore.QDateTime.currentDateTime()
            now = now_q.toString('yyyy-MM-dd hh:mm:ss')
            now_time = datetime.strptime(now, '%Y-%m-%d %H:%M:%S')
            percent_used = (now_time - start_time).total_seconds() / (end_time - start_time).total_seconds()
            time_used_visualisation = QtWidgets.QProgressBar(self.centralwidget)
            time_used_visualisation.setRange(1, 100)
            if end_time == now_time:
                playsound('voice/rick-sad.wav')
                self.showSadAction.activate(QtWidgets.QAction.Trigger)
            if percent_used <= 1:
                time_used_visualisation.setProperty("value", percent_used * 100)
                self.tableWidget_3.setCellWidget(row, 1, time_used_visualisation)
                self.tableWidget_3.item(row, 0).setForeground(QBrush(QColor(255 * percent_used, 0, 0)))
                self.tableWidget_3.item(row, 0).setFont(QFont('Optima', 13 + 7 * percent_used))
            elif percent_used > 1:
                time_used_visualisation.setProperty("value", 100)
                self.tableWidget_3.setCellWidget(row, 1, time_used_visualisation)
                self.tableWidget_3.item(row, 0).setForeground(QBrush(QColor(255, 0, 0)))
                self.tableWidget_3.item(row, 0).setFont(QFont('Optima', 13 + 7))
                dataset = Dataset()
                dataset.update_status_overdue(task_info, start, end)
                res = dataset.getPercent()
                PaintVar.percent = res[0] * 100
                PaintVar.percent2 = res[1] * 100
                self.setPercent()
                dataset.close()

            number_of_rows4 = self.tableWidget_4.rowCount()
            for row in range(number_of_rows4):
                task_info = self.tableWidget_4.item(row, 0).text()
                start = self.tableWidget_4.item(row, 2).text()
                start_time = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
                end = self.tableWidget_4.item(row, 3).text()
                end_time = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
                now_q = QtCore.QDateTime.currentDateTime()
                now = now_q.toString('yyyy-MM-dd hh:mm:ss')
                now_time = datetime.strptime(now, '%Y-%m-%d %H:%M:%S')
                percent_used = (now_time - start_time).total_seconds() / (end_time - start_time).total_seconds()
                time_used_visualisation = QtWidgets.QProgressBar(self.centralwidget)
                time_used_visualisation.setRange(1, 100)
                if end_time == now_time:
                    playsound('voice/rick-sad.wav')
                    self.showSadAction.activate(QtWidgets.QAction.Trigger)
                if percent_used <= 1:
                    time_used_visualisation.setProperty("value", percent_used * 100)
                    self.tableWidget_4.setCellWidget(row, 1, time_used_visualisation)
                    self.tableWidget_4.item(row, 0).setForeground(QBrush(QColor(255 * percent_used, 0, 0)))
                    self.tableWidget_4.item(row, 0).setFont(QFont('Optima', 13 + 7 * percent_used))
                elif percent_used > 1:
                    time_used_visualisation.setProperty("value", 100)
                    self.tableWidget_4.setCellWidget(row, 1, time_used_visualisation)
                    self.tableWidget_4.item(row, 0).setForeground(QBrush(QColor(255, 0, 0)))
                    self.tableWidget_4.item(row, 0).setFont(QFont('Optima', 13 + 7))
                    dataset = Dataset()
                    dataset.update_status_overdue(task_info, start, end)
                    res = dataset.getPercent()
                    PaintVar.percent = res[0] * 100
                    PaintVar.percent2 = res[1] * 100
                    self.setPercent()
                    dataset.close()

    # write a function to clear all contents from the table
    def clear(self):
        rows = self.tableWidget_1.rowCount()
        for row in range(rows):
            self.tableWidget_1.removeRow(row)
        rows = self.tableWidget_2.rowCount()
        for row in range(rows):
            self.tableWidget_2.removeRow(row)
        rows = self.tableWidget_3.rowCount()
        for row in range(rows):
            self.tableWidget_3.removeRow(row)
        rows = self.tableWidget_4.rowCount()
        for row in range(rows):
            self.tableWidget_4.removeRow(row)

'''播放音乐'''
def playsound(path):
    pygame.mixer.init()
    sound = pygame.mixer.Sound(path)
    sound.play(0)


# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     myWin = MainWindow()
#     focus_matrix = FocusMatrix()
#     myWin.actionFocus_Matrix.triggered.connect(focus_matrix.show)
#     myWin.show()
#     sys.exit(app.exec_())