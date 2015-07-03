#!/usr/bin/env python
#coding=utf-8

from Tkinter import *
import tkMessageBox

from HHCountLine import HHCountLineClass

class HHApplicationClass(Frame):

    def __init__(self, master=None):
            Frame.__init__(self, master)
            self.pack()
            self.createWidgets()

    def createWidgets(self):

        self.helloLabel = Label(self, text='统计代码行数Demo')
        self.helloLabel.pack()

        self.nameInput = Entry(self,bd = 3,text = '',bg = '#87CEFA')
        self.nameInput.pack()

        self.alertButton = Button(self, text='开始计算', command=self.hello)
        self.alertButton.pack()

        self.quitButton = Button(self, text='退出',activebackground = '#87CEFA', highlightcolor = '#87CEFA',bg = '#87CEFA', command=self.quit)
        self.quitButton.pack()

    def startCaculate(self,filename):
        testLine = HHCountLineClass(filename,self.finishMessage)

    def finishMessage(self,dirr):

        msg = '文件统计结束: \n 文件数: %s  \n 总计： %s 行 \n 实际: %s 行 \n' %(dirr['file'],dirr['all'],dirr['allSource'])
        tkMessageBox.showinfo('Message', msg,command=self.quit)
        

    def hello(self):
        name = self.nameInput.get()
        if  name:
            self.startCaculate(name)
        else :
            name = '请输入目标文件夹路径'
            tkMessageBox.showinfo('Message', '文件目录不能为空')

    
         


		