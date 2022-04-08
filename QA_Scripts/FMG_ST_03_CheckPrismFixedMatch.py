# -*- coding: UTF-8 -*-

import arcpy
import FMG_QA_FunctionLibrary
import os

# Get Parameter arguments for script tool
FC_Prism = arcpy.GetParameterAsText(0)
Prism_PlotID = arcpy.GetParameterAsText(1)
FC_Fixed = arcpy.GetParameterAsText(2)
Fixed_PlotID = arcpy.GetParameterAsText(3)

# Check each fixed plot has a prism plot and each prism plot has a fixed plot
FMG_QA_FunctionLibrary.check_Prism_Fixed(FC_Prism = FC_Prism,
                                         Prism_PlotID = Prism_PlotID,
                                         FC_Fixed = FC_Fixed,
                                         Fixed_PlotID = Fixed_PlotID)


                                         
