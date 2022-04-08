# -*- coding: UTF-8 -*-

import arcpy
import FMG_QA_FunctionLibrary
import os

# Get Parameter arguments for script tool
FC_Plots = arcpy.GetParameterAsText(0)
Plots_PlotID = arcpy.GetParameterAsText(1)
Age_FlagField = arcpy.GetParameterAsText(2)
FC_Age = arcpy.GetParameterAsText(3)
Age_PlotID = arcpy.GetParameterAsText(4)

# Verify required age trees have been collected
FMG_QA_FunctionLibrary.check_Contractor_Age_Plots(FC_Plots = FC_Plots,
                                                  Plots_PlotID = Plots_PlotID,
                                                  Age_FlagField = Age_FlagField,
                                                  FC_Age = FC_Age,
                                                  Age_PlotID = Age_PlotID)

                                                  
                                                  
