#This script is intended to generate a health summary table from the USACE Phase 2 Forest Inventory
#   dataset, and summarize it by user defined fields. Last Updated: 27FEB2013

#Comments written above code

arcpy.AddMessage('Beginning...')

#Imports the prefixes for ArcGIS specific codes
import arcpy
from arcpy import env

# Change - 20190228 Overwrite Output enabled
arcpy.env.overwriteOutput = True

#Codeblock that removes null values from the output table fields
codeblock = """def removenull(x):
    if x is None:
        return 0
    return x
    """

#codeblock that reads diameters and determines their size class
codeblock2 = """def sizeclass(y, x):
    if y.upper() == "D":
	return "SNAG"
    elif x < 12: 
        return "POL"
    elif x >= 12 and x < 18 :
        return "SAW"
    elif x >= 18 and x < 24 :
        return "MAT"
    elif x >= 24 :
        return "OVM"
    else:
        return "ERROR" """
    
#Identifies the user-provided parameters from the GUI
arcpy.AddMessage('Identifying parameters')
raw_prism = arcpy.GetParameterAsText(0)
PID = arcpy.GetParameterAsText(1)
tr_spp = arcpy.GetParameterAsText(2)
tr_dbh = arcpy.GetParameterAsText(3)
tr_hlth = arcpy.GetParameterAsText(4)
summary_level = arcpy.GetParameterAsText(5)
out_table = arcpy.GetParameterAsText(6)
sum_spp = arcpy.GetParameterAsText(7)
sum_size = arcpy.GetParameterAsText(8)
sum_mast = arcpy.GetParameterAsText(9)
tr_mast = arcpy.GetParameterAsText(10)

arcpy.AddMessage('Parameters identified.')

#Sets the workplace (where temporary files are written)
arcpy.AddMessage('Setting workspace...')                
env.workspace = raw_prism
arcpy.AddMessage('Workspace set.')

arcpy.AddMessage('Assembling output table...')
out_tablename = out_table.split('\\')[-1]
out_tablepath = out_table.replace(out_tablename, '')
arcpy.CreateTable_management(out_tablepath, out_tablename)

arcpy.AddMessage('Identifying nones/blanks/nulls in ' + tr_spp + ' field and trees with DBH > 4...')
tree_prism = str(env.scratchWorkspace) + "\\tree_pr"
arcpy.TableSelect_analysis(raw_prism, tree_prism, 'LOWER("' +tr_spp + '") <> \'none\' and LOWER("' + tr_spp + '") <> \'null\' and \
LOWER("' + tr_spp + '") <> \'\'') # removed tr_dbh >4 from select query

#A list of summarization variables used in other tools
sumby = []
sumby.append(summary_level)
sumby.append(tr_hlth)

#Adds tree species to summary list if select in GUI
if sum_spp.lower() == "true":
    arcpy.AddMessage('Will summarize by species...')
    sumby.append(tr_spp)
else:
    pass

#Adds size class to summary list if select in GUI
if sum_size.lower() == "true":
    arcpy.AddMessage('Determining tree size classes...')
    arcpy.AddField_management(tree_prism, "SIZE_CLASS", "TEXT")
    arcpy.CalculateField_management(tree_prism, "SIZE_CLASS", "sizeclass(!"+tr_hlth+ "! , !" + tr_dbh + "!)", "PYTHON", codeblock2)
    arcpy.AddMessage('Will summarize by size class...')
    sumby.append("SIZE_CLASS")
else:
    pass

#Adds mast type to summary list if select in GUI
if sum_mast.lower() == "true":
    arcpy.AddMessage('Will summarize by mast type...')
    sumby.append(tr_mast)
else:
    pass

arcpy.AddMessage('Calculating # of trees and TPA expansion factors...')
arcpy.AddField_management(tree_prism, "DENS", "DOUBLE")
arcpy.AddField_management(tree_prism, "BA", "DOUBLE")
arcpy.CalculateField_management(tree_prism, "DENS", "10 / (0.005454 * !"+tr_dbh+"! * !"+tr_dbh+"!)", "PYTHON")
arcpy.Statistics_analysis(tree_prism, out_table, [["DENS", "SUM"]], sumby)
arcpy.AddField_management(out_table, "AV_TPA", "DOUBLE")
arcpy.CalculateField_management(out_table, "AV_TPA", "!SUM_DENS!", "PYTHON")
arcpy.AddIndex_management(out_table, summary_level, "out_table", "NON_UNIQUE", "NON_ASCENDING")

arcpy.AddMessage('Calculating total # of trees for each '+summary_level+'...')
scratch_pl3 = env.scratchWorkspace + "\scratch_pl3"
arcpy.Statistics_analysis(tree_prism, scratch_pl3, [[summary_level, "FIRST"]], summary_level)
arcpy.AddField_management(scratch_pl3, "TOT_COUNT", "DOUBLE")
arcpy.CalculateField_management(scratch_pl3, "TOT_COUNT", "!FREQUENCY!", "PYTHON")
arcpy.AddIndex_management(scratch_pl3, summary_level, "scratch_pl3", "NON_UNIQUE", "NON_ASCENDING")
arcpy.JoinField_management(out_table, summary_level, scratch_pl3, summary_level, "TOT_COUNT")

arcpy.AddMessage('Calculating average trees per acre...')
case_pl = []
case_pl.append(summary_level)
case_pl.append(PID)
scratch_pl1 = env.scratchWorkspace + "\scratch_pl1"
arcpy.Statistics_analysis(raw_prism, scratch_pl1, [[summary_level, "COUNT"]], case_pl)
scratch_pl2 = env.scratchWorkspace + "\scratch_pl2"
arcpy.Statistics_analysis(scratch_pl1, scratch_pl2, [[summary_level, "COUNT"]], summary_level)
arcpy.AddField_management(scratch_pl2, "NUM_PL", "SHORT")
arcpy.CalculateField_management(scratch_pl2, "NUM_PL", "!FREQUENCY!", "PYTHON")
arcpy.AddIndex_management(scratch_pl2, summary_level, "summary_pl2", "NON_UNIQUE", "NON_ASCENDING")
arcpy.JoinField_management(out_table, summary_level, scratch_pl2, summary_level, ["NUM_PL"])
arcpy.Delete_management(scratch_pl1)
arcpy.Delete_management(scratch_pl2)

#Calculates Average TPA
arcpy.CalculateField_management(out_table, "AV_TPA", "!AV_TPA! / !NUM_PL!", "PYTHON")

arcpy.AddMessage('Calculating percent composition...')
arcpy.AddField_management(out_table, "COUNT_COMP", "DOUBLE")
arcpy.CalculateField_management(out_table, "COUNT_COMP", "100 * !FREQUENCY! / !TOT_COUNT!", "PYTHON")


arcpy.AddMessage('Cleaning output table...')
arcpy.DeleteField_management(out_table, ["FREQUENCY", "TOT_COUNT", "SUM_DENS", "NUM_PL"])
arcpy.Delete_management(scratch_pl3)
arcpy.Delete_management(tree_prism)

arcpy.AddMessage('Output table created.')
