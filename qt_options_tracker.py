import sys
import json
from PyQt5.QtWidgets import * 
from PyQt5.QtGui import * 
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import yfinance as yf
import os
from math import *
from black_scholes import *
import qdarkstyle

with open("/home/eric/projects/options_tracker/json/20211126SOXLIB1_results.json","r") as f:
    result = json.load(f)

with open("/home/eric/projects/options_tracker/json/20211126ADSKSP1.json","r") as f:
    config = json.load(f)

with open("/home/eric/projects/options_tracker/json/20211126SOXLIB1_plan.json","r") as f:
    description = json.load(f)

iter_par = config["0"]
strat = result["strat"]
sum = result["sum"]
zeros = result["zeros"]
pos = result["pos"]
neg = result["neg"]
percent = result["percent"]
index = []
index1 = []
index_num1 = iter_par["start"]
index_num = iter_par["start"]
increment = (iter_par["end"] - iter_par["start"])/len(sum)
for i in range(len(sum) + 1): 
    index.append(index_num)
    index_num = index_num + increment

for i in range(len(sum)): 
    index1.append(index_num1)
    index_num1 = index_num1 + increment

# Format
# "1":{
#     "name":         "IBM",
#     "strategy":     "Iron Butterfly",
#     "group:":       "20211105IBMIB1",
#     "strike":       134,
#     "dis_rate":     0.016,
#     "volatility":   0.202,
#     "time":         0.030136,
#     "exec_price":   1.3,
#     "PC":           1,
#     "b/s":          1,
#     "qty":          200
# },

class Window(QWidget):
    def __init__(self):

        # Data
        breakeven_price = []
        max_loss = []
        strike = []
        r = 0.0011
        sigma = 0.5349
        temp_delta = []
        temp_gamma = []
        temp_theta = []
        temp_vega = []
        time_to_expiry = []
        exec_price = []
        PC = []
        bs = []
        stock_price = 322.5
        for i in range(len(config)-1):
            if config[str(i+1)]["O/S"] == 1:
                strike.append(config[str(i+1)]["strike"])
                if str(config[str(i+1)]["PC"]) == "0" and str(config[str(i+1)]["b/s"]) == "1":
                    breakeven_price.append(float(config[str(i+1)]["exec_price"]) + strike[i])
                elif str(config[str(i+1)]["PC"]) == "1" and str(config[str(i+1)]["b/s"]) == "1":
                    breakeven_price.append(strike[i] - float(config[str(i+1)]["exec_price"]))
                elif str(config[str(i+1)]["PC"]) == "0" and str(config[str(i+1)]["b/s"]) == "0":
                    breakeven_price.append(strike[i] + float(config[str(i+1)]["exec_price"]))
                elif str(config[str(i+1)]["PC"]) == "1" and str(config[str(i+1)]["b/s"]) == "0":
                    breakeven_price.append(strike[i] - float(config[str(i+1)]["exec_price"]))
                time_to_expiry.append(config[str(i+1)]["time"])
                PC.append(config[str(i+1)]["PC"])
                bs.append(config[str(i+1)]["b/s"])
                if str(config[str(i+1)]["PC"]) == "0" and str(config[str(i+1)]["b/s"]) == "1":
                    max_loss.append(float(config[str(i+1)]["exec_price"]))
                elif str(config[str(i+1)]["PC"]) == "1" and str(config[str(i+1)]["b/s"]) == "1":
                    max_loss.append(float(config[str(i+1)]["exec_price"]))
                elif str(config[str(i+1)]["PC"]) == "0" and str(config[str(i+1)]["b/s"]) == "0":
                    max_loss.append("infinity")
                elif str(config[str(i+1)]["PC"]) == "1" and str(config[str(i+1)]["b/s"]) == "0":
                    max_loss.append("infinity")
                temp_delta.append(delta(stock_price,strike[i],r,sigma,time_to_expiry[i],PC[i],bs[i]))
                temp_gamma.append(gamma(stock_price,strike[i],r,sigma,time_to_expiry[i],PC[i],bs[i]))
                temp_theta.append(theta(stock_price,strike[i],r,sigma,time_to_expiry[i],PC[i],bs[i]))
                temp_vega.append(vega(stock_price,strike[i],r,sigma,time_to_expiry[i],PC[i],bs[i]))
                exec_price.append(config[str(i+1)]["exec_price"])
            elif config[str(i+1)]["O/S"] == 0:
                breakeven_price.append(0)
                strike.append(0)
                time_to_expiry.append(0)
                PC.append(0)
                bs.append(0)
                max_loss.append(0)
                temp_delta.append(0)
                temp_gamma.append(0)
                temp_theta.append(0)
                temp_vega.append(0)
                exec_price.append(0)

        super().__init__()
        self.setWindowTitle("Options Tracker")
        
        # Create a QVBoxLayout instance
        layout = QHBoxLayout()
        self.setLayout(layout)

        # Create the stacked layout
        self.stackedLayout = QStackedLayout()

        # Create the first summary page

        self.page1 = QWidget()
        self.page1layout = QVBoxLayout()

            # Set Title
        temp_str = str(config["1"]["group:"])
        self.page1title = QLabel(str(temp_str))
        self.page1title.setFont(QFont("Arial",20))
        self.page1layout.addWidget(self.page1title)

            # Graphing
        self.page1horizontal = QHBoxLayout()
        self.page1graph = pg.PlotWidget()
        self.page1horizontal.addWidget(self.page1graph)
        pen = pg.mkPen(color=(255,255,255),width=5)
        self.page1graph.setLabel('left',"Profit/Loss")
        self.page1graph.setLabel('bottom','Stock_Price')
        # self.page1graph.setBackground('w')
        self.page1graph.plot(index1,sum,pen=pen)

            # Data and Variable Declarations
        self.page1deltalabel = 0
        self.page1gammalabel = 0
        self.page1thetalabel = 0
        self.page1vegalabel = 0
        temp_max_gain = np.amax(percent)
        temp_max_loss = np.amin(percent)
        temp_strike = strike
        temp_strike.sort()
        bep = []
        # bep = bepoint(sum,strike,config,r,sigma,increment)
        stratdelta = self.sumarr(temp_delta)
        stratgamma = self.sumarr(temp_gamma)
        strattheta = self.sumarr(temp_theta)
        stratvega = self.sumarr(temp_vega)
        w_prob = []
        # for i in range(len(bep)):
        #     w_prob.append(black_scholes_method(stock_price,bep[i],r,sigma,config["4"]["time"]))
            # w_prob.append(1 - cdf(0.001111481,0.55,1))

        self.page1w_problabel = []
        self.page1w_probvaluelabel = []
            # Values to Keep Track of (page1horizontal)
        self.page1values = QGridLayout()
        self.labelbep = []
        self.bepdisplay = []
        for i in range(len(bep)):
            self.labelbep.append(QLabel("Breakeven_Point:"))
        self.page1labelmaxloss = QLabel("Max_Loss:")
        self.page1labelmaxgain = QLabel("Max_Gain:")
        self.page1deltalabel = QLabel("Strategy_Delta:")
        self.page1gammalabel = QLabel("Strategy_Gamma:")
        self.page1thetalabel = QLabel("Strategy_Theta:")
        self.page1vegalabel = QLabel("Strategy_Vega:")
        for i in range(len(bep)):
            temp_string = "P(X >= Breakeven Point" + " " + str(i) + " " + ")"
            self.page1w_problabel.append(QLabel(str(temp_string)))

        for i in range(len(bep)):
            self.bepdisplay.append(QLabel(str(bep[i])))
        self.page1maxlossvalue = QLabel(str(temp_max_loss))
        self.page1maxgainvalue = QLabel(str(temp_max_gain))
        self.page1deltavalue = QLabel(str(stratdelta))
        self.page1gammavalue = QLabel(str(stratgamma))
        self.page1thetavalue = QLabel(str(strattheta))
        self.page1vegavalue = QLabel(str(stratvega))
        for i in range(len(bep)):
            self.page1w_probvaluelabel.append(QLabel(str(w_prob[i])))

        for i in range(len(bep)):
            self.page1values.addWidget(self.labelbep[i],i,0)
        self.page1values.addWidget(self.page1labelmaxloss,len(bep) + 1,0)
        self.page1values.addWidget(self.page1labelmaxgain,len(bep) + 2,0)
        self.page1values.addWidget(self.page1deltalabel,len(bep) + 3,0)
        self.page1values.addWidget(self.page1gammalabel,len(bep) + 4,0)
        self.page1values.addWidget(self.page1thetalabel,len(bep) + 5,0)
        self.page1values.addWidget(self.page1vegalabel,len(bep) + 6,0)
        for i in range(len(bep)):
            self.page1values.addWidget(self.page1w_problabel[i],len(bep) + 7 + i,0)

        for i in range(len(bep)):
            self.page1values.addWidget(self.bepdisplay[i],i,1)
        self.page1values.addWidget(self.page1maxlossvalue,len(bep) + 1,1)
        self.page1values.addWidget(self.page1maxgainvalue,len(bep) + 2,1)
        self.page1values.addWidget(self.page1deltavalue,len(bep) + 3,1)
        self.page1values.addWidget(self.page1gammavalue,len(bep) + 4,1)
        self.page1values.addWidget(self.page1thetavalue,len(bep) + 5,1)
        self.page1values.addWidget(self.page1vegavalue,len(bep) + 6,1)
        for i in range(len(bep)):
            self.page1values.addWidget(self.page1w_probvaluelabel[i],len(bep) + 7 + i,1)

            # Strategy Description (page1layout)
        self.strategydescriptionlayout = QGridLayout()
        self.string_description = description["description"]
        self.string_entrance_condition = description["entrance_condition"]
        self.string_exit_condition = description["exit_condition"]

        self.page1stratlabel1 = QLabel("Strategy Description:")
        self.page1stratlabel2 = QLabel("Entrance Condition:")
        self.page1stratlabel3 = QLabel("Exit Condition:")

        self.strategydescriptionlayout.addWidget(self.page1stratlabel1,0,0)
        self.strategydescriptionlayout.addWidget(self.page1stratlabel2,1,0)
        self.strategydescriptionlayout.addWidget(self.page1stratlabel3,2,0)

        self.labeldescription = QLabel(str(self.string_description))
        self.labelentrance = QLabel(str(self.string_entrance_condition))
        self.labelexit = QLabel(str(self.string_exit_condition))

        self.strategydescriptionlayout.addWidget(self.labeldescription,0,1)
        self.strategydescriptionlayout.addWidget(self.labelentrance,1,1)
        self.strategydescriptionlayout.addWidget(self.labelexit,2,1)

            # Set Layout
        self.page1horizontal.addLayout(self.page1values)
        self.page1layout.addLayout(self.page1horizontal)    
        self.page1layout.addLayout(self.strategydescriptionlayout)
        self.page1.setLayout(self.page1layout)
        self.stackedLayout.addWidget(self.page1)

        # Create the pages
        self.pages = []
        self.labels = []
        self.graphWidget = []
        self.labeltwo = []
        self.labelthree = []
        self.labelfour = []
        self.labelfive = []
        self.labelsix = []
        self.labelseven = []
        self.labeleight = []
        self.labelnine = []
        self.labelten = []
        self.labeldelta = []
        self.labelgamma = []
        self.labeltheta = []
        self.labelvega = []
        self.delta = []
        self.gamma = []
        self.theta = []
        self.vega = []
        self.realdelta = []
        self.realtheta = []
        self.realgamma = []
        self.realvega = []
        for i in range(len(config)-1):
            # Append Pages and Setting Layout
            self.pages.append(QWidget())
            self.temp_layout = QVBoxLayout()
            # Qlabel Widget
            if str(config[str(i+1)]["PC"]) == "0":
                temp_pc = "Call"
            elif str(config[str(i+1)]["PC"]) == "1":
                temp_pc = "Put"
            elif str(config[str(i+1)]["PC"]) == "-1":
                temp_pc = "Stock"
            if str(config[str(i+1)]["b/s"]) == "1":
                temp_bs = "Bought"
            elif str(config[str(i+1)]["b/s"]) == "0":
                temp_bs = "Sold"
            temp_str = "\t" + temp_pc + " " + temp_bs
            print(temp_str)
            self.labels.append(QLabel(str(temp_str)))
            self.labels[i].setFont(QFont("Arial font",20))
            self.temp_layout.addWidget(self.labels[i])
                # Horizontal Layout
            self.temp_2_layout = QHBoxLayout()
            self.graphWidget.append(pg.PlotWidget())
            self.temp_2_layout.addWidget(self.graphWidget[i])
            pen = pg.mkPen(color=(0,0,0),width=1)
            self.graphWidget[i].setLabel('left',"Profit/Loss")
            self.graphWidget[i].setLabel('bottom','Stock_Price')
            # self.graphWidget[i].setBackground('w')
            self.graphWidget[i].plot(index1,strat[i],pen=pen,symbol = '+',symbolSize = 10)
            # self.temp_2_layout.addStretch()

            if config[str(i+1)]["O/S"] == 1:
                        # Vertical Layout
                self.temp_3_layout = QVBoxLayout()

                            # Grid Layout
                self.temp_4_layout = QGridLayout()
                self.labeltwo.append(QLabel("Stock Price"))
                self.labelthree.append(QLabel("Breakeven Point"))
                self.labelfour.append(QLabel("Strike Price"))
                self.labelfive.append(QLabel("Max Loss"))
                self.temp_4_layout.addWidget(self.labeltwo[i],0,0)
                self.temp_4_layout.addWidget(self.labelthree[i],1,0)
                self.temp_4_layout.addWidget(self.labelfour[i],2,0)
                self.temp_4_layout.addWidget(self.labelfive[i],3,0)

                self.labelsix.append(QLabel(str(stock_price)))
                self.labelseven.append(QLabel(str(breakeven_price[i])))
                self.labeleight.append(QLabel(str(strike[i])))
                self.labelnine.append(QLabel(str(max_loss[i])))
                self.temp_4_layout.addWidget(self.labelsix[i],0,1)
                self.temp_4_layout.addWidget(self.labelseven[i],1,1)
                self.temp_4_layout.addWidget(self.labeleight[i],2,1)
                self.temp_4_layout.addWidget(self.labelnine[i],3,1)

                            # Grid Layout
                self.temp_5_layout = QGridLayout()
                self.labeldelta.append(QLabel("Estimated Delta"))
                self.labelgamma.append(QLabel("Estimated Gamma"))
                self.labeltheta.append(QLabel("Estimated Theta"))
                self.labelvega.append(QLabel("Estimated Vega"))
                self.temp_5_layout.addWidget(self.labeldelta[i],0,0)
                self.temp_5_layout.addWidget(self.labelgamma[i],1,0)
                self.temp_5_layout.addWidget(self.labeltheta[i],2,0)
                self.temp_5_layout.addWidget(self.labelvega[i],3,0)

                self.delta.append(QLabel(str(temp_delta[i])))
                self.gamma.append(QLabel(str(temp_gamma[i])))
                self.theta.append(QLabel(str(temp_theta[i])))
                self.vega.append(QLabel(str(temp_vega[i])))
                self.temp_5_layout.addWidget(self.delta[i],0,1)
                self.temp_5_layout.addWidget(self.gamma[i],1,1)
                self.temp_5_layout.addWidget(self.theta[i],2,1)
                self.temp_5_layout.addWidget(self.vega[i],3,1)

                # Set Layout
                self.temp_layout.addLayout(self.temp_2_layout)
                self.temp_2_layout.addLayout(self.temp_3_layout)
                self.temp_3_layout.addLayout(self.temp_4_layout)
                self.temp_3_layout.addLayout(self.temp_5_layout)
                self.pages[i].setLayout(self.temp_layout)
            elif config[str(i+1)]["O/S"] == 0:
                self.labeltwo.append(0)
                self.labelthree.append(0)
                self.labelfour.append(0)
                self.labelfive.append(0)
                self.labelsix.append(0)
                self.labelseven.append(0)
                self.labeleight.append(0)
                self.labelnine.append(0)
                self.labeldelta.append(0)
                self.labelgamma.append(0)
                self.labeltheta.append(0)
                self.labelvega.append(0)
                self.delta.append(0)
                self.gamma.append(0)
                self.theta.append(0)
                self.vega.append(0)

                # Set Layout
                self.temp_layout.addLayout(self.temp_2_layout)
                self.pages[i].setLayout(self.temp_layout)

        for j in self.pages:
            self.stackedLayout.addWidget(j)

        # Sidebar
        sidebar = QVBoxLayout()
        temp = config["1"]["group:"]
        self.groupbutton = QPushButton(str(temp))
        sidebar.addWidget(self.groupbutton)
        self.groupbutton.clicked.connect(lambda: self.switchpage(0))
        self.pushbuttons = []
        self.arr = []
        self.tempvar = 0
        for i in range(len(config)-1):
            if str(config[str(i+1)]["PC"]) == "0":
                temp_pc = "Call"
            elif str(config[str(i+1)]["PC"]) == "1":
                temp_pc = "Put"
            elif str(config[str(i+1)]["PC"]) == "-1":
                temp_pc = "Stock"
            if str(config[str(i+1)]["b/s"]) == "1":
                temp_bs = "Bought"
            elif str(config[str(i+1)]["b/s"]) == "0":
                temp_bs = "Sold"
            temp_str = "\t" + temp_pc + " " + temp_bs
            self.pushbuttons.append(QPushButton(str(temp_str)))
            sidebar.addWidget(self.pushbuttons[i])
        self.pushbuttons[0].clicked.connect(lambda: self.switchpage(1))
        self.pushbuttons[1].clicked.connect(lambda: self.switchpage(2))
        # self.pushbuttons[2].clicked.connect(lambda: self.switchpage(3))
        # self.pushbuttons[3].clicked.connect(lambda: self.switchpage(4))
        # self.pushbuttons[4].clicked.connect(lambda: self.switchpage(5))
        
        sidebar.addStretch()
        layout.addLayout(sidebar)
    
        # Add the stacked layout to the toplevel layout
        layout.addLayout(self.stackedLayout)

    # SwitchPage Function
    def switchpage(self,page):
        self.stackedLayout.setCurrentIndex(page)

    def sumarr(self,arr):
        sum=0
        for i in arr:
            sum = sum + i
        return(sum) 
    
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))
    window.show()
    sys.exit(app.exec_())
