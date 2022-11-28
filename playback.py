import Simulation
import export
import time

"""
Freezer simulation - playback.py
@author: Morten Zink Stage
https://github.com/Peasniped/AAU-Simulering-af-fryserum

Created on 19/nov-2022

--

This module contains a single class, 'MonteCarlo', that utilizes the Monte Carlo-method to simulate the freezer room in many iterations
The simulation is started by instantiating the class and calling the function runManySimulations().
The calculated data is saved in the parameter dataList

The simulation can utilize an intelligent thermostat by instantiating the class with the parameters 'True' and a limit price. Example: ' > test = MonteCarlo(100, True, 2.10)'

"""

class MonteCarlo:

    def __init__(self, samples: int, smartThermostatOn: bool = False, smartPriceMax: float = 2.10) -> None:
        """
        Sets important variables when the class is instantiated

        - samples is how many iterations the simulation should be run
        - smartThermostatOn is set to True to use the intelligent thermostat
        - smartPriceMax is set with a float to limit the max price, where the thermostat can run

        """        
        self.smartThermostatOn = smartThermostatOn
        self.smartPriceMax = smartPriceMax

        self.playback = Simulation.freezer(self.smartThermostatOn, self.smartPriceMax)

        self.samples = int(samples)
        self.simHasBeenRun = False
        self.dataList = []

    
    def saveData(self, column: int = 5) -> list:
        """
        Returns data isolated from a specified column and calculates the moving average.
        """
        data = self.isolateColumn(column, self.dataList)
        dataMA = self.movingAverage(data)

        return(dataMA)


    def runManySimulations(self) -> None:
        """
        Runs many simulations using parameters set when instantiating the class.
        Simulation time of a single sample is slightly longer than 1 second.
        """
        self.dataList = []
        for sample in range(self.samples):
            startTime = time.time()
            self.playback.__init__(self.smartThermostatOn, self.smartPriceMax)

            sampleData = self.playback.simulateMonth()
            self.dataList.append(sampleData)
            
            endTime = time.time()
            diffTime = endTime - startTime

            print(f"Simulated Sample {1 + sample:02d} of {self.samples} in {round(diffTime,1)} seconds - ETA: {round(((self.samples - (sample + 1)) * diffTime) / 60,2)} minutes")
        self.simHasBeenRun = True

    def isolateColumn(self, column: int, dataList: list) -> list:
        """
        Returns a list with every entry in a specified column from the specified data set
        """
        newList = []
        for each in dataList:
            newList.append(each[-1][column])
        return newList

    def movingAverage(self, listOfTotals: list) -> list:
        """
        Calculates the moving average of each number in a list
        """
        records = len(listOfTotals)
        movingSum = []
        movingAverage = []

        for i in range(records):
            if len(movingSum) > 0:
                movingSum.append(movingSum[-1] + listOfTotals[i])
            else:
                movingSum.append(listOfTotals[0])

            movingAverage.append(movingSum[-1] / (i + 1))
        return movingAverage

    def graphSimulations(self, dataListCollection: list, plotTitleList: list, title: str, xTitle: str, yTitle: str, fileName: str, yLimMin: float = None, yLimMax: float = None) -> None:
        """
        Uses the Export-module to export data to a graph

        Parameters:
        dataListCollection: list    A list of lists with data sets
        plotTitleList: list         A list with titles for each data set
        title: str                  A string with the title of the graph
        xTitle: str                 A String with the title of the x-axis
        yTitle: str                 A String with the title of the y-axis
        fileName: str               A String specifying the filename of the output. .png will be appended automatically.
        yLimMin:                    Optional - Y-axis minimum limiter
        yLimMax:                    Optional - Y-axis maximum limiter
        """
        if not self.simHasBeenRun:
            print("Simulation has not been run.")

        # Kigger efter, hvor mange samples der var i den sidste simulering
        periods = len(self.dataList)        

        export.outGraph(periods, dataListCollection, plotTitleList, title, xTitle, yTitle, fileName, yLimMin, yLimMax)


if __name__ == "__main__":
    
    # Sample code running 50 simulations with conventional and intelligent thermostats and exporting a graph comparing price and temperature
    tempDataCollection = []
    costDataCollection = []
    plotTitleList = []

    for i in range(1):
        test = MonteCarlo(50, False)
        print("\n  --- Simulating 50 samples with the conventional thermostat")
        test.runManySimulations()
        tempDataCollection.append(test.saveData(3))
        costDataCollection.append(test.saveData(5))
        plotTitleList.append(f"Conventional thermostat")

    for i in range(1):
        test = MonteCarlo(50, True, 2.1)
        print("\n  --- Simulating 50 samples with the intelligent thermostat")
        test.runManySimulations()
        tempDataCollection.append(test.saveData(3))
        costDataCollection.append(test.saveData(5))
        plotTitleList.append(f"Intelligent thermostat")

    test.graphSimulations(costDataCollection, plotTitleList,"Monte Carlo Simulation of monthly average total cost", "Number of simulations", "Total cost in kr.", "graphCost")
    test.graphSimulations(tempDataCollection, plotTitleList,"Monte Carlo Simulation of monthly average temperatura", "Number of simulations", "Temperature in °C", "graphTemp")