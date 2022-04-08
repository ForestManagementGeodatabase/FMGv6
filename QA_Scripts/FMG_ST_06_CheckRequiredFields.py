# -*- coding: UTF-8 -*-

import arcpy
import FMG_QA_FunctionLibrary
import os

# Get Parameter arguments for script tool
FC_Prism = arcpy.GetParameterAsText(0)
FC_Age = arcpy.GetParameterAsText(1)
FC_Fixed = arcpy.GetParameterAsText(2)

# Check each field collected dataset for required fields
FMG_QA_FunctionLibrary.check_Required_Fields_Prism(FC_Prism)

FMG_QA_FunctionLibrary.check_Required_Fields_Age(FC_Age)

FMG_QA_FunctionLibrary.check_Required_Fields_Fixed(FC_Fixed)
