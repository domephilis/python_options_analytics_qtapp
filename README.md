# python_options_analytics_qtapp

## File Structure
This is an application I made to practice a bit on my understanding of the black-scholes formulas.  There are 3 useful python files in this folder.  One is black-scholes.py that establishes the entire computational system on the black-scholes equation and their derived equations.  The other one is the binomial.py that uses the binomial tree to build out the program.  Due to there similarity, from now on these 2 files are going to be collectively called the Computations Files  The qt_options_tracker.py is the qt gui wrapper that presents the calculations in an ugly way.

## Brief Explanation of the Computations Files
All of the Computations Files will follow this format.  We define a few functions that would be used in the gui wrapper.  In order, these are, OptionsVal (to determine the value of an option at any specified parameter), ThreadWithReturnValue (a class to help with running the threading module of python with return values), plgraph (which generates the plgraph of an option with the parameter being a dictionary that is called config, see later), legn (a subfunction under plgraph that calculates for a specific leg of option specified in config the profit of an option), legstock (a subfunction under plgraph that calculates for a specific leg of stock that is within the option strategy specified in config the profit of a stock), plpoint (a pl of the specified strategy under a specfic set of parameters), bepoint(the breakeven point at expiration of the specified strategy), delta, gamma, theta, vega, cdf (cumulative distribution function of a lognormal distribution), pdf (probability density function of a lognormal distribution), black_scholes_method (for calculating the probability of the stock price exceeding a certain amount).

The program itself defines the related functions, import the necessary config files, and write to a result file the result of the plgraph.  In the config files, you may the properties of multiple options in order to form a strategy.  The file is located in the ./json folder.

## qt_options_tracker.py

This program loads the variables and dictionaries from the Computations Files, uses the functions in the Computations Files to compute them for each options in the strategy and the strategy as a whole, and creates the qt application in the following manner.  The program uses stackedLayout in Qt5 to create several pages for each options in the strategy you load.  As of now, you need to go into the code and configure how many options you have.  In each page, we have a nested series of horizontal and vertical layouts.  Vertical for the division between the title and the page, a grid, a horizontal, and another grid.

## Implementation Notes

I'm too lazy for that, seriously did you think I of all people are going to carefully document every function in the program.  It's close to a thousand lines of crappy code.
