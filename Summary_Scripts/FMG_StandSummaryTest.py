#This script is intended to generate a summary table of forestry statistics from the USACE Phase 2 Forest Inventory
#   dataset, and summarize it by user defined fields. Last Updated: 17MAY2013

#Comments written above code

arcpy.AddMessage('Beginning...')

#Imports the prefixes for ArcGIS specific codes
import arcpy
from arcpy import env

#Codeblock that removes null values from the output table fields
codeblock = """def removenull(x):
    if x > 0:
        return x
    else:
        return 0"""

arcpy.env.overwriteOutput = True
    
arcpy.AddMessage('Identifying parameters')
raw_prism = arcpy.GetParameterAsText(0)
PID = arcpy.GetParameterAsText(1)
tr_spp = arcpy.GetParameterAsText(2)
tr_dbh = arcpy.GetParameterAsText(3)
tr_hlth = arcpy.GetParameterAsText(4)
mast_type = arcpy.GetParameterAsText(5)
notes = arcpy.GetParameterAsText(6)
summary_level = arcpy.GetParameterAsText(7)
out_table = arcpy.GetParameterAsText(8)
arcpy.AddMessage('Parameters identified.')

arcpy.AddMessage('Setting workspace...')               
env.workspace = raw_prism
arcpy.AddMessage('Workspace set.')

arcpy.AddMessage('Assembling output table...')
out_tablename = out_table.split('\\')[-1]
out_tablepath = out_table.replace(out_tablename, '')
arcpy.CreateTable_management(out_tablepath, out_tablename)

arcpy.AddMessage('Creating output table fields...')
arcpy.AddField_management(out_table, summary_level, "TEXT")
arcpy.AddField_management(out_table, "AV_BA", "DOUBLE")
arcpy.AddField_management(out_table, "AV_TPA", "DOUBLE")
arcpy.AddField_management(out_table, "POL_TPA", "DOUBLE")
arcpy.AddField_management(out_table, "SAW_TPA", "DOUBLE")
arcpy.AddField_management(out_table, "MAT_TPA", "DOUBLE")
arcpy.AddField_management(out_table, "OVM_TPA", "DOUBLE")
arcpy.AddField_management(out_table, "SNAG_TPA", "DOUBLE")
arcpy.AddField_management(out_table, "HRD_MAST", "DOUBLE")
arcpy.AddField_management(out_table, "SFT_MAST", "DOUBLE")
arcpy.AddField_management(out_table, "NUM_TR", "LONG")
arcpy.AddField_management(out_table, "NUM_PL", "LONG")
arcpy.AddField_management(out_table, "SPP_RICH", "LONG")
arcpy.AddField_management(out_table, "QM_DBH", "DOUBLE")
arcpy.AddField_management(out_table, "NUM_NOTES", "LONG")
arcpy.AddField_management(out_table, "SCRATCH", "TEXT")
arcpy.AddMessage('Output table fields created...')

arcpy.AddMessage('Calculating fields...')

arcpy.AddMessage('Identifying nones/blanks/nulls in ' + tr_spp + ' field...')
tree_prism = str(env.scratchWorkspace) + "\\tree_pr"
arcpy.TableSelect_analysis(raw_prism, tree_prism, tr_dbh + '>4 and LOWER("' +tr_spp + '") <> \'none\' and LOWER("' + tr_spp + '") <> \'null\' and \
LOWER("' + tr_spp + '") <> \'\'')

arcpy.AddMessage('Calculating NUM_PL and NUM_NOTE fields...')
#A list of summarization variables used in other tools
case_three = []
case_three.append(summary_level)
case_three.append(PID)

##Counts the number of plots and notes for each class within the summary level
scratch_4 = env.scratchWorkspace + "\scratch_4"
arcpy.Statistics_analysis(raw_prism, scratch_4, [[PID, "COUNT"], [notes, "COUNT"]], case_three)
arcpy.AddField_management(scratch_4, "NOTES", "LONG")
arcpy.AddField_management(scratch_4, "SCRATCH", "TEXT")
arcpy.CalculateField_management(scratch_4, "NOTES", "!COUNT_"+str(notes)+"!", "PYTHON")
arcpy.CalculateField_management(scratch_4, "NOTES", "removenull(!NOTES!)", "PYTHON", codeblock)
scratch_5 = env.scratchWorkspace + "\scratch_5"
arcpy.Statistics_analysis(scratch_4, scratch_5, [[PID, "COUNT"], ["NOTES", "SUM"]], summary_level)
arcpy.Append_management(scratch_5, out_table, "NO_TEST")
arcpy.JoinField_management(out_table, summary_level, scratch_5, summary_level, ["FREQUENCY"])
arcpy.CalculateField_management(out_table, "NUM_PL", "0 + !FREQUENCY!", "PYTHON")
arcpy.DeleteField_management(out_table, ["FREQUENCY"])
arcpy.JoinField_management(out_table, summary_level, scratch_5, summary_level, ["SUM_NOTES"])
arcpy.CalculateField_management(out_table, "SUM_NOTES", "removenull(!SUM_NOTES!)", "PYTHON", codeblock)
arcpy.CalculateField_management(out_table, "NUM_NOTES", "0.0 + !SUM_NOTES!", "PYTHON")
arcpy.DeleteField_management(out_table, ["SUM_NOTES"])
arcpy.Delete_management(scratch_4)
arcpy.Delete_management(scratch_5)

arcpy.AddMessage('Calculating SPP_RICH field...')
#A list of summarization variables used in other tools
case_two = []
case_two.append(summary_level)
case_two.append(tr_spp)

scratch_2 = env.scratchWorkspace + "\scratch_2"
arcpy.Statistics_analysis(tree_prism, scratch_2, [[tr_spp, "COUNT"]], case_two)
scratch_3 = env.scratchWorkspace + "\scratch_3"
arcpy.Statistics_analysis(scratch_2, scratch_3, [[tr_spp, "COUNT"]], summary_level)
arcpy.JoinField_management(out_table, summary_level, scratch_3, summary_level, ["FREQUENCY"])
arcpy.CalculateField_management(out_table, "FREQUENCY", "removenull(!FREQUENCY!)", "PYTHON")
arcpy.CalculateField_management(out_table, "SPP_RICH", "0 + !FREQUENCY!", "PYTHON")
arcpy.DeleteField_management(out_table, ["FREQUENCY"])
arcpy.Delete_management(scratch_2)
arcpy.Delete_management(scratch_3)

arcpy.AddMessage('Calculating NUM_TR field...')
scratch_6 = env.scratchWorkspace + "\scratch_6"
arcpy.Statistics_analysis(tree_prism, scratch_6, [[PID, "COUNT"]], summary_level)
arcpy.JoinField_management(out_table, summary_level, scratch_6, summary_level, ["FREQUENCY"])
arcpy.CalculateField_management(out_table, "FREQUENCY", "removenull(!FREQUENCY!)", "PYTHON")
arcpy.CalculateField_management(out_table, "NUM_TR", "0 + !FREQUENCY!", "PYTHON")
arcpy.DeleteField_management(out_table, ["FREQUENCY"])
arcpy.Delete_management(scratch_6)

arcpy.AddMessage('Calculating AV_BA field...')
arcpy.CalculateField_management(out_table, "AV_BA", "( 10.00 * !NUM_TR! ) / !NUM_PL!", "PYTHON")
arcpy.CalculateField_management(out_table, "AV_BA", "removenull(!AV_BA!)", "PYTHON")
arcpy.AddMessage('Calculating all TPA fields...')

arcpy.AddMessage('Calculating POL_TPA field...')
scratch_11 = env.scratchWorkspace + "\scratch_11"
tree_pol = str(env.scratchWorkspace)+"\\tree_pol"
arcpy.TableSelect_analysis(tree_prism, tree_pol, '"'+tr_dbh+'" >= 5 AND "'+tr_dbh+'" <12 AND LOWER("'+tr_hlth+'")<> \'d\'')
arcpy.AddField_management(tree_pol, "DENS", "DOUBLE")
arcpy.CalculateField_management(tree_pol, "DENS", "10/(!"+tr_dbh+"!*!"+tr_dbh+"!*0.005454)", "PYTHON")
arcpy.Statistics_analysis(tree_pol, scratch_11, [["DENS", "SUM"]], summary_level)
arcpy.JoinField_management(out_table, summary_level, scratch_11, summary_level, ["SUM_DENS"])
arcpy.CalculateField_management(out_table, "POL_TPA", "1.0 * !SUM_DENS! / !NUM_PL!", "PYTHON")
arcpy.CalculateField_management(out_table, "POL_TPA", "removenull(!POL_TPA!)", "PYTHON", codeblock)
arcpy.DeleteField_management(out_table, ["SUM_DENS"])
arcpy.Delete_management(scratch_11)
arcpy.Delete_management(tree_pol)

arcpy.AddMessage('Calculating SAW_TPA field...')
scratch_12 = env.scratchWorkspace + "\scratch_12"
tree_saw = str(env.scratchWorkspace)+"\\tree_saw"
arcpy.TableSelect_analysis(tree_prism, tree_saw, '"'+tr_dbh+'">=12 AND "'+tr_dbh+'"<18 AND LOWER("'+tr_hlth+'")<>\'d\'')
arcpy.AddField_management(tree_saw, "DENS", "DOUBLE")
arcpy.CalculateField_management(tree_saw, "DENS", "10/(!"+tr_dbh+"!*!"+tr_dbh+"!*0.005454)", "PYTHON")
arcpy.Statistics_analysis(tree_saw, scratch_12, [["DENS", "SUM"]], summary_level)
arcpy.JoinField_management(out_table, summary_level, scratch_12, summary_level, ["SUM_DENS"])
arcpy.CalculateField_management(out_table, "SAW_TPA", "1.0 * !SUM_DENS! / !NUM_PL!", "PYTHON")
arcpy.CalculateField_management(out_table, "SAW_TPA", "removenull(!SAW_TPA!)", "PYTHON", codeblock)
arcpy.DeleteField_management(out_table, ["SUM_DENS"])
arcpy.Delete_management(scratch_12)
arcpy.Delete_management(tree_saw)

arcpy.AddMessage('Calculating MAT_TPA field...')
scratch_13 = env.scratchWorkspace + "\scratch_13"
tree_mat = str(env.scratchWorkspace)+"\\tree_mat"
arcpy.TableSelect_analysis(tree_prism, tree_mat, '"'+tr_dbh+'">=18 AND "'+tr_dbh+'"<24 AND LOWER("'+tr_hlth+'")<>\'d\'')
arcpy.AddField_management(tree_mat, "DENS", "DOUBLE")
arcpy.CalculateField_management(tree_mat, "DENS", "10/(!"+tr_dbh+"!*!"+tr_dbh+"!*0.005454)", "PYTHON")
arcpy.Statistics_analysis(tree_mat, scratch_13, [["DENS", "SUM"]], summary_level)
arcpy.JoinField_management(out_table, summary_level, scratch_13, summary_level, ["SUM_DENS"])
arcpy.CalculateField_management(out_table, "MAT_TPA", "1.0 * !SUM_DENS! / !NUM_PL!", "PYTHON")
arcpy.CalculateField_management(out_table, "MAT_TPA", "removenull(!MAT_TPA!)", "PYTHON", codeblock)
arcpy.DeleteField_management(out_table, ["SUM_DENS"])
arcpy.Delete_management(scratch_13)
arcpy.Delete_management(tree_mat)

arcpy.AddMessage('Calculating OVM_TPA field...')
scratch_14 = env.scratchWorkspace + "\scratch_14"
tree_ovm = str(env.scratchWorkspace)+"\\tree_ovm"
arcpy.TableSelect_analysis(tree_prism, tree_ovm, ('"'+tr_dbh+'">=24 AND LOWER("'+tr_hlth+'")<>\'d\''))
arcpy.AddField_management(tree_ovm, "DENS", "DOUBLE")
arcpy.CalculateField_management(tree_ovm, "DENS", "10/(!"+tr_dbh+"!*!"+tr_dbh+"!*0.005454)", "PYTHON")
arcpy.Statistics_analysis(tree_ovm, scratch_14, [["DENS", "SUM"]], summary_level)
arcpy.JoinField_management(out_table, summary_level, scratch_14, summary_level, ["SUM_DENS"])
arcpy.CalculateField_management(out_table, "OVM_TPA", "1.0 * !SUM_DENS! / !NUM_PL!", "PYTHON")
arcpy.CalculateField_management(out_table, "OVM_TPA", "removenull(!OVM_TPA!)", "PYTHON", codeblock)
arcpy.DeleteField_management(out_table, ["SUM_DENS"])
arcpy.Delete_management(scratch_14)
arcpy.Delete_management(tree_ovm)

arcpy.AddMessage('Calculating SNAG_TPA field...')
scratch_8 = env.scratchWorkspace + "\scratch_8"
tree_snag = str(env.scratchWorkspace)+"\\tree_snag"
arcpy.TableSelect_analysis(tree_prism, tree_snag, 'LOWER("'+tr_hlth+'")=\'snag\' OR LOWER("'+tr_hlth+'")=\'dead\' OR LOWER("'+tr_hlth+'")=\'d\'')
arcpy.AddField_management(tree_snag, "DENS", "DOUBLE")
arcpy.CalculateField_management(tree_snag, "DENS", "10/(!"+tr_dbh+"!*!"+tr_dbh+"!*0.005454)", "PYTHON")
arcpy.Statistics_analysis(tree_snag, scratch_8, [["DENS", "SUM"]], summary_level)
arcpy.JoinField_management(out_table, summary_level, scratch_8, summary_level, ["SUM_DENS"])
arcpy.CalculateField_management(out_table, "SNAG_TPA", "1.0 * !SUM_DENS! / !NUM_PL!", "PYTHON")
arcpy.CalculateField_management(out_table, "SNAG_TPA", "removenull(!SNAG_TPA!)", "PYTHON", codeblock)
arcpy.DeleteField_management(out_table, ["SUM_DENS"])
arcpy.Delete_management(scratch_8)
arcpy.Delete_management(tree_snag)

arcpy.AddMessage('Calculating AV_TPA field...')
arcpy.CalculateField_management(out_table, "AV_TPA", "0.0 + 1.0*!POL_TPA! + 1.0*!SAW_TPA! + 1.0*!MAT_TPA! + 1.0*!OVM_TPA! + 1.0*!SNAG_TPA!", "PYTHON")
arcpy.CalculateField_management(out_table, "AV_TPA", "removenull(!AV_TPA!)", "PYTHON", codeblock)

arcpy.AddMessage('Calculating HRD_MAST field...')
scratch_9 = env.scratchWorkspace + "\scratch_9"
scratch_hmast = env.scratchWorkspace + "\scratch_hmast"
arcpy.TableSelect_analysis(tree_prism, scratch_9, 'LOWER(mast_type) = \'hard\' AND LOWER("'+tr_hlth+'")<>\'d\'')
arcpy.AddField_management(scratch_9, "DENS", "DOUBLE")
arcpy.CalculateField_management(scratch_9, "DENS", "10/(!"+tr_dbh+"!*!"+tr_dbh+"!*0.005454)", "PYTHON")
arcpy.Statistics_analysis(scratch_9, scratch_hmast, [["DENS", "SUM"]], summary_level)
arcpy.JoinField_management(out_table, summary_level, scratch_hmast, summary_level, ["SUM_DENS"])
arcpy.CalculateField_management(out_table, "HRD_MAST", "1.0 * !SUM_DENS! / !NUM_PL!", "PYTHON")
arcpy.CalculateField_management(out_table, "HRD_MAST", "removenull(!HRD_MAST!)", "PYTHON", codeblock)
arcpy.DeleteField_management(out_table, ["SUM_DENS"])
arcpy.Delete_management(scratch_9)
arcpy.Delete_management(scratch_hmast)

arcpy.AddMessage('Calculating SFT_MAST field...')
scratch_10 = env.scratchWorkspace + "\scratch_10"
scratch_smast = env.scratchWorkspace + "\scratch_smast"
arcpy.TableSelect_analysis(tree_prism, scratch_10, 'LOWER(mast_type) = \'soft\' AND LOWER("'+tr_hlth+'")<>\'d\'')
arcpy.AddField_management(scratch_10, "DENS", "DOUBLE")
arcpy.CalculateField_management(scratch_10, "DENS", "10/(!"+tr_dbh+"!*!"+tr_dbh+"!*0.005454)", "PYTHON")
arcpy.Statistics_analysis(scratch_10, scratch_smast, [["DENS", "SUM"]], summary_level)
arcpy.JoinField_management(out_table, summary_level, scratch_smast, summary_level, ["SUM_DENS"])
arcpy.CalculateField_management(out_table, "SFT_MAST", "1.0 * !SUM_DENS! / !NUM_PL!", "PYTHON")
arcpy.CalculateField_management(out_table, "SFT_MAST", "removenull(!SFT_MAST!)", "PYTHON", codeblock)
arcpy.DeleteField_management(out_table, ["SUM_DENS"])
arcpy.Delete_management(scratch_10)
arcpy.Delete_management(scratch_smast)

arcpy.AddMessage('Calculating QM_DBH field...')
arcpy.CalculateField_management(out_table, "QM_DBH", "0.0 + ((!AV_BA!/!AV_TPA!)/(0.005454))**(0.5)", "PYTHON")
arcpy.CalculateField_management(out_table, "SCRATCH", "removenull(!QM_DBH!)", "PYTHON")
arcpy.CalculateField_management(out_table, "QM_DBH", "!SCRATCH!", "PYTHON")

arcpy.AddMessage('Cleaning output table...')
arcpy.DeleteField_management(out_table, ["SCRATCH"])
arcpy.Delete_management(tree_prism)
arcpy.CalculateField_management(out_table, "POL_TPA", "removenull(!POL_TPA!)", "PYTHON", codeblock)
arcpy.CalculateField_management(out_table, "SAW_TPA", "removenull(!SAW_TPA!)", "PYTHON", codeblock)
arcpy.CalculateField_management(out_table, "MAT_TPA", "removenull(!MAT_TPA!)", "PYTHON", codeblock)
arcpy.CalculateField_management(out_table, "OVM_TPA", "removenull(!OVM_TPA!)", "PYTHON", codeblock)
arcpy.CalculateField_management(out_table, "SNAG_TPA", "removenull(!SNAG_TPA!)", "PYTHON", codeblock)
arcpy.CalculateField_management(out_table, "AV_TPA", "removenull(!AV_TPA!)", "PYTHON", codeblock)
arcpy.CalculateField_management(out_table, "HRD_MAST", "removenull(!HRD_MAST!)", "PYTHON", codeblock)
arcpy.CalculateField_management(out_table, "SFT_MAST", "removenull(!SFT_MAST!)", "PYTHON", codeblock)
arcpy.CalculateField_management(out_table, "NUM_TR", "removenull(!NUM_TR!)", "PYTHON", codeblock)
arcpy.CalculateField_management(out_table, "NUM_PL", "removenull(!NUM_PL!)", "PYTHON", codeblock)
arcpy.CalculateField_management(out_table, "QM_DBH", "removenull(!QM_DBH!)", "PYTHON", codeblock)
arcpy.CalculateField_management(out_table, "NUM_NOTES", "removenull(!NUM_NOTES!)", "PYTHON", codeblock)


arcpy.AddMessage('Output table created.')

