
import plotly as pl
import numpy as np
import pandas as pn

# Set up the first csv file to be read, which is the Edmonton Assessment Info (EAI).
df_EAI = pn.read_csv('Property_Assessment_Data__Current_Calendar_Year_.csv')

# First filter out all property assessments that are not 100% residential.
df_EAI = df_EAI[(df_EAI['Assessment Class % 1'] == 100) &
                                  (df_EAI['Assessment Class 1'] == 'RESIDENTIAL')]

# Then set the dataframe to contain only the Neighbourhood name and Assessed Value of each entry,
# as those are the values we care about.
df_EAI = df_EAI.loc[:, ['Neighbourhood', 'Assessed Value']]

# Also filter out any entries with attributes listed as 'NaN'
df_EAI = df_EAI.dropna()
df_EAI = df_EAI.sort_values(by='Neighbourhood')


# Create the dataframe for the Pop. by Household Income (PHI) csv
df_PHI = pn.read_csv('2016_Census_-_Population_by_Household_Income__Neighbourhood_Ward_.csv')

# Create a sum column for the dataframe that contains the total number of users that responded
df_PHI['Sum'] = df_PHI["Less than $30,000"] + df_PHI["$30,000 to less than $60,000"] + \
                df_PHI["$60,000 to less than $100,000"] + df_PHI["$100,000 to less than $125,000"] + \
                df_PHI["$125,000 to less than $150,000"] + df_PHI["$150,000 to less than $200,000"] + \
                df_PHI["$200,000 to less than $250,000"] + df_PHI["$250,000 or more"]

# Filter out all the neighbourhoods that have 0 responses, since these are 'neighbourhoods' without
# any actual residents, therefore useless.
df_PHI = df_PHI[df_PHI['Sum'] > 0]


# The generateSpecificData function is used by the Specific View on the Dash page to fetch the
# relevant information on a certain neighbourhood. It takes a string name as a parameter, and
# searches the EAI dataframe for that neighbourhood's data. It then returns a list containing
# the number of neighbourhoods (count), the minimum assessed value, the maximum value, the mean
# value, and the median value.

def generateSpecificData(name):
    df = df_EAI[df_EAI['Neighbourhood'] == str(name).upper()]
    count = df.count()[0]
    # Count will be 0 if the neighbourhood isn't found. Thus, it will return None.
    if count == 0:
        return None
    minValue = df.min(0)[1]
    maxValue = df.max(0)[1]
    mean = int(df.mean(0, numeric_only=True)[0])
    df = df.sort_values(by='Assessed Value')
    if count % 2 == 0:
        median = df.iloc[int(count/2)][1]
    else:
        median = (df.iloc[int((count/2)-0.5)][1] + df.iloc[int((count/2)+0.5)][1]) / 2
    df2 = df_PHI[df_PHI['Neighbourhood Name'] == str(name).upper()]
    if df2.count()[0] == 0:
        mode = None
    else:
        comp1 = df2.iloc[0, 3]
        comp2 = df2.iloc[0, 4]
        comp3 = df2.iloc[0, 5]
        comp4 = df2.iloc[0, 6]
        comp5 = df2.iloc[0, 7]
        comp6 = df2.iloc[0, 8]
        comp7 = df2.iloc[0, 9]
        comp8 = df2.iloc[0, 10]

        # Find the category with the most respondants, and use that as our mode income. I'm sure there's
        # a more optimized way to do this, but I don't know it.
        if (comp1 > comp2 and comp1 > comp3 and comp1 > comp4 and comp1 > comp5 and comp1 > comp6 and comp1 > comp7 and
            comp1 > comp8):
            mode = "Less than $30,000"
        elif (comp2 > comp1 and comp2 > comp3 and comp2 > comp4 and comp2 > comp5 and comp2 > comp6 and comp2 > comp7 and
            comp2 > comp8):
            mode = "$30,000 to less than $60,000"
        elif (comp3 > comp1 and comp3 > comp2 and comp3 > comp4 and comp3 > comp5 and comp3 > comp6 and comp3 > comp7 and
            comp3 > comp8):
            mode = "$60,000 to less than $100,000"
        elif (comp4 > comp1 and comp4 > comp2 and comp4 > comp3 and comp4 > comp5 and comp4 > comp6 and comp4 > comp7 and
            comp4 > comp8):
            mode = "$100,000 to less than $125,000"
        elif (comp5 > comp1 and comp5 > comp2 and comp5 > comp3 and comp5 > comp4 and comp5 > comp6 and comp5 > comp7 and
            comp5 > comp8):
            mode = "$125,000 to less than $150,000"
        elif (comp6 > comp1 and comp6 > comp2 and comp6 > comp3 and comp6 > comp4 and comp6 > comp5 and comp6 > comp7 and
            comp6 > comp8):
            mode = "$150,000 to less than $200,000"
        elif (comp7 > comp1 and comp7 > comp2 and comp7 > comp3 and comp7 > comp4 and comp7 > comp5 and comp7 > comp6 and
            comp7 > comp8):
            mode = "$200,000 to less than $250,000"
        elif (comp8 > comp1 and comp8 > comp3 and comp8 > comp3 and comp8 > comp4 and comp8 > comp5 and comp8 > comp6 and
            comp8 > comp7):
            mode = "$250,000 or more"

    dataList = [name, count, '$' + str(minValue), '$' + str(maxValue), '$' + str(mean), '$' + str(median), mode]

    return dataList


