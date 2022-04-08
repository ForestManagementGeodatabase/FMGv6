#This script is intended to generate a summary table of plot-level importance values  
#   from the USACE Phase 2 Forest Inventory dataset. Last Updated: 28MAR2013

#Comments written above code

arcpy.AddMessage('Beginning...')

#Imports the prefixes for ArcGIS specific codes
import arcpy
from arcpy import env

#Codeblock that removes null values from the output table fields
codeblock = """def removenull(x):
    if x is None:
        return 0
    return x
    """

arcpy.AddMessage('Identifying parameters')
raw_prism = arcpy.GetParameterAsText(0)
PID = arcpy.GetParameterAsText(1)
tr_spp = arcpy.GetParameterAsText(2)
tr_dbh = arcpy.GetParameterAsText(3)
out_table = arcpy.GetParameterAsText(4)
arcpy.AddMessage('Parameters identified.')

arcpy.AddMessage('Setting workspace...')               
env.workspace = raw_prism
arcpy.AddMessage('Workspace set.')

arcpy.AddMessage('Assembling output table...')
out_tablename = out_table.split('\\')[-1]
out_tablepath = out_table.replace(out_tablename, '')
arcpy.CreateTable_management(out_tablepath, out_tablename)

arcpy.AddMessage('Creating output table fields...')
arcpy.AddField_management(out_table, PID, "TEXT")


arcpy.AddMessage('Identifying trees with DBH > 4 and nones/blanks/nulls in ' + tr_spp + ' field...')
tree_prism = str(env.scratchWorkspace) + "\\tree_pr"
arcpy.TableSelect_analysis(raw_prism, tree_prism, 'LOWER("' +tr_spp + '") <> \'none\' and LOWER("' + tr_spp + '") <> \'null\' and \
LOWER("' + tr_spp + '") <> \'\'') # removed tr_dbh + DBH >4 from select query

arcpy.AddMessage('Calculating species densities...')
arcpy.AddField_management(tree_prism, "DENS", "DOUBLE")
arcpy.CalculateField_management(tree_prism, "DENS", "10 / (0.005454 * !"+tr_dbh+"! * !"+tr_dbh+"!)", "PYTHON")

#A list of summarization variables used in other tools
case_two = []
case_two.append(PID)
case_two.append(tr_spp)

arcpy.AddMessage('Calculating species dominances...')
arcpy.Statistics_analysis(tree_prism, out_table, [["DENS", "SUM"]], case_two)
arcpy.AddField_management(out_table, tr_spp, "TEXT")
arcpy.AddField_management(out_table, "DOM", "SHORT")
arcpy.AddField_management(out_table, "RDOM", "DOUBLE")
arcpy.AddField_management(out_table, "DENS", "DOUBLE")
arcpy.AddField_management(out_table, "RDENS", "DOUBLE")
arcpy.AddField_management(out_table, "IV", "DOUBLE")
arcpy.CalculateField_management(out_table, "DOM", "10*!FREQUENCY!", "PYTHON")
arcpy.CalculateField_management(out_table, "DENS", "1.0*!SUM_DENS!", "PYTHON")
arcpy.DeleteField_management(out_table, [["FREQUENCY"], ["SUM_DENS"]])
arcpy.AddIndex_management(out_table, PID, "out_PID", "NON_UNIQUE", "NON_ASCENDING")

                             
arcpy.AddMessage('Calculating relative frequencies and dominances...')
scratch_5 = env.scratchWorkspace + "\scratch_5"
arcpy.Statistics_analysis(out_table, scratch_5, [["DOM", "SUM"], ["DENS", "SUM"]], PID)
arcpy.AddIndex_management(scratch_5, PID, "scratch_5", "NON_UNIQUE", "NON_ASCENDING")
arcpy.JoinField_management(out_table, PID, scratch_5, PID, [["SUM_DOM"], ["SUM_DENS"]])
arcpy.CalculateField_management(out_table, "RDOM", "100.0*((1.0*!DOM!)/(1.0*!SUM_DOM!))", "PYTHON")
arcpy.CalculateField_management(out_table, "RDENS", "100.0*(!DENS!/!SUM_DENS!)", "PYTHON")
arcpy.CalculateField_management(out_table, "IV", "!RDENS! + !RDOM!", "PYTHON")
arcpy.DeleteField_management(out_table, [["SUM_DOM"], ["SUM_DENS"]])

arcpy.Delete_management(tree_prism)
arcpy.Delete_management(scratch_5)



