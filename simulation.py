from random import randint
import pandas as pd

# -*- coding: utf-8 -*-
"""
Freezer simulation - simulation.py
@author: Morten Zink Stage
https://github.com/Peasniped/AAU-Simulering-af-fryserum

Created on 19/nov-2022

--

This module contains a single class, 'freezer', thgat simulates the refrigerated room
The simulation can be started by instantiating the class and calling the function 'runSingleSim()'

The simulation can utilize an intelligent thermostat by instantiating the class with the parameters 'True' and a limit price. Example: ' > test = freezer(True, 2.10)'

"""

class freezer:

    def __init__(self, smartThermostatOn: bool = False, smartPriceMax: float = 2.10) -> None:
        """
        Sets important variables when the class is instantiated
        
        - smartThermostatOn is set to True to use the intelligent thermostat
        - smartPriceMax is set with a float to limit the max price, where the thermostat can run

        """
        ## ---------------- Settings ----------------
        self.tempLast = 5.0         # T_0 / T[n-1]
        self.tempOutside = 20       # T_rum
        self.tempCompressor = -5    # T_komp
        self.tempGoal = 5           # T_mål
        self.budget = 12000         # cumlative counter of the cost of electricity used by the compressor
        self.smartThermostat = smartThermostatOn
        self.smartPriceMax = smartPriceMax # If temp is within interval 
        self.smartTempMax = 6       # Max allowed temp. Food starts rotting at temp < 6.5
        self.smartTempMin = 4       # Min allowed temp. Food starts gettomg freezerburn(?) at 3.5 < temp
        
        ## ----------- Working variables ------------
        self.period = 1             # counts the current 5-minute interval
        self.periods = 8640         # the amount of periods in a 30-day month (12*24*30)
        self.kWhUsed = 0            # cumlative counter of the kWh used by the compressor
        self.kWhCost = 0            # cumlative counter of the cost of electricity used by the compressor
        self.csvLoaded = False      # boolean to make sure the CSV is not loaded every time the price is fetched
        self.priceList = []         # list to store the contents of 'elpris.csv'
        self.foodWasteCost = 0      # cumlative counter of the cost of food wasted by bad temperatures 
        pass

    def doorOpen(self) -> bool:
        """
        Determines if the door is open by drawing a random number from 1-10. If the number is 10, the door is open.
        """
        num = randint(1,10)
        if num == 10:
            isOpen = True
        else:
            isOpen = False
        return(isOpen)

    def compRunning(self) -> bool:
        """
        Determines if the compressor is running.
        This is the Simple conventional thermostatic.
        """
        if self.tempLast > self.tempGoal:
            isOn = True
        else:
            isOn = False
        return(isOn)

    def smartCompRunning(self) -> bool:
        """
        Determines if the compressor is running.
        This is the smarter price-aware thermostat.
        """
        temp = self.tempLast

        if temp > self.smartTempMax:
            isOn = True
        elif temp < self.smartTempMin:
            isOn = False
        elif self.priceList[self.period - 1] < self.smartPriceMax:
            isOn = True
        else:
            isOn = False
        return(isOn)

    def tempLoss(self,doorOpen: bool) -> float: # C_1
        """
        Calculates the temperature loss based on whether the door is open or closed.
        """
        seconds = 1
        if doorOpen == False:
            return(5 * 10**-7 * seconds**-1)
        else:
            return(3 * 10**-5 * seconds**-1)

    def tempCooled(self, compOn: bool) -> float: # C_2
        """
        Calculates the temperature that is cooled if the compressor is running.
        """
        seconds = 1
        if compOn == False:
            return(0 * seconds**-1)
        else:
            return(8 * 10**-6 * seconds**-1)

    def loadCSV(self) -> None:
        """
        Loads the CSV-file 'elpris.csv' with periodic electricity prices.
        """
        if not self.csvLoaded:
            dataFrame = pd.read_csv('elpris.csv', sep = ',', index_col = 0)
            self.priceList = dataFrame['Pris'].values.tolist()
            self.csvLoaded = True

    def calcPeriodElectricCosts(self) -> int:
        """
        Calculates the cost of electricity based on time(period) and if the compressor is running.
        """
        if self.smartThermostat == True:
            if self.smartCompRunning():
                self.kWhCost += self.priceList[self.period]
                self.kWhUsed += 1
                return 1
            else:
                return 0
        else:
            if self.compRunning():
                self.kWhCost += self.priceList[self.period]
                self.kWhUsed += 1
                return 1
            else:
                return 0     

    def calcFoodWaste(self, temp: float) -> float:
        """
        Calculates the cost of food waste based on the temperature.
        """
        wasted = 0
        if temp < 3.5:
            wasted = 4.39**(-0.49*temp)
            self.foodWasteCost += wasted
        elif temp >= 6.5:
            wasted = 0.11**(0.31*temp)
            self.foodWasteCost += wasted
        return wasted
        

    def T(self) -> float:
        """
        Calculates the temperature based on if the foor is open and if the compressor is running.
        """
        minutes = 5
        doorOpen = self.doorOpen()

        for minute in range(minutes):
            if self.smartThermostat == True:
                compOn = self.smartCompRunning()
            else:
                compOn = self.compRunning()
            
            for second in range(60):
                temp = self.tempLast + (self.tempLoss(doorOpen)*(self.tempOutside - self.tempLast) + self.tempCooled(compOn)*(self.tempCompressor - self.tempLast) )
                self.tempLast = temp
        return temp

    def periodToDTG(self, period: int) -> str:
        """
        Returns the Date-Time Group of the beginning of a given 5-minute period.
        This can be a useful way to tag the data.
        """
        year = 2022
        month = "SEP"
        tz = "A"
        day = (period / 288) + 1
        dayR = int(period / 288) + 1
        hour = (day - dayR) * 24
        hourR = int(hour)
        min = (hour - hourR) * 60
        minR = round(min)               # her bruges round(), da int() gav nogle mærkelige tal
        return(str(f"{dayR:02d} {hourR:02d}:{minR:02d} {tz} {month} {year}"))

    def periodCost(self, temp: float) -> float:
        """
        Calculates the total cost of a month by adding costs of electricity and wasted food.
        """
        costSum = self.calcPeriodElectricCosts() + self.calcFoodWaste(temp)
        return costSum

    def totalCost(self) -> float:
        """
        Returns the total cost of a month if it has already been calculated with peridCosts().
        """
        costSum = self.kWhCost + self.foodWasteCost
        return costSum
    
    def remainingBudget(self) -> float:
        """
        Calculates the remainder of the budget.
        """
        costSum = self.totalCost()
        diff = self.budget - costSum
        return diff

    def printRemainginBudget(self) -> None:
        """
        Prints out the remaining budget using the function remainingBudget() to the console.
        """
        print(f"Monthly consumption: Electricity = {self.kWhUsed} kWh at a cost of {round(self.kWhCost,2)} kr. - Cost of wasted food: {round(self.foodWasteCost,2)} kr.")
        diff = self.remainingBudget()
        diffRound = round(diff, 2)
        if diff > 0:
            print(f"You have spent LESS than budgeted, your surplus is {diffRound} kr.\n")
        elif diff < 0:
            print(f"You have spent MORE than budgeted, your deficit is {-1 * diffRound} kr.\n")
        else:
            print(f"You have used your entire budget but no extra. Good job!\n")

    def simulateMonth(self) -> list:
        """
        Simulates data for a whole month. Returns a list with an entry for each period in the format [date-time group, period number, total cost, temp, kWh used, cost of electricity, cost of food waste].
        """
        self.loadCSV()
        outList = []
        for period in range(self.periods):
            self.period = period
            dtg = self.periodToDTG(period)
            temp = self.T()
            cost = self.periodCost(temp)
            
            outList.append([dtg, period, cost, temp, self.kWhUsed, self.kWhCost, self.foodWasteCost])
        return(outList)

    def runSingleSim(self) -> None:
        """
        runs a single simulation.
        """
        self.simulateMonth()
        print("\n   --- Simulation completed ---")
        self.printRemainginBudget()

if __name__ == "__main__":

    test = freezer(True, 2.10)
    test.runSingleSim()
