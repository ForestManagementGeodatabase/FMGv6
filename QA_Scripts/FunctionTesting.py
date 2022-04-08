import arcpy
import os, sys, datetime
import FMG_QA_FunctionLibrary

# Define some input datasets
inPlot = r"D:\FMG_Testing\FMG_FieldCollection_20180815_1.gdb\Plot" 
inFixed = r"D:\FMG_Testing\FMG_FieldCollection_20180815_1.gdb\Fixed"
inPrism = r"D:\FMG_Testing\FMG_FieldCollection_20180815_1.gdb\Prism"
inAge = r"D:\FMG_Testing\FMG_FieldCollection_20180815_1.gdb\Age"

FieldCollect = [inFixed, inPrism, inAge]

# Check fixed plot IDs against Plot locations
##for data in FieldCollect:
##    FMG_QA_FunctionLibrary.check_Plot_IDs(inPlot, 'PLOT', data, 'PLOT')
##    print 'checked {0}'.format(data)
# Ran correctly and quickly, add a master plot id field data type check to function


    
# Check that prism plots have fixed plots and that fixed plots have prism plots
##FMG_QA_FunctionLibrary.check_Prism_Fixed(inPrism, 'PLOT', inFixed, 'PLOT')
# Ran quickly and correctly



# Check that age plots have been collected as prescribed
##FMG_QA_FunctionLibrary.check_Contractor_Age_Plots(FC_Plots = inPlot,
##                                                  Plots_PlotID = 'PLOT',
##                                                  Age_FlagField = 'Age',
##                                                  FC_Age = inAge,
##                                                  Age_PlotID = 'PLOT')
# Ran quickly and correctly, need to watch for the AGE field definition query
# without this being standardized the tool will be more error prone



# Check that fixed plots are within 3 meters of plot center
##FMG_QA_FunctionLibrary.check_Fixed_Offset(FC_PlotLocations = inPlot,
##                                          PlotID_Field = 'PLOT',
##                                          FC_Fixed = inFixed,
##                                          Fixed_PlotID_Field = 'PLOT')
# Ran quickly and correctly - need to pay attention to magnitude of offset:
# large offsets can indicate that the fixed plot has the wrong plot ID



# Check Missing fields for Prism Points
## FMG_QA_FunctionLibrary.check_Required_Fields_Prism(inPrism)
# Ran quickly and correctly



# Check missing fields for Age points
## FMG_QA_FunctionLibrary.check_Required_Fields_Age(inAge)
# Ran quickly and correctly


# Check missing fields for Fixed points
## FMG_QA_FunctionLibrary.check_Required_Fields_Fixed(inFixed)
# Ran Quickly and correctly


