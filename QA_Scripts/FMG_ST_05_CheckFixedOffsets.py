# -*- coding: UTF-8 -*-

import arcpy
import FMG_QA_FunctionLibrary
import os

# Get Parameter arguments for script tool
FC_PlotLocations = arcpy.GetParameterAsText(0)
PlotID_Field = arcpy.GetParameterAsText(1)
FC_Fixed = arcpy.GetParameterAsText(2)
Fixed_PlotID_Field = arcpy.GetParameterAsText(3)

# Check fixed plot offset from plot centers
FMG_QA_FunctionLibrary.check_Fixed_Offset(FC_PlotLocations = FC_PlotLocations,
                                          PlotID_Field = PlotID_Field,
                                          FC_Fixed = FC_Fixed,
                                          Fixed_PlotID_Field = Fixed_PlotID_Field)
