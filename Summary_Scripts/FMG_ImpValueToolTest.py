#This script is intended to generate a summary table of forestry statistics from the USACE Phase 2 Forest Inventory
#   dataset, and summarize it by user defined fields. Last Updated: 19FEB2013
#This tool calculates importance values on a 300 point scale.

#Notes are above the code they refer to

arcpy.AddMessage('Beginning...')

#import arcpy (the ArcGIS Python module) and env (the environmental settings tools of arcpy) 
import arcpy
from arcpy import env

#The codeblock that creates the customized tool used to remove null values from tables
codeblock = """def removenull(x):
    if x is None:
        return 0
    return x
    """
    
arcpy.AddMessage('Identifying parameters')
#Define parameters for analysis
#   1: input stand summary table
#   2: input spp summary table
#   3: summary level of stand stand and spp summary tables
#   4: output table name and location
stand_sum = arcpy.GetParameterAsText(0)
spp_sum = arcpy.GetParameterAsText(1)
summary_level = arcpy.GetParameterAsText(2)
out_table = arcpy.GetParameterAsText(3)
arcpy.AddMessage('Parameters identified.')
#
arcpy.AddMessage('Setting workspace...')                 
#Sets the workspace to the location of the input table
env.workspace = stand_sum
arcpy.AddMessage('Workspace set.')
#
arcpy.AddMessage('Assembling output table...')
#The code for creating the final output table
out_tablename = out_table.split('\\')[-1]
out_tablepath = out_table.replace(out_tablename, '')
arcpy.CreateTable_management(out_tablepath, out_tablename, spp_sum)
#
arcpy.AddMessage('Creating output table fields...')
#appends the species summary table to the output table
arcpy.Append_management(spp_sum, out_table, "TEST")
#adds additional fields to the output table
arcpy.AddField_management(out_table, "TOT_BA", "DOUBLE")
arcpy.AddField_management(out_table, "TOT_TPA", "DOUBLE")
arcpy.AddField_management(out_table, "TOT_PL", "LONG")
arcpy.AddField_management(out_table, "FREQ", "DOUBLE")
arcpy.AddField_management(out_table, "TOT_FREQ", "DOUBLE")
arcpy.AddField_management(out_table, "REL_BA", "DOUBLE")
arcpy.AddField_management(out_table, "REL_TPA", "DOUBLE")
arcpy.AddField_management(out_table, "REL_FREQ", "DOUBLE")
arcpy.AddField_management(out_table, "IMP_VAL", "DOUBLE")
#
#Joins fields from the stand summary table to the output table
arcpy.JoinField_management(out_table, summary_level, stand_sum, summary_level, ["AV_BA", "AV_TPA", "NUM_PL"])
arcpy.CalculateField_management(out_table, "TOT_BA", "!AV_BA_1!", "PYTHON")
arcpy.CalculateField_management(out_table, "TOT_TPA", "!AV_TPA_1!", "PYTHON")
arcpy.CalculateField_management(out_table, "TOT_PL", "!NUM_PL_1!", "PYTHON")
#
arcpy.AddMessage('Calculating frequencies...')
#Calculates the frequency fields
arcpy.CalculateField_management(out_table, "FREQ", "!NUM_PL!*1.0/!TOT_PL!*1.0", "PYTHON")
scratch_freq = env.scratchWorkspace + "\scratch_freq"
arcpy.Statistics_analysis(out_table, scratch_freq, [["FREQ", "SUM"]],summary_level)
arcpy.AddIndex_management(scratch_freq, summary_level, "freq", "NON_UNIQUE", "NON_ASCENDING")
arcpy.JoinField_management(out_table, summary_level, scratch_freq, summary_level, ["SUM_FREQ"])
arcpy.CalculateField_management(out_table, "TOT_FREQ", "!SUM_FREQ!", "PYTHON")
#
arcpy.AddMessage('Calculating importance values...')
#Calculates relative values of IV factors and IV for each species
arcpy.CalculateField_management(out_table, "REL_BA", "100.0*!AV_BA!/!TOT_BA!", "PYTHON")
arcpy.CalculateField_management(out_table, "REL_TPA", "100.0*!AV_TPA!/!TOT_TPA!", "PYTHON")
arcpy.CalculateField_management(out_table, "REL_FREQ", "100.0*!FREQ!/!TOT_FREQ!", "PYTHON")
arcpy.CalculateField_management(out_table, "IMP_VAL", "!REL_BA! + !REL_TPA! + !REL_FREQ!", "PYTHON")
#
arcpy.AddMessage('Cleaning up table...')
#eliminates unnessecary fields from the output table
arcpy.DeleteField_management(out_table, ["SDG_TPA"])
arcpy.DeleteField_management(out_table, ["SAP_TPA"])
arcpy.DeleteField_management(out_table, ["POL_TPA"])
arcpy.DeleteField_management(out_table, ["SAW_TPA"])
arcpy.DeleteField_management(out_table, ["MAT_TPA"])
arcpy.DeleteField_management(out_table, ["OVM_TPA"])
arcpy.DeleteField_management(out_table, ["SNAG_TPA"])
##arcpy.DeleteField_management(out_table, ["NUM_TR"]) #This has been commented out to preserve the total number of trees at the summary level
arcpy.DeleteField_management(out_table, ["QM_DBH"])
arcpy.DeleteField_management(out_table, ["NUM_PL_1"])
arcpy.DeleteField_management(out_table, ["AV_BA_1"])
arcpy.DeleteField_management(out_table, ["AV_TPA_1"])
arcpy.DeleteField_management(out_table, ["SUM_FREQ"])
arcpy.Delete_management(scratch_freq)
#
arcpy.AddMessage('Importance Values Calculated!')
#End of script
