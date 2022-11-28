import csv
import matplotlib.pyplot as plt
import numpy as np

"""
Freezer simulation - export.py
@author: Morten Zink Stage
https://github.com/Peasniped/AAU-Simulering-af-fryserum

Created on 19/nov-2022

--

This module contains two functions to export a data set as a CSV-file or a graph

"""

def outCSV(self, outList: list, header: list = []) -> None:
    """
    Exports a list of data as a CSV-file.
    Header-row can be set with a list of titles in the optional header parameter
    """
    with open("out.csv", "w", newline="") as file:
        writer = csv.writer(file)
        if len(header) > 0:
            writer.writerow(header)
        writer.writerows(outList)

def outGraph(periods: int, yData: list, plotTitleList: list, graphTitle: str, xLabel: str, yLabel: str, fileName: str, yLimMin: float = None, yLimMax: float = None,) -> None:
    """
    Exports a given data set as a graph.

    Parameters:
    periods: int                An integer of how many x-values are contained in the dataset.
    dataListCollection: list    A list of lists with data sets
    plotTitleList: list         A list with titles for each data set
    title: str                  A string with the title of the graph
    xTitle: str                 A String with the title of the x-axis
    yTitle: str                 A String with the title of the y-axis
    fileName: str               A String specifying the filename of the output. .png will be appended automatically.
    yLimMin:                    Optional - Y-axis minimum limiter
    yLimMax:                    Optional - Y-axis maximum limiter
    """
    x = np.linspace(1, periods + 1, periods)

    plt.figure(figsize=(12,4))
    count = 0
    for dataList in yData:
        if 0 <= count < 10:
            y = np.array(dataList)
            plt.plot(x, y, label = plotTitleList[count], linestyle='solid')
            count += 1
        elif 10 <= count < 20:
            y = np.array(dataList)
            plt.plot(x, y, label = plotTitleList[count], linestyle='dashed')
            count += 1        
        elif 20 <= count < 30:
            y = np.array(dataList)
            plt.plot(x, y, label = plotTitleList[count], linestyle='dotted')
            count += 1              
        else: 
            y = np.array(dataList)
            plt.plot(x, y, label = plotTitleList[count], linestyle='dashdot')
            count += 1  
    if not type(yLimMin) == None and not type(yLimMax) == None :
        plt.ylim([yLimMin, yLimMax])
    #plt.xlim([0.75, 30.25])
    plt.title(graphTitle)
    plt.xlabel(xLabel)
    plt.ylabel(yLabel)
    plt.legend(loc='upper left', prop={'size': 8})
    plt.grid()
    plt.savefig(f"{fileName}.png", dpi=300)