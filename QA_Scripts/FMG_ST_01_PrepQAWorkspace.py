# -*- coding: UTF-8 -*-

import arcpy
import os, sys, datetime
from datetime import date

# Define Input Parameters
destinationFolder = arcpy.GetParameterAsText(0)
inFixed = arcpy.GetParameterAsText(1)
inPrism = arcpy.GetParameterAsText(2)
inAge = arcpy.GetParameterAsText(3)
inPlot = arcpy.GetParameterAsText(4)

# Define global date string used for naming
tDate = datetime.date.today().strftime('%Y%m%d')

# Create QA Geodatabase
gdbName = 'FMG_FieldData_QA_{0}'.format(tDate)

arcpy.CreateFileGDB_management(out_folder_path = destinationFolder,
                               out_name = gdbName,
                               out_version = 'CURRENT')

arcpy.AddMessage('Working GDB {0} created'.format(gdbName))
                 
# Loop through input datasets, copying out features
FCs = [(inFixed, 'Fixed', 5), (inPrism, 'Prism', 6), (inAge, 'Age', 7), (inPlot, 'Plot', 8)]
                 
for fc in FCs:
    outName = '{0}_QA_{1}'.format(fc[1], tDate)
    outPath = os.path.join(destinationFolder, gdbName + '.gdb', outName)
    arcpy.CopyFeatures_management(in_features = fc[0],
                                  out_feature_class = outPath)
    arcpy.AddMessage('{0} copied to {1}'.format(fc[1], outPath))
    #outFC = arcpy.SetParameterAsText(fc[2], outPath)
    


                     
                 
                                  
                               
