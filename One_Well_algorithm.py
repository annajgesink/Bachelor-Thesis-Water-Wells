import numpy as np
import pandas as pd

def load_data(woreda_name):
    '''Load data from Excel sheets obtained from QGIS'''

    file_path_grid = f"excel/{woreda_name} grid.xlsx"
    data_grid = pd.read_excel(file_path_grid, index_col=1, header=0)
    data_grid = data_grid.drop('fid', axis=1)
    data_grid.index = data_grid.index.astype(str)

    file_path_village = f"excel/villages {woreda_name}.xlsx"
    columns_to_use = ['id', 'populationsum', 'elevation1']
    data_village = pd.read_excel(file_path_village, usecols=columns_to_use, index_col=0)
    data_village.index = data_village.index.astype(str)

    return data_village, data_grid

def hydrolic_power(heigth):
    ''' Energy needed to pump water up height in kWh'''
    rho = 1000
    g = 9.81
    Q = 0.03
    etha = 0.70
    hours = 10 * 365 * 24
    return rho * g * heigth * Q * hours / (etha * 1000)


def connection_cost(village_id, well_id):
    '''Costs to connect a village to a potential well location. Based on distance and elevation difference.
    :param village_id: number of the village
    :param well_id: number of the well'''
    distance_to_village = data_grid.at[well_id,village_id]
    elevation_difference = data_village.at[village_id, "elevation1"] - data_grid.at[well_id, "elevation1"]
    if elevation_difference < 0:
        elevation_difference = 0
    return well_pipeline_ratio * distance_to_village + well_hill_ratio * hydrolic_power(elevation_difference)


def find_cheapest_configuration(data_village, data_grid):
    '''' Takes the villages, potential well locations and distances between them and calculates the cheapest location to
    place the well and returns the location, cost and villages connected
    :param data_grid: data frame with potential well locations with corresponding suitablity, elevation and distances to villages
    :param data_village: data frame with villages and population'''

    minimal_cost = (data_grid.index[0], np.inf, [])
    population = data_village['populationsum'].sum()

    for gridpoint in data_grid.index:
        connect_cost_per_capita = []
        for village in data_village.index:
            connect_cost_per_capita.append((connection_cost(village,gridpoint)/ data_village.at[village,'populationsum'],village))
        sorted_cost = sorted(connect_cost_per_capita, key= lambda x:x[0], reverse = False)
        chosen_villages = []
        pop = population * percentage_to_connect
        i = 0
        while pop > 0 and i < len(sorted_cost):
            chosen_villages.append(sorted_cost[i][1])
            pop -= data_village.at[sorted_cost[i][1],'populationsum']
            i += 1
        cost = 1/data_grid.at[gridpoint,'suitability1']
        for village in chosen_villages:
            cost += connection_cost(village,gridpoint)

        if cost < minimal_cost[1]:
            minimal_cost = (gridpoint, cost, chosen_villages)

    return minimal_cost



if __name__ == '__main__':

    # variables
    # amount of wells per m pipeline
    well_pipeline_ratio = 1 / 5000
    # amount of wells per m elevation
    well_hill_ratio = 1 / (500000 / 0.32)
    # percentage of population to connect to the new well
    percentage_to_connect = 0.7
    # names of priority areas
    woreda_names = ['Basketo SP Woreda', "Bilate Zuria", "Kucha", "Maji", "Melekoza", "Menit Shasha", "Salamago",
                    "South Ari", "Uba Debre Tsehay", "Wulbareg"]
    wellstring = ''
    villagestring = ''

    pipeline = []
    for woreda_name in woreda_names:
        print(f' ---- {woreda_name} ----')
        data_village, data_grid = load_data(woreda_name)
        (well_location,cost,villages) = find_cheapest_configuration(data_village,data_grid)
        wellstring +=  f' "id" = {well_location} OR '
        print(f'the total costs are {cost}')

        km_pipeline = 0
        for vil in villages:
            villagestring += f'"ID" = {vil} OR '
            km_pipeline += data_grid.at[well_location, vil]
        print(f'km pipeline {km_pipeline / 1000}')


    print('wells')
    print(wellstring)
    print('villages')
    print(villagestring)









