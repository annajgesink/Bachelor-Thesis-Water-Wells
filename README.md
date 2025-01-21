This repository was made to share the python code used to obtain numerical results for my Bachelor Thesis in which I determine new water well locations for the SNNP Region in Ethiopia. The algorithms used can be
found in my report. The following files have been made and should be used as follows:

One_Well_algorithm.py: computes, for a given percentage of the population to connect, the location of one well, the costs, villages connected and the total km of pipeline. 
                    Next to that it gives QGIS computation strings that can be used to obtain maps with the well and connected villages in QGIS.
                    Uses as input the excel sheets 'woreda_name grid' and 'villages woreda_name' in the folder 'excel' in the same directory.
                    The results are printed to the terminal.

Multiple_Well_algorithm.py: computes the location of multiple wells, the costs, villages connected and the total km of pipeline. 
                    Next to that it gives QGIS computation strings that can be used to obtain maps with the wells and connected villages in QGIS.
                    Uses as input the excel sheets 'woreda_name grid' and 'villages woreda_name' in the folder 'excel' in the same directory.
                    The results are printed to the terminal and the configuration is saved in an excel sheet called 'results.xlsx', which needs to be created before executing and placed in the same directory.

Star_Picking_algorithm.py: takes the configuration as obtained by the Multiple_Well_algorithm.py and saved in 'results.xlsx' and calculates the location of multiple wells, the costs, 
                    villages connected and the total km of pipeline for a given percentage of the population desired to connect to a well.
                    Next to that it gives QGIS computation strings that can be used to obtain maps with the wells and connected villages in QGIS.
                    Uses as input the excel sheet 'woreda_name grid' in the folder 'excel' in the same directory and the aforementioned 'results.xlsx'.
                    The results are printed to the terminal and the configuration is saved in an excel sheet called 'results n percent.xlsx', which needs to be created before executing and placed in the same directory.

Multiple_well_smart_timesteps.py: Does the same as Multiple_Well_algorithm.py but takes smarter timesteps to reduce computation time.

qgiscode.py: obtains code to be executed in the PyGIS plugin in QGIS. In qgiscode.py the files 'potential villages filtered.gpkg' with the 5km grid sampled for population and elevation 
                    and '500m grid clipped to priority filtered' with the 500m grid are combined to obtain the required Excel's with distances, suitability, elevation and population. 
                    Local folders 'intermediate' and 'excel' are required for execution.
