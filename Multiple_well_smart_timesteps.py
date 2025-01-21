import numpy as np
import pandas as pd

def load_data(woreda_name):
    '''Load data from Excel sheets obtained from QGIS'''

    file_path_grid = f"excel/{woreda_name} grid.xlsx"
    data_grid = pd.read_excel(file_path_grid, index_col= 1, header=0)
    data_grid = data_grid.drop('fid', axis=1)
    data_grid.index= data_grid.index.astype(str)
    data_grid['connected'] = [False]*len(data_grid.index)


    file_path_village = f"excel/villages {woreda_name}.xlsx"
    columns_to_use = ['id', 'populationsum', 'elevation1']
    data_village = pd.read_excel(file_path_village, usecols=columns_to_use, index_col= 0)
    data_village.index= data_village.index.astype(str)
    data_village['budget'] = [1.0]*len(data_village.index)
    data_village['connected'] = ['']*len(data_village.index)


    return data_village, data_grid



def connection_cost(village_id, well_id):
    '''Costs to connect a village to a potential well location. Based on distance and elevation difference.
    :param village_id: number of the village
    :param well_id: number of the well'''

    distance_to_village = data_grid.at[well_id,village_id]
    elevation_difference = data_village.at[village_id, "elevation1"] - data_grid.at[well_id, "elevation1"]
    if elevation_difference < 0:
        elevation_difference = 0
    return well_pipeline_ratio * distance_to_village + well_hill_ratio * hydrolic_power(elevation_difference)



def hydrolic_power(heigth):
    ''' Energy needed to pump water up height (in m) in kWh'''
    rho = 1000
    g = 9.81
    Q = 0.03
    etha = 0.70
    hours = 10*365*24
    #energy_price = 0.32
    return  rho * g * heigth * Q * hours / (etha * 1000)

def get_total_costs(data_villages, data_wells):
    '''calculate the total costs (connection and digging cost) for the well configuration found in data_villages and data_wells
    :param data_villages: data frame with villages and corresponding suitability and connections to wells
    :param data_wells: data frame with wells and corresponding suitability'''

    nr_wells = len(data_village['connected'].unique())

    pipeline = 0
    connect_cost = 0
    wells = set()
    for village in data_villages.index:
        connect_cost += connection_cost(village, data_villages.at[village,'connected'])
        wells.add(data_villages.at[village,'connected'])
        pipeline += data_grid.at[data_village.at[village, 'connected'], village]

    suitability_cost = 0
    for well in wells:
        suitability_cost += 1/data_wells.at[well,'suitability1']

    qgis_string = ''
    for well in wells:
        qgis_string += f'"ID" = {well} OR '

    return suitability_cost + connect_cost, qgis_string, nr_wells, pipeline


def try_options(data_village, data_grid, interval):
    '''Calculates whether villages and wells can be connected with their current budget, and how much the offer overshoots
    the opening costs (and how much the budget overshoots the opening costs). If the overshoot is less than 'interval' the
    connection is made.
    :param data_village: data frame with villages and corresponding suitability, budget and connections to wells
    :param data_grid: data frame with wells and corresponding suitability
    :param interval: maximum allowed overshoot (error)
    '''

    for well_i in data_grid.index:

        offer_to_facility_i = []  # list of tuples with offer from j to i and ID of j

        for village_j in data_village.index:
            if data_village.at[village_j, 'connected'] == '':  # j unconnected
                offer_to_facility_i.append(
                    (max(data_village.at[village_j, 'budget'] - connection_cost(village_j, well_i), 0), village_j))

                if data_grid.at[well_i, 'connected']:  # well i is already open and j unconnected
                    budget = data_village.at[village_j, 'budget']
                    cost_i = connection_cost(village_j, well_i)
                    if budget >= cost_i:  # budget of village j is bigger than connection cost to well i
                        if budget - cost_i > interval:
                            return False, data_village, data_grid
                        else:
                            data_village.at[village_j, 'connected'] = well_i  # connect village j to well i

            else:  # j connected
                well_i_prime = data_village.at[village_j, 'connected']
                offer_to_facility_i.append(
                    (max(connection_cost(village_j, well_i_prime) - connection_cost(village_j, well_i), 0), village_j))

        offer_from_unconnected = sum(map(lambda x: x[0], offer_to_facility_i))
        opening_cost = 1 / data_grid.at[well_i, 'suitability1']

        if opening_cost <= offer_from_unconnected:  # total offer received by well i is bigger than opening costs (1/suitability)
            if offer_from_unconnected - opening_cost > interval:
                return False, data_village, data_grid
            else:
                for offer in offer_to_facility_i:  # connect village j to i, for all j with nonzero offer
                    if offer[0] > 0:
                        data_village.at[offer[1], 'connected'] = well_i
                data_grid.at[well_i, 'connected'] = True  # open well i

    return True, data_village, data_grid


def find_connections(data_grid, data_village):
    ''' Apply algorithm from paper to find which wells to open/dig and which villages to connect to it. Takes bigger timesteps
    until connection is found, and backtracks to earliest possible moment of connection by taking small timesteps back.
    :param data_grid: data frame with potential well locations with corresponding suitablity and whether they have been connected to a village yet
    :param data_village: data frame with villages and their budget, and possible connection to a well'''

    nr_unconnected_city = len(data_village.index)

    while nr_unconnected_city > 0:

        nr_unconnected_city = (data_village['connected'].values == '').sum()
        data_village.loc[data_village['connected'] == '', 'budget'] += 0.1  # update budget

        indicator = False
        counter = 0

        while not indicator and counter < 9:
            indicator, data_village, data_grid = try_options(data_village, data_grid, 0.05)
            data_village.loc[data_village['connected'] == '', 'budget'] -= 0.01  # update budget
            counter += 1

        data_village.loc[data_village['connected'] == '', 'budget'] += 0.01  # update budget


    return data_village, data_grid



if __name__ == '__main__':
    # variables

    well_pipeline_ratio = 1 / 5000  # amount of wells per m pipeline
    well_hill_ratio = 1 / (500000 / 0.32)  # amount of wells per m elevation
    percent_to_connect = 1
    woreda_names = ['Basketo SP Woreda', "Bilate Zuria", "Kucha", "Maji", "Melekoza", "Menit Shasha", "Salamago", "South Ari", "Uba Debre Tsehay", "Wulbareg"]

    # initialization
    qgis_string_100percent = ''

    # computations and print results
    for woreda_name in woreda_names:
        data_village, data_grid = load_data(woreda_name)
        data_village, data_grid = find_connections(data_grid, data_village)

        cost, string, nr_wells, pipeline = get_total_costs(data_village, data_grid)
        print(f'{woreda_name} cost = {cost}')
        print(f'nr of wells {nr_wells}')
        print(f'km pipeline {pipeline / 1000}')
        qgis_string_100percent += string
        # with pd.ExcelWriter('results example.xlsx', mode='a') as writer:
        #     data_village.to_excel(writer, sheet_name=f'{woreda_name}2')

    print('wells')
    print(qgis_string_100percent)





