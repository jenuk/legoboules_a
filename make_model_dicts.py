import numpy as np
from scipy.interpolate import interp1d
from math import ceil, floor
import sys

class ModelMaker:
    '''
        The ModelMaker Class generates different models from 21 given measured data points.
    '''

    def __init__(self, data):
        '''
            Initializes a ModelMaker with 20 measured data points. The data points correspond to percentages in steps of 5 starting with 0 and ending at 95.

            Argument:
                data    measured data as a list of floats
        '''

        if len(data) != 20:
            raise ValueError
        self.data = data
        self.percentages = list(range(0, 100, 5))
        self.evaluation_points = [0.5*i for i in range(1, 191)]     # points in steps of 0.5

    def make_spline(self, kind):
        '''
            Generates a spline model.

            Argument:
                kind    'linear' or 'cubic' kind of spline

            Returns:
                a dictionary with key-value pairs matching distances in cm to percentages in [0,1) representing the model
        '''

        spline = interp1d(self.percentages, self.data, kind=kind)
        evaluation_results = spline(self.evaluation_points)
        return self.inverse_funcion(evaluation_results)

    def make_polynom(self, degree):
        '''
            Generates a polynomial model.

            Argument:
                degree    degree of the polynomial, e.g. 1=linear, 3 = cubic

            Returns:
                a dictionary with key-value pairs matching distances in cm to percentages in [0,1) representing the model
        '''

        polynom = np.polyfit(self.percentages, self.data, degree)
        evaluation_results = np.polyval(polynom, self.evaluation_points)
        return self.inverse_funcion(evaluation_results)

    def inverse_funcion(self, evaluation_results):
        '''
            Inverts a function given by dicrete points

            Argument:
                evaluation_results      values that result from the evaluation of the spline/polynom a the evaluation points

            Returns:
                a dictionary with key-value pairs matching distances in cm to percentages in [0,1) representing the function of a model
        '''

        inverted = dict()
        mini, maxi = ceil(min(evaluation_results)), floor(max(evaluation_results))
        # searches for each point in the range interval [mini, maxi] a nearest value in the evaluation_results
        for i in range(mini, maxi+1):
            # gets evaluation_result with minimal distance to i
            inverted[i] = self.evaluation_points[np.abs(evaluation_results - i).argmin()]
        return inverted

if __name__ == '__main__':
    # 20 measured data points are needed as command line parameters for generating models
    if len(sys.argv) != 21:
        print("Not enough data")
    data = list(map(float, sys.argv[1:])) # makes arguments floats
    model_maker = ModelMaker(data)

    # generate a python file with 4 objects to save the 4 models
    text = "spline_cubic = " + repr(model_maker.make_spline("linear"))
    text += "\n" + "spline_lin = " + repr(model_maker.make_spline("cubic"))
    text += "\n" + "pol_lin = " + repr(model_maker.make_polynom(1))
    text += "\n" + "pol_cubic = " + repr(model_maker.make_polynom(3))
    with open("model_dicts.py", "w") as file:
        file.write(text)
