import numpy as np
import pandas as pd

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



def percentage_to_connect(percentage, data_village, data_grid):
    '''Finds the costs to connect percentage of people and returns the calculation strings for QGIS too. Uses the Star Picking
    method to find the cheapest connections.
    :param percentage: percentage of population to connect to a well
    :param data_grid: data frame with potential well locations with corresponding suitablity and if connected to a village
    :param data_village: data frame with villages and their populations, and connection to a well'''

    # find stars with cheapest cost per capita
    chosen_wells = data_village['connected'].unique()
    stars = []

    for well in chosen_wells:
        chosen_villages = data_village.loc[data_village['connected']==well]
        population = chosen_villages['populationsum'].sum()
        cost = 1/data_grid.at[well,'suitability1']
        for village in chosen_villages.index:
            cost += connection_cost(village,well)
        cost_per_capita = cost/population
        stars.append((cost_per_capita,well,chosen_villages.index,cost,population))

    sorted_stars = sorted(stars, key= lambda x:x[0], reverse = False)

    population = percentage * data_village['populationsum'].sum()
    chosen_stars = []
    i=0
    while population > 0 and i < len(sorted_stars):
        chosen_stars.append(sorted_stars[i])
        population -= sorted_stars[i][-1]
        i += 1

    population += sorted_stars[i-1][-1]
    del chosen_stars[-1]

    # find villages with cheapest cost per capita in last added star

    well_to_divide = sorted_stars[i-1][1]
    villages_to_divide = []
    for village in sorted_stars[i-1][2]:
        villages_to_divide.append((village,connection_cost(village,well_to_divide), connection_cost(village,well_to_divide)/data_village.at[village,'populationsum']))
    sorted_villages_to_divide = sorted(villages_to_divide, key= lambda x:x[2], reverse = False)

    chosen_villages = []
    j=0
    while population > 0 and j < len(sorted_villages_to_divide):
        chosen_villages.append(sorted_villages_to_divide[j])
        population -= data_village.at[sorted_villages_to_divide[j][0],'populationsum']
        j+= 1

    string_village = ''
    villages_final = []
    final_cost = 1/data_grid.at[well_to_divide,'suitability1']
    for vil in chosen_villages:
        final_cost += vil[1]
        string_village += f'"id" = {vil[0]} OR '
        villages_final.append(vil[0])



    string_well = f'"id" = {well_to_divide} OR '

    for star in chosen_stars:
        final_cost += star[3]
        string_well += f'"id" = {star[1]} OR'
        for vil in star[2]:
            string_village += f'"id" = {vil} OR'
            villages_final.append(vil)

    pipeline = 0
    for vil in villages_final:
        pipeline += data_grid.at[data_village.at[vil, 'connected'], vil]

    return final_cost, string_well, string_village, len(chosen_stars) + 1, pipeline



if __name__ == '__main__':
    # variables

    well_pipeline_ratio = 1 / 5000  # amount of wells per m pipeline
    well_hill_ratio = 1 / (500000 / 0.32)  # amount of wells per m elevation
    percent_to_connect = 0.7
    woreda_names = ['Basketo SP Woreda', "Bilate Zuria", "Kucha", "Maji", "Melekoza", "Menit Shasha", "Salamago", "South Ari", "Uba Debre Tsehay", "Wulbareg"]

    # initialization
    qgis_string_village_n_percent = ''
    qgis_string_well_n_percent = ''

    costs = []
    nr_well = []
    km_pipeline = []

    for woreda_name in woreda_names:
        data_village = pd.read_excel('results.xlsx', sheet_name=f'{woreda_name}',index_col= 0)
        data_village.index = data_village.index.astype(str)
        data_village['connected'] = data_village['connected'].astype(str)

        file_path_grid = f"excel/{woreda_name} grid.xlsx"
        data_grid = pd.read_excel(file_path_grid, index_col=1, header=0)
        data_grid = data_grid.drop('fid', axis=1)
        data_grid.index = data_grid.index.astype(str)
        data_grid['connected'] = [False] * len(data_grid.index)

        cost, string_well, string_village, nr_wells, pipeline = percentage_to_connect(percent_to_connect, data_village, data_grid)
        print(f'{woreda_name} cost = {cost}')
        print(f'nr of wells {nr_wells}')
        print(f'km pipeline {pipeline/1000}')
        qgis_string_village_n_percent += string_village
        qgis_string_well_n_percent += string_well
        # with pd.ExcelWriter('results n percent.xlsx', mode='a') as writer:
        #     data_village.to_excel(writer, sheet_name=f'{woreda_name}')

    print('villages')
    print(qgis_string_village_n_percent)
    print('wells')
    print(qgis_string_well_n_percent)






