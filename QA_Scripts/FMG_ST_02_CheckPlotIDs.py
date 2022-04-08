# -*- coding: UTF-8 -*-

import arcpy
import FMG_QA_FunctionLibrary
import os

# Get Parameter arguments for script tool
FC_Master = arcpy.GetParameterAsText(0)
Master_PlotID_Field = arcpy.GetParameterAsText(1)
FC_Check = arcpy.GetParameterAsText(2)
Check_PlotID_Field = arcpy.GetParameterAsText(3)

# Check PlotIDs
FMG_QA_FunctionLibrary.check_Plot_IDs(FC_Master = FC_Master,
                                      Master_PlotID_Field = Master_PlotID_Field,
                                      FC_Check = FC_Check,
                                      Check_PlotID_Field = Check_PlotID_Field)





                                      
