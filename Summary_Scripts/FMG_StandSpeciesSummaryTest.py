#This script is intended to generate a species summary table from the USACE Phase 2 Forest Inventory
#   dataset, and summarize it by user defined fields. Last Updated: 10JUL2013

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
    
arcpy.AddMessage('Identifying parameters')
raw_prism = arcpy.GetParameterAsText(0)
PID = arcpy.GetParameterAsText(1)
tr_spp = arcpy.GetParameterAsText(2)
tr_dbh = arcpy.GetParameterAsText(3)
tr_hlth = arcpy.GetParameterAsText(4)
summary_level = arcpy.GetParameterAsText(5)
out_table = arcpy.GetParameterAsText(6)
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
arcpy.AddField_management(out_table, tr_spp, "TEXT")
arcpy.AddField_management(out_table, "AV_BA", "DOUBLE")
arcpy.AddField_management(out_table, "AV_TPA", "DOUBLE")
arcpy.AddField_management(out_table, "POL_TPA", "DOUBLE")
arcpy.AddField_management(out_table, "SAW_TPA", "DOUBLE")
arcpy.AddField_management(out_table, "MAT_TPA", "DOUBLE")
arcpy.AddField_management(out_table, "OVM_TPA", "DOUBLE")
arcpy.AddField_management(out_table, "SNAG_TPA", "DOUBLE")
arcpy.AddField_management(out_table, "NUM_TR", "LONG")
arcpy.AddField_management(out_table, "NUM_PL", "LONG")
arcpy.AddField_management(out_table, "TOT_PL", "LONG")
arcpy.AddField_management(out_table, "QM_DBH", "DOUBLE")
arcpy.AddField_management(out_table, "SCRATCH", "TEXT")
arcpy.AddField_management(out_table, "JOINFIELD", "TEXT")
arcpy.AddIndex_management(out_table, summary_level, "summary_out", "NON_UNIQUE", "NON_ASCENDING")
arcpy.AddMessage('Output table fields created...')

arcpy.AddMessage('Calculating fields...')

arcpy.AddMessage('Identifying trees with DBH > 4 and nones/blanks/nulls in ' + tr_spp + ' field...')
tree_prism = str(env.scratchWorkspace) + "\\tree_pr"
arcpy.TableSelect_analysis(raw_prism, tree_prism, tr_dbh + '>4 and LOWER("' +tr_spp + '") <> \'none\' and LOWER("' + tr_spp + '") <> \'null\' and \
LOWER("' + tr_spp + '") <> \'\'')

arcpy.AddMessage('Calculating NUM_TR and NUM_PL fields...')
#A list of summarization variables used in other tools
case_two = []
case_two.append(summary_level)
case_two.append(PID)
case_two.append(tr_spp)
#A list of summarization variables used in other tools
case_three = []
case_three.append(summary_level)
case_three.append(tr_spp)
#A list of summarization variables used in other tools
case_pl34 = []
case_pl34.append(summary_level)
case_pl34.append(PID)

scratch_4 = env.scratchWorkspace + "\scratch_4"
arcpy.Statistics_analysis(tree_prism, scratch_4, [[PID, "COUNT"], [tr_spp, "COUNT"]], case_two)
scratch_5 = env.scratchWorkspace + "\scratch_5"
arcpy.Statistics_analysis(scratch_4, scratch_5, [["FREQUENCY", "SUM"]], case_three)
arcpy.AddField_management(scratch_5, "JOINFIELD", "TEXT")
arcpy.AddField_management(scratch_5, "NUM_TR", "LONG")
arcpy.CalculateField_management(scratch_5, "JOINFIELD", "!"+str(summary_level)+"! + !" +str(tr_spp)+ "!", "PYTHON")
arcpy.CalculateField_management(scratch_5, "NUM_TR", "!SUM_FREQUENCY!", "PYTHON")
arcpy.AddIndex_management(scratch_5, "JOINFIELD", "summary_5", "NON_UNIQUE", "NON_ASCENDING")
arcpy.Append_management(scratch_5, out_table, "NO_TEST")
arcpy.Delete_management(scratch_4)
arcpy.Delete_management(scratch_5)

scratch_pl1 = env.scratchWorkspace + "\scratch_pl1"
arcpy.Statistics_analysis(raw_prism, scratch_pl1, [[PID, "FIRST"]], case_two)
scratch_pl2 = env.scratchWorkspace + "\scratch_pl2"
arcpy.Statistics_analysis(scratch_pl1, scratch_pl2, [[PID, "COUNT"]], case_three)
arcpy.AddField_management(scratch_pl2, "JOINFIELD", "TEXT")
arcpy.CalculateField_management(scratch_pl2, "JOINFIELD", "!"+str(summary_level)+"! + !" +str(tr_spp)+ "!", "PYTHON")
arcpy.AddIndex_management(scratch_pl2, "JOINFIELD", "summary_pl2", "NON_UNIQUE", "NON_ASCENDING")
arcpy.JoinField_management(out_table, "JOINFIELD", scratch_pl2, "JOINFIELD", ["FREQUENCY"])
arcpy.CalculateField_management(out_table, "NUM_PL", "0 + !FREQUENCY!", "PYTHON")
arcpy.DeleteField_management(out_table, ["FREQUENCY"])
arcpy.Delete_management(scratch_pl1)
arcpy.Delete_management(scratch_pl2)


###
scratch_pl3 = env.scratchWorkspace + "\scratch_pl3"
arcpy.Statistics_analysis(raw_prism, scratch_pl3, [[PID, "FIRST"]], case_pl34)
scratch_pl4 = env.scratchWorkspace + "\scratch_pl4"
arcpy.Statistics_analysis(scratch_pl3, scratch_pl4, [[PID, "COUNT"]], summary_level)
arcpy.AddIndex_management(scratch_pl4, summary_level, "summary_pl4", "NON_UNIQUE", "NON_ASCENDING")
arcpy.JoinField_management(out_table, summary_level, scratch_pl4, summary_level, ["FREQUENCY"])
arcpy.CalculateField_management(out_table, "TOT_PL", "0 + !FREQUENCY!", "PYTHON")
arcpy.DeleteField_management(out_table, ["FREQUENCY"])
arcpy.Delete_management(scratch_pl3)
arcpy.Delete_management(scratch_pl4)
###





arcpy.AddMessage('Calculating AV_BA field...')
arcpy.CalculateField_management(out_table, "AV_BA", "10.00*!NUM_TR! / !TOT_PL!", "PYTHON")

arcpy.AddMessage('Calculating all TPA fields...')

arcpy.AddMessage('Calculating POL_TPA field...')
scratch_11 = env.scratchWorkspace + "\scratch_11"
tree_pol = str(env.scratchWorkspace)+"\\tree_pol"
arcpy.TableSelect_analysis(tree_prism, tree_pol, '"'+tr_dbh+'" >= 5 AND "'+tr_dbh+'" <12 AND LOWER("'+tr_hlth+'")<> \'d\'')
arcpy.AddField_management(tree_pol, "DENS", "DOUBLE")
arcpy.CalculateField_management(tree_pol, "DENS", "10 / (0.005454 * !"+tr_dbh+"! * !"+tr_dbh+"!)", "PYTHON")
arcpy.Statistics_analysis(tree_pol, scratch_11, [["DENS", "SUM"]], case_three)
arcpy.AddField_management(scratch_11, "JOINFIELD", "TEXT")
arcpy.CalculateField_management(scratch_11, "JOINFIELD", "!"+str(summary_level)+"! + !" +str(tr_spp)+ "!", "PYTHON")
arcpy.AddIndex_management(scratch_11, "JOINFIELD", "summary_11", "NON_UNIQUE", "NON_ASCENDING")
arcpy.JoinField_management(out_table, "JOINFIELD", scratch_11, "JOINFIELD", ["SUM_DENS"])
arcpy.CalculateField_management(out_table, "POL_TPA", "1.0 * !SUM_DENS!/!TOT_PL!", "PYTHON")
arcpy.CalculateField_management(out_table, "POL_TPA", "removenull(!POL_TPA!)", "PYTHON", codeblock)
arcpy.DeleteField_management(out_table, ["SUM_DENS"])
arcpy.Delete_management(scratch_11)
arcpy.Delete_management(tree_pol)

arcpy.AddMessage('Calculating SAW_TPA field...')
scratch_12 = env.scratchWorkspace + "\scratch_12"
tree_saw = str(env.scratchWorkspace)+"\\tree_saw"
arcpy.TableSelect_analysis(tree_prism, tree_saw, '"'+tr_dbh+'">=12 AND "'+tr_dbh+'"<18 AND LOWER("'+tr_hlth+'")<>\'d\'')
arcpy.AddField_management(tree_saw, "DENS", "DOUBLE")
arcpy.CalculateField_management(tree_saw, "DENS", "10 / (0.005454 * !"+tr_dbh+"! * !"+tr_dbh+"!)", "PYTHON")
arcpy.Statistics_analysis(tree_saw, scratch_12, [["DENS", "SUM"]], case_three)
arcpy.AddField_management(scratch_12, "JOINFIELD", "TEXT")
arcpy.CalculateField_management(scratch_12, "JOINFIELD", "!"+str(summary_level)+"! + !" +str(tr_spp)+ "!", "PYTHON")
arcpy.AddIndex_management(scratch_12, "JOINFIELD", "summary_12", "NON_UNIQUE", "NON_ASCENDING")
arcpy.JoinField_management(out_table, "JOINFIELD", scratch_12, "JOINFIELD", ["SUM_DENS"])
arcpy.CalculateField_management(out_table, "SAW_TPA", "1.0 * !SUM_DENS!/!TOT_PL!", "PYTHON")
arcpy.CalculateField_management(out_table, "SAW_TPA", "removenull(!SAW_TPA!)", "PYTHON", codeblock)
arcpy.DeleteField_management(out_table, ["SUM_DENS"])
arcpy.Delete_management(scratch_12)
arcpy.Delete_management(tree_saw)

arcpy.AddMessage('Calculating MAT_TPA field...')
scratch_13 = env.scratchWorkspace + "\scratch_13"
tree_mat = str(env.scratchWorkspace)+"\\tree_mat"
arcpy.TableSelect_analysis(tree_prism, tree_mat, '"'+tr_dbh+'">=18 AND "'+tr_dbh+'"<24 AND LOWER("'+tr_hlth+'")<>\'d\'')
arcpy.AddField_management(tree_mat, "DENS", "DOUBLE")
arcpy.CalculateField_management(tree_mat, "DENS", "10 / (0.005454 * !"+tr_dbh+"! * !"+tr_dbh+"!)", "PYTHON")
arcpy.Statistics_analysis(tree_mat, scratch_13, [["DENS", "SUM"]], case_three)
arcpy.AddField_management(scratch_13, "JOINFIELD", "TEXT")
arcpy.CalculateField_management(scratch_13, "JOINFIELD", "!"+str(summary_level)+"! + !" +str(tr_spp)+ "!", "PYTHON")
arcpy.AddIndex_management(scratch_13, "JOINFIELD", "summary_13", "NON_UNIQUE", "NON_ASCENDING")
arcpy.JoinField_management(out_table, "JOINFIELD", scratch_13, "JOINFIELD", ["SUM_DENS"])
arcpy.CalculateField_management(out_table, "MAT_TPA", "1.0 * !SUM_DENS!/!TOT_PL!", "PYTHON")
arcpy.CalculateField_management(out_table, "MAT_TPA", "removenull(!MAT_TPA!)", "PYTHON", codeblock)
arcpy.DeleteField_management(out_table, ["SUM_DENS"])
arcpy.Delete_management(scratch_13)
arcpy.Delete_management(tree_mat)

arcpy.AddMessage('Calculating OVM_TPA field...')
scratch_14 = env.scratchWorkspace + "\scratch_14"
tree_ovm = str(env.scratchWorkspace)+"\\tree_ovm"
arcpy.TableSelect_analysis(tree_prism, tree_ovm, ('"'+tr_dbh+'">=24 AND LOWER("'+tr_hlth+'")<>\'d\''))
arcpy.AddField_management(tree_ovm, "DENS", "DOUBLE")
arcpy.CalculateField_management(tree_ovm, "DENS", "10 / (0.005454 * !"+tr_dbh+"! * !"+tr_dbh+"!)", "PYTHON")
arcpy.Statistics_analysis(tree_ovm, scratch_14, [["DENS", "SUM"]], case_three)
arcpy.AddField_management(scratch_14, "JOINFIELD", "TEXT")
arcpy.CalculateField_management(scratch_14, "JOINFIELD", "!"+str(summary_level)+"! + !" +str(tr_spp)+ "!", "PYTHON")
arcpy.AddIndex_management(scratch_14, "JOINFIELD", "summary_14", "NON_UNIQUE", "NON_ASCENDING")
arcpy.JoinField_management(out_table, "JOINFIELD", scratch_14, "JOINFIELD", ["SUM_DENS"])
arcpy.CalculateField_management(out_table, "OVM_TPA", "1.0 * !SUM_DENS!/!TOT_PL!", "PYTHON")
arcpy.CalculateField_management(out_table, "OVM_TPA", "removenull(!OVM_TPA!)", "PYTHON", codeblock)
arcpy.DeleteField_management(out_table, ["SUM_DENS"])
arcpy.Delete_management(scratch_14)
arcpy.Delete_management(tree_ovm)

arcpy.AddMessage('Calculating SNAG_TPA field...')
scratch_8 = env.scratchWorkspace + "\scratch_8"
tree_snag = str(env.scratchWorkspace)+"\\tree_snag"
arcpy.TableSelect_analysis(tree_prism, tree_snag, 'LOWER("'+tr_hlth+'")=\'snag\' OR LOWER("'+tr_hlth+'")=\'dead\' OR LOWER("'+tr_hlth+'")=\'d\'')
arcpy.AddField_management(tree_snag, "DENS", "DOUBLE")
arcpy.CalculateField_management(tree_snag, "DENS", "10 / (0.005454 * !"+tr_dbh+"! * !"+tr_dbh+"!)", "PYTHON")
arcpy.Statistics_analysis(tree_snag, scratch_8, [["DENS", "SUM"]], case_three)
arcpy.AddField_management(scratch_8, "JOINFIELD", "TEXT")
arcpy.CalculateField_management(scratch_8, "JOINFIELD", "!"+str(summary_level)+"! + !" +str(tr_spp)+ "!", "PYTHON")
arcpy.AddIndex_management(scratch_8, "JOINFIELD", "summary_8", "NON_UNIQUE", "NON_ASCENDING")
arcpy.JoinField_management(out_table, "JOINFIELD", scratch_8, "JOINFIELD", ["SUM_DENS"])
arcpy.CalculateField_management(out_table, "SNAG_TPA", "1.0 * !SUM_DENS!/!TOT_PL!", "PYTHON")
arcpy.CalculateField_management(out_table, "SNAG_TPA", "removenull(!SNAG_TPA!)", "PYTHON", codeblock)
arcpy.DeleteField_management(out_table, ["SUM_DENS"])
arcpy.Delete_management(scratch_8)
arcpy.Delete_management(tree_snag)

arcpy.AddMessage('Calculating AV_TPA field...')
arcpy.CalculateField_management(out_table, "AV_TPA", "0.0 + !POL_TPA! + !SAW_TPA! + !MAT_TPA! + !OVM_TPA! + !SNAG_TPA!", "PYTHON")
arcpy.CalculateField_management(out_table, "AV_TPA", "removenull(!AV_TPA!)", "PYTHON", codeblock)

arcpy.AddMessage('Calculating QM_DBH field...')
arcpy.CalculateField_management(out_table, "QM_DBH", "0.0 + ((!AV_BA!/!AV_TPA!)/(0.005454))**(0.5)", "PYTHON")
arcpy.CalculateField_management(out_table, "QM_DBH", "removenull(!QM_DBH!)", "PYTHON", codeblock)

arcpy.AddMessage('Cleaning output table...')
arcpy.DeleteField_management(out_table, ["SCRATCH"])
arcpy.DeleteField_management(out_table, ["JOINFIELD"])
arcpy.Delete_management(tree_prism)


arcpy.CalculateField_management(out_table, "POL_TPA", "removenull(!POL_TPA!)", "PYTHON", codeblock)
arcpy.CalculateField_management(out_table, "SAW_TPA", "removenull(!SAW_TPA!)", "PYTHON", codeblock)
arcpy.CalculateField_management(out_table, "MAT_TPA", "removenull(!MAT_TPA!)", "PYTHON", codeblock)
arcpy.CalculateField_management(out_table, "OVM_TPA", "removenull(!OVM_TPA!)", "PYTHON", codeblock)
arcpy.CalculateField_management(out_table, "SNAG_TPA", "removenull(!SNAG_TPA!)", "PYTHON", codeblock)
arcpy.CalculateField_management(out_table, "AV_TPA", "removenull(!AV_TPA!)", "PYTHON", codeblock)
arcpy.CalculateField_management(out_table, "NUM_TR", "removenull(!NUM_TR!)", "PYTHON", codeblock)
arcpy.CalculateField_management(out_table, "NUM_PL", "removenull(!NUM_PL!)", "PYTHON", codeblock)
arcpy.CalculateField_management(out_table, "TOT_PL", "removenull(!TOT_PL!)", "PYTHON", codeblock)
arcpy.CalculateField_management(out_table, "QM_DBH", "removenull(!QM_DBH!)", "PYTHON", codeblock)

arcpy.AddMessage('Output table created.')


