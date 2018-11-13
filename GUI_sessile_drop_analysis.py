# -*- coding: utf-8 -*-
"""
GUI for sessile drop analysis. Uses contact_angle_analysis_function.py, which in turn uses edge_detection.py.
"""

import tkinter as tk
import numpy as np
from tkinter import ttk
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from matplotlib import style

LARGE_FONT= ("Verdana", 12)
SMALL_FONT= ("Verdana", 8)
style.use("ggplot")

fig = Figure(figsize=(5,5),dpi=100)
a = fig.add_subplot(111)

def runscript(erfbool,k,II):
    from contact_angle_analysis_function import analysis
    global thetal, thetar, leftspeed, rightspeed, contactpointleft, contactpointright, dropvolume
    thetal, thetar, leftspeed, rightspeed, contactpointleft, contactpointright, dropvolume = analysis(erfbool,k,II)

def plotstuff(typexplot,typeyplot,logxbool,logybool,pxscale,fps):
    x=np.float()
    y=np.float()
    if typexplot==1:
        x=thetal
    elif typexplot==2:
        x=thetar
    elif typexplot==3:
        x=dropvolume*pxscale**3
    elif typexplot==3:
        x=leftspeed*pxscale*fps
    elif typexplot==4:
        x=rightspeed*pxscale*fps
    else:
        print('no x variable set')
    if typeyplot==1:
        y=thetal
    elif typeyplot==2:
        y=thetar
    elif typeyplot==3:
        y=dropvolume
    elif typeyplot==3:
        y=leftspeed
    elif typeyplot==4:
        y=rightspeed
    else:
        print('no y variable set')
    if x.size==1 or y.size==1:
        plt.scatter(x,y)
    else:
        plt.plot(x,y)
    
    if logxbool:
        plt.xscale('log')
    if logybool:
        plt.yscale('log')
    plt.show()

class CAA(tk.Tk):
    def __init__(self,*args,**kwargs):
        tk.Tk.__init__(self,*args,**kwargs)
        container=tk.Frame(self)
        container.pack(side="top", fill="both", expand = True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (StartPage, PageThree):
            frame = F(container,self)
            self.frames[F]=frame
            frame.grid(row=0, column=0,sticky= "nesw")

        self.show_frame(StartPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


def qf(stringtoprint):
    print(stringtoprint)


class StartPage(tk.Frame):

    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)

        label1 = ttk.Label(self, text="File analysis", font=LARGE_FONT)
        label1.grid(row=0, column=1,pady=10,padx=10)

        labelk = ttk.Label(self, text="Amount of pixels from the baseline to fit:", font=SMALL_FONT)
        labelk.grid(row=1, column=1)
        kinput=ttk.Entry(self)
        kinput.grid(row=2, column=1)
        kinput.insert(0, 70)

        labelII = ttk.Label(self, text="Show output every 'x' frames:", font=SMALL_FONT)
        labelII.grid(row=3, column=1)
        IIinput=ttk.Entry(self)
        IIinput.grid(row=4, column=1)
        IIinput.insert(0, 5)

        labelpxscale = ttk.Label(self, text="Pixel size in mm per pixel:", font=SMALL_FONT)
        labelpxscale.grid(row=5, column=1)
        pxscaleinput=ttk.Entry(self)
        pxscaleinput.grid(row=6, column=1)
        pxscaleinput.insert(0, 1)

        labelfps = ttk.Label(self, text="Framerate of source", font=SMALL_FONT)
        labelfps.grid(row=7, column=1)
        fpsinput=ttk.Entry(self)
        fpsinput.grid(row=8, column=1)
        fpsinput.insert(0, 1)

        self.fasterbool = tk.BooleanVar()
        self.fasterbool.set(False)
        checkbox1 = ttk.Checkbutton(self,text="Faster execution (but less precise)",variable=self.fasterbool)
        checkbox1.grid(row=9, column=1)

        button2 = ttk.Button(self,text="Go",command=lambda: runscript(self.fasterbool.get(),int(kinput.get()),int(IIinput.get())))
        button2.grid(row=10, column=1)


        label2 = ttk.Label(self, text="Plot x variable", font=LARGE_FONT)
        label2.grid(row=0,column=2,pady=10,padx=10)
        self.typexplot=tk.IntVar()

        ttk.Radiobutton(self, text="Theta left", variable=self.typexplot, value=1).grid(row=1, column=2)
        ttk.Radiobutton(self, text="Theta right", variable=self.typexplot, value=2).grid(row=2, column=2)
        ttk.Radiobutton(self, text="Volume", variable=self.typexplot, value=3).grid(row=3, column=2)
        ttk.Radiobutton(self, text="Left speed", variable=self.typexplot, value=4).grid(row=4, column=2)
        ttk.Radiobutton(self, text="Right speed", variable=self.typexplot, value=5).grid(row=5, column=2)

        self.logxbool = tk.BooleanVar()
        self.logxbool.set(False)

        checkbox2 = ttk.Checkbutton(self,text="Logaritmic scale",variable=self.logxbool)
        checkbox2.grid(row=6, column=2)
        label3 = ttk.Label(self, text="Plot y variable", font=LARGE_FONT)
        label3.grid(row=0,column=3,pady=10,padx=10)
        self.typeyplot=tk.IntVar()

        ttk.Radiobutton(self, text="Theta left", variable=self.typeyplot, value=1).grid(row=1, column=3)
        ttk.Radiobutton(self, text="Theta right", variable=self.typeyplot, value=2).grid(row=2, column=3)
        ttk.Radiobutton(self, text="Volume", variable=self.typeyplot, value=3).grid(row=3, column=3)
        ttk.Radiobutton(self, text="Left speed", variable=self.typeyplot, value=4).grid(row=4, column=3)
        ttk.Radiobutton(self, text="Right speed", variable=self.typeyplot, value=5).grid(row=5, column=3)

        self.logybool = tk.BooleanVar()
        self.logybool.set(False)
        checkbox2 = ttk.Checkbutton(self,text="Logaritmic scale",variable=self.logybool)
        checkbox2.grid(row=6, column=3)

        button3 = ttk.Button(self,text="Show plot",command=lambda: plotstuff(self.typexplot.get(),self.typeyplot.get(),self.logxbool.get(),self.logybool.get(),np.float(pxscaleinput.get()),np.float(fpsinput.get())))
        button3.grid(row=8,column=3)
        #canvas._tkcanvas.pack()

class PageThree(tk.Frame):
    def main(self):
        self.thetal = np.random.rand(1,1)
    def __init__(self,parent,controller):
        tk.Frame.__init__(self,parent)
        label = ttk.Label(self, text="dummy page, just in case I want to use it later", font=LARGE_FONT)
        label.pack(pady=10,padx=10)


app = CAA()

app.mainloop()
