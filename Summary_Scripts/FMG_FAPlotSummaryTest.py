#This script is intended to generate a summary table of forestry statistics from the USACE Phase 2 Forest Inventory
#   dataset, and summarize it by user defined fields. Last Updated: 28FEB2013

#Comments written above code

arcpy.AddMessage('Beginning...')

#Imports the prefixes for ArcGIS specific codes
import arcpy
from arcpy import env

arcpy.AddMessage('Identifying parameters')
fixed = arcpy.GetParameterAsText(0)
age = arcpy.GetParameterAsText(1)
ov_clsr = arcpy.GetParameterAsText(2)
ov_ht = arcpy.GetParameterAsText(3)
und_cov = arcpy.GetParameterAsText(4)
und_ht = arcpy.GetParameterAsText(5)
year = arcpy.GetParameterAsText(6)
summary_level = arcpy.GetParameterAsText(7)
out_table = arcpy.GetParameterAsText(8)
arcpy.AddMessage('Parameters identified.')

arcpy.AddMessage('Setting workspace...')
env.workspace = fixed
arcpy.AddMessage('Workspace set.')

arcpy.AddMessage('Assembling output table...')
out_tablename = out_table.split('\\')[-1]
out_tablepath = out_table.replace(out_tablename, '')
arcpy.CreateTable_management(out_tablepath, out_tablename)

arcpy.AddMessage('Creating output table fields...')
arcpy.AddField_management(out_table, summary_level, "TEXT")
arcpy.AddField_management(out_table, "OV_CLSR", "DOUBLE")
arcpy.AddField_management(out_table, "OV_HT", "DOUBLE")
arcpy.AddField_management(out_table, "UND_COV", "DOUBLE")
arcpy.AddField_management(out_table, "UND_HT", "DOUBLE")
arcpy.AddField_management(out_table, "TR_AGE", "DOUBLE")
arcpy.AddIndex_management(out_table, summary_level, "summary_out", "NON_UNIQUE", "NON_ASCENDING")
arcpy.AddMessage('Output table fields created...')

arcpy.AddMessage('Calculating fields...')

arcpy.AddMessage('Calculating OV_CLSR, OV_HT, UND_COV, & UND_HT fields...')
fixed_stats = str(env.scratchWorkspace) + "\\fixed_stats"
arcpy.Statistics_analysis(fixed, fixed_stats, [[ov_clsr, "MEAN"], [ov_ht, "MEAN"], [und_cov, "MEAN"], [und_ht, "MEAN"]], summary_level)
arcpy.AddField_management(fixed_stats, "OV_CLSR", "DOUBLE")
arcpy.AddField_management(fixed_stats, "OV_HT", "DOUBLE")
arcpy.AddField_management(fixed_stats, "UND_COV", "DOUBLE")
arcpy.AddField_management(fixed_stats, "UND_HT", "DOUBLE")
arcpy.CalculateField_management(fixed_stats, "OV_CLSR", "!MEAN_"+ov_clsr+"!", "PYTHON")
arcpy.CalculateField_management(fixed_stats, "OV_HT", "!MEAN_"+ov_ht+"!", "PYTHON")
arcpy.CalculateField_management(fixed_stats, "UND_COV", "!MEAN_"+und_cov+"!", "PYTHON")
arcpy.CalculateField_management(fixed_stats, "UND_HT", "!MEAN_"+und_ht+"!", "PYTHON")
arcpy.AddIndex_management(fixed_stats, summary_level, "fixed_stats", "NON_UNIQUE", "NON_ASCENDING")

arcpy.AddMessage('Calculating TR_AGE field...')
age_stats = str(env.scratchWorkspace) + "\\age_stats"
arcpy.Statistics_analysis(age, age_stats, [[year, "MEAN"]], summary_level)
arcpy.AddIndex_management(age_stats, summary_level, "age_stats", "NON_UNIQUE", "NON_ASCENDING")

arcpy.AddMessage('Assembling output table...')
arcpy.Append_management(fixed_stats, out_table, "NO_TEST")
arcpy.JoinField_management(out_table, summary_level, age_stats, summary_level, ["MEAN_"+year])
arcpy.CalculateField_management(out_table, "TR_AGE", "!MEAN_"+year+"!", "PYTHON")

arcpy.AddMessage('Cleaning output table...')
arcpy.DeleteField_management(out_table, ["MEAN_"+ov_clsr, "MEAN_"+ov_ht, "MEAN_"+und_ht, "MEAN_"+year])
arcpy.Delete_management(fixed_stats)
arcpy.Delete_management(age_stats)

arcpy.AddMessage('Output table created.')
