# coding: utf-8
from __future__ import unicode_literals
from math import *
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import threading
import json

def OptionsVal(n, S, K, r, v, T, PC):
    dt = T/n
    u = m.exp(v*m.sqrt(dt))
    d = 1/u
    p = (m.exp(r*dt)-d)/(u-d)
    Pm = np.zeros((n+1, n+1))
    Cm = np.zeros((n+1, n+1))
    tmp = np.zeros((2,n+1))
    for j in range(n+1):
        tmp[0,j] = S*m.pow(d,j)
        tmp[1,j] = S*m.pow(u,j)
    tot = np.unique(tmp)
    c = n
    for i in range(c+1):
        for j in range(c+1):
            Pm[i,j-c-1] = tot[(n-i)+j]
        c=c-1
    for j in range(n+1, 0, -1):
        for i in range(j):
            if (PC == 1):
                if(j == n+1):
                    Cm[i,j-1] = max(K-Pm[i,j-1], 0)
                else:
                    Cm[i,j-1] = m.exp(-.05*dt) * (p*Cm[i,j] + (1-p)*Cm[i+1,j])
            if (PC == 0):
                if (j == n + 1):
                    Cm[i,j-1] = max(Pm[i,j-1]-K, 0)
                else:
                    Cm[i,j-1] = m.exp(-.05*dt) * (p*Cm[i,j] + (1-p)*Cm[i+1,j])
    # FOR USE IN MULTITHREADING
    return Cm[0,0]

# Threading Class

class ThreadWithReturnValue(threading.Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        threading.Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None
    def run(self):
        print(type(self._target))
        if self._target is not None:
            self._return = self._target(*self._args,
                                                **self._kwargs)
    def join(self, *args):
        threading.Thread.join(self, *args)
        return self._return

# Configuration Import

with open("/home/eric/projects/options_tracker/json/20211105IBMIB1.json","r") as f:
    config = json.load(f)

iter_par = config["0"]

# PLgraph generation
def plgraph(config):
    # Parameter Definitions

    sum = []
    percent = []
    temp_sum = 0
    zero_array = []
    under_price = []
    n = 400

    iter_par = config["0"]
    iter_step = (iter_par["end"] - iter_par["start"]) / iter_par["iters"]

    # Function Definition

    # Underlying Asset Price Generation

    for i in range(iter_par["iters"] + 1):
        if i == 0:
            under_price.append(iter_par["start"])
        elif i > 0:
            under_price.append(under_price[i-1] + iter_step)

    # Function for Calculating a Series of Options Profits Based on Parameters

    def legn(iter_par,calc_par,under_price):
        leg_n = []
        for j in range(iter_par["iters"] + 1):
            temp_1 = OptionsVal(n,under_price[j],calc_par["strike"],calc_par["dis_rate"],calc_par["volatility"],calc_par["time"],calc_par["PC"])
            if calc_par["b/s"] == 1:
                profit_temp_1 = temp_1 - calc_par["exec_price"]
            elif calc_par["b/s"] == 0:
                profit_temp_1 = calc_par["exec_price"] - temp_1
            leg_n.append(profit_temp_1)
        return leg_n

    strat = []

    # MULTITHREADING
    threads = []
    threads.append(ThreadWithReturnValue(target = legn, args = (iter_par,config["1"],under_price)))
    threads.append(ThreadWithReturnValue(target = legn, args = (iter_par,config["2"],under_price)))
    threads.append(ThreadWithReturnValue(target = legn, args = (iter_par,config["3"],under_price)))
    threads.append(ThreadWithReturnValue(target = legn, args = (iter_par,config["4"],under_price)))

    # Running the Threads

    for l in threads:
        l.start()
        temp = l.join()
        strat.append(temp)

    # Summing the Results

    for k in range(iter_par["iters"]):
        for m in range(4):
            temp_sum += strat[m][k]
        sum.append(temp_sum)
        percent.append(temp_sum/4.83)
        temp_sum = 0
        zero_array.append(0)

    # Creating the POS_NEG Arrays

    pos = np.array(sum)
    neg = np.array(sum)

    pos[pos < 0] = np.nan
    neg[neg > 0] = np.nan

    # Index Generation

    index_array = []

    for a in range(len(under_price)):
        if ((a + 1) % 10) != 0:
            pass
        elif ((a + 1) % 10) == 0:
            index_array.append(round(under_price[a],2))

    return index_array,zero_array,sum,strat,percent,pos,neg

#   P/L Function

def plpoint(S,K,r,v,T,PC,bs,exec_price):
    tempoptionsval = OptionsVal(400,S,K,r,v,T,PC)
    # bs == 1 is bought bs == 0 is sold
    if bs == 1:
        profit_temp_1 = temp_1 - exec_price
    elif bs == 0:
        profit_temp_1 = exec_price - temp_1
    return profit_temp_1

#   Breakeven Point Function

def bepoint(sum,strike,configuration,r,v,increment):
    sign = lambda a: (a>0) - (a<0)
    strike_to_ob = []
    result = []
    for i in range(len(sum)):
        if i > 0:
            if sign(sum[i-1]) != sign(sum[i]):
                obpoint = iter_par["start"] + (i * increment)
                for j in range(len(strike)):
                    strike_to_ob.append([j,(obpoint-strike[j])])
                sorted_strike_to_ob = sorted(strike_to_ob, key = lambda x:x[1], reverse=True)
                x1 = strike[int(sorted_strike_to_ob[0][0])]
                x2 = strike[int(sorted_strike_to_ob[1][0])]
                y1 = 0
                y2 = 0
                for i in range(len(configuration) - 1):
                    tempstrike = configuration[str(i + 1)]["strike"]
                    temptime = 0.001
                    tempPC = configuration[str(i + 1)]["PC"]
                    tempbs = configuration[str(i + 1)]["b/s"]
                    tempexec = configuration[str(i + 1)]["exec_price"]
                    y1 += plpoint(x1,tempstrike,r,v,temptime,tempPC,tempbs,tempexec)
                    y2 += plpoint(x1,tempstrike,r,v,temptime,tempPC,tempbs,tempexec)
                m = (y2 - y1) / (x2 - x1)
                b = y1 - (m * x1)
                result.append((0 - b) / m)
            else:
                pass
        else:
            pass
        return result


# The Greeks (The delta gamma theta and vega exposure in just the sum of the individual positions)

def delta(current_price,strike,risk_free_rate,sigma,time_to_expiry,put_call):
    n = 400
    S = current_price
    K = strike
    r = risk_free_rate
    v = sigma
    T = time_to_expiry
    PC = put_call
    increment = 0.0000000000001
    return (OptionsVal(n,S+increment,K,r,v,T,PC) - OptionsVal(n,S,K,r,v,T,PC))/increment

def gamma(current_price,strike,risk_free_rate,sigma,time_to_expiry,put_call):
    n = 400
    S = current_price
    K = strike
    r = risk_free_rate
    v = sigma
    T = time_to_expiry
    PC = put_call
    increment = 1
    a = OptionsVal(n,S+increment,K,r,v,T,PC)
    b = OptionsVal(n,S,K,r,v,T,PC)
    c = OptionsVal(n,S - increment,K,r,v,T,PC)
    d = m.pow(increment,2)
    return  (a - (2 * b) + c) / d

def theta(current_price,strike,risk_free_rate,sigma,time_to_expiry,put_call):
    n = 400
    S = current_price
    K = strike
    r = risk_free_rate
    v = sigma
    T = time_to_expiry
    PC = put_call
    increment = 0.0000001
    return 0-((OptionsVal(n,S,K,r,v,T + increment,PC) - OptionsVal(n,S,K,r,v,T,PC))/(increment * 365))

def vega(current_price,strike,risk_free_rate,sigma,time_to_expiry,put_call):
    n = 400
    S = current_price
    K = strike
    r = risk_free_rate
    v = sigma
    T = time_to_expiry
    PC = put_call
    increment = 0.000000000001
    return (OptionsVal(n,S,K,r,v + increment,T,PC) - OptionsVal(n,S,K,r,v,T,PC))/(increment * 100)

# current_price = 123.61
# r = 0.015
# sigma = 0.20
# time_to_expiry = 9/365
# delta_arr = []
# print(gamma(current_price,123,r,sigma,time_to_expiry,0))
# for i in range(len(config)-1):
#     delta_value = delta(current_price,config[str(i + 1)]["strike"],r,sigma,time_to_expiry,config[str(i + 1)]["PC"])
#     delta_arr.append(delta_value)
# print(delta_arr)

# Probability Calculations

def cdf(mu,sigma,price_target):
    logmu = log(pow(mu,2) / sqrt(pow(mu,2) + pow(sigma,2)))
    logsigma = log(1 + (pow(sigma,2) / pow(mu,2)))
    half = 1/2
    erf_value = (log(price_target) - logmu) / logsigma * sqrt(2)
    cdf_value = half * (1 + erf(erf_value))
    return cdf_value

def pdf(mu,sigma,price_target):
    logmu = log(pow(mu,2) / sqrt(pow(mu,2) + pow(sigma,2)))
    logsigma = log(1 + (pow(sigma,2) / pow(mu,2)))
    reciprocal = price_target * sigma * sqrt(2 * pi)
    exponent = pow((- log(price_target) - mu),2) / (2 * sigma ^ 2)
    pdf_value = (1 / reciprocal) * exp(exponent)
    return pdf_value


# Plotting and Print
# index_array,zero_array,sum,strat,percent,pos,neg = plgraph(config=config)
# index_np = np.array(index_array)
# zero_np = np.array(zero_array)
# sum_np = np.array(sum)
# strat_np = np.array(strat)
# percent_np = np.array(percent)
# pos_np = np.array(pos)
# neg_np = np.array(neg)
# result = {
#     "index": index_np.tolist(),
#     "zeros": zero_np.tolist(),
#     "sum": sum_np.tolist(),
#     "strat": strat_np.tolist(),
#     "percent": percent_np.tolist(),
#     "pos": pos_np.tolist(),
#     "neg": neg_np.tolist()
# }
# json_result = json.dumps(result)
# with open("/home/eric/projects/options_tracker/json/json_result.json","w") as f:
#     f.write(json_result)

# print(sum)
# print(percent)
# print(strat)

# plt.style.use('fivethirtyeight')
# plt.plot(pos, color = 'r')
# plt.plot(neg, color = 'b')
# plt.plot(zero_array)
# plt.xticks(np.arange(0,config["0"]["iters"],step = (config["0"]["iters"]/20)),index_array)
# plt.show()
# print(len(config))
