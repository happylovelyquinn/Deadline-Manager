import os
from round import PaintVar
from PyQt5 import QtCore, QtGui, QtWidgets
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QColor, QBrush, QFont


from main_window_layout import Ui_MainWindow
from datetime import date, datetime
import sqlite3


class Dataset(object):
    def __init__(self):
        # set the database path
        self.path = './data/database.db'
        # create a new table at the first run
        if not os.path.exists(self.path):
            sql = 'create table TaskTable' \
                  '(' \
                  'task_id INTEGER PRIMARY KEY  AUTOINCREMENT, ' \
                  'task_class INTEGER NOT NULL,' \
                  'task_info varchar(30) NOT NULL,' \
                  'start_date varchar(30) NOT NULL,' \
                  'end_date varchar(30) NOT NULL,' \
                  'status INTEGER NOT NULL,' \
                  'user varchar(30) NOT NULL'\
                  ')'
            # connect to the database and execute the sql
            conn = sqlite3.connect(self.path)
            conn.execute(sql)
        else:
            conn = sqlite3.connect(self.path)
        self.conn = conn

    # define a function to insert items into the database
    def insert(self, item_class, item_task, item_start, item_end, status=0):
        # get the name of the currently logged in user
        user = ""
        with open("./user.txt", "r") as f:
            user = f.read()
        # insert current user's task items into the table
        sql = "INSERT INTO TaskTable (task_class ,task_info, start_date, end_date, status, user) VALUES({}, '{}','{}','{}',{},'{}')"\
            .format(item_class, item_task, item_start, item_end, status, user)
        cur = self.conn.cursor()
        try:
            # connect to the database and execute the sql
            cur.execute(sql)
            print('create successfully')
        except Exception as e:
            print(e)
            print('fail to create')
        self.conn.commit()

    # define a function to delete from the database
    def delete(self, task_info):
        # get the name of the currently logged in user
        user = ""
        with open("./user.txt", "r") as f:
            user = f.read()
        # connect to the database and delete current user's task items from table
        self.conn.execute("DELETE FROM TaskTable WHERE task_info = ? and user=?", (task_info, user,))
        self.conn.commit()
        self.close()

    # define a function to read all task items which haven't be completed yet
    def read(self):
        # get the name of the currently logged in user
        user = ""
        with open("./user.txt", "r") as f:
            user = f.read()
        # read current user's task items from table
        sql = 'SELECT * from TaskTable where user=? AND status !=1 AND status !=3'
        # connect to the database and execute the sql
        cur = self.conn.cursor()
        try:
            data = cur.execute(sql, (user,))
            print('read successfully')
            return data
        except Exception as e:
            print(e)
            print('fail to read')
            return None

    # define a function to update status to 1 when the task is completed on time and update to 3 when completed out of the time limit
    def update_status(self, task_info, start_date, end_date):
        # get the name of the currently logged in user
        user = ""
        with open("./user.txt", "r") as f:
            user = f.read()
        # complete on time
        sql1 = "UPDATE TaskTable SET status = 1 WHERE task_info = '{}' AND start_date = '{}' AND end_date = '{}' AND user='{}' AND status !=2" \
            .format(task_info, start_date, end_date, user)
        # complete overtime
        sql2 = "UPDATE TaskTable SET status = 3 WHERE task_info = '{}' AND start_date = '{}' AND end_date = '{}' AND user='{}' AND status =2" \
            .format(task_info, start_date, end_date, user)
        # connect to the database and execute the sql
        cur = self.conn.cursor()
        cur.execute(sql1)
        self.conn.commit()
        cur.execute(sql2)
        self.conn.commit()


    # define a function to update status to 2 when time is out
    def update_status_overdue(self, task_info, start_date, end_date):
        # get the name of the currently logged in user
        user = ""
        with open("./user.txt", "r") as f:
            user = f.read()
        # update status to 2 when time is out
        sql = "UPDATE TaskTable SET status = 2 WHERE task_info = '{}' AND start_date = '{}' AND end_date = '{}' AND user='{}'" \
            .format(task_info, start_date, end_date, user)
        # connect to the database and execute the sql
        cur = self.conn.cursor()
        cur.execute(sql)
        self.conn.commit()

    # define a function to get the data of the total task progress
    def getPercent(self):
        # get the name of the currently logged in user
        user = ""
        with open("./user.txt", "r") as f:
            user = f.read()
        # get quantity of total tasks
        sql="select count(*) from tasktable where user=?"
        # get quantity of tasks completed on time
        sql2="select count(*) from tasktable where status=1 and user=?"
        # get quantity of tasks overdue
        sql3="select count(*) from tasktable where (status=2 or status=3) and user=?"
        # connect to the database and execute the sql
        cur = self.conn.cursor()
        cur2 = self.conn.cursor()
        cur3 = self.conn.cursor()
        percent1=0
        percent2=0
        try:
            data1 = cur.execute(sql, (user,))
            data2 = cur2.execute(sql2, (user,))
            data3 = cur3.execute(sql3, (user,))
            # deal with situations where the total number of tasks is zero
            if (data1!=None):
                all_num=data1.fetchone()[0]
                if(data2!=None):
                    status1_num=data2.fetchone()[0]
                    percent1=(status1_num/all_num)
                if(data3!=None):
                    percent2=(data3.fetchone()[0]/all_num)
            cur3.close()
            cur2.close()
            cur.close()
            return (percent1,percent2)
        except Exception as e:
            print(e)
            print('fail to read')
            return (percent1,percent2)

    # close the database
    def close(self):
        self.conn.close()