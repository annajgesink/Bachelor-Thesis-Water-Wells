import os # This is is needed in the pyqgis console also
from qgis.core import (
    QgsVectorLayer
)


def make_files(woreda_name,file_path):
    # clip villages to woreda
    processing.run("native:clip", {'INPUT':f'{file_path}potential villages filtered.gpkg',
                                   'OVERLAY':f'{file_path}priority woredas/ADM3_EN_{woreda_name}.gpkg|layername=ADM3_EN_{woreda_name}',
                                   'OUTPUT':f'{file_path}intermediate/villages {woreda_name}.gpkg'})
    # clip wells to woreda
    processing.run("native:clip", {'INPUT':f'{file_path}500m grid clipped to priority filtered.gpkg',
                                   'OVERLAY': f'{file_path}priority woredas/ADM3_EN_{woreda_name}.gpkg|layername=ADM3_EN_{woreda_name}',
                                   'OUTPUT': f'{file_path}intermediate/500m grid {woreda_name}.gpkg'})
    # calculate distances from each well to each village
    processing.run("qgis:distancematrix", {'INPUT':f'{file_path}intermediate/500m grid {woreda_name}.gpkg',
                                           'INPUT_FIELD':'fid',
                                           'TARGET':f'{file_path}intermediate/villages {woreda_name}.gpkg',
                                           'TARGET_FIELD':'fid',
                                           'MATRIX_TYPE':1,
                                           'NEAREST_POINTS':0,
                                           'OUTPUT':f'{file_path}intermediate/{woreda_name} distance matrix.gpkg'})
    # sample all wells on suitability
    processing.run("native:rastersampling", {'INPUT':f'{file_path}intermediate/{woreda_name} distance matrix.gpkg',
                                             'RASTERCOPY':f'{file_path}suitability.tif','COLUMN_PREFIX':'suitability',
                                             'OUTPUT':f'{file_path}intermediate/{woreda_name} grid.gpkg'})
    # sample all wells on elevation
    processing.run("native:rastersampling", {'INPUT':f'{file_path}intermediate/{woreda_name} grid.gpkg',
                                             'RASTERCOPY':f'{file_path}Mosaic2.tif',
                                             'COLUMN_PREFIX':'elevation',
                                             'OUTPUT':f'{file_path}intermediate/{woreda_name} grid 2.gpkg'})
    # export wells to Excel spreadsheet
    processing.run("native:exporttospreadsheet",
                   {'LAYERS':f'{file_path}intermediate/{woreda_name} grid 2.gpkg',
                                                  'OUTPUT':f'{file_path}excel/{woreda_name} grid.xlsx' })
    #export villages to Excel spreadsheet
    processing.run("native:exporttospreadsheet",
                   {'LAYERS': f'{file_path}intermediate/villages {woreda_name}.gpkg',
                    'OUTPUT': f'{file_path}excel/villages {woreda_name}.xlsx'})

woreda_names = ['Basketo SP Woreda', "Bilate Zuria", "Kucha", "Maji", "Melekoza", "Menit Shasha", "Salamago", "South Ari", "Uba Debre Tsehay", "Wulbareg"]
file_path = 'C:/Users/annaj/Desktop/uni/eerste project/'

for woreda_name in woreda_names:
    make_files(woreda_name, file_path)

