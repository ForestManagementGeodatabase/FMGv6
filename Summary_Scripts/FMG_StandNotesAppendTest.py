#This script is intended to aggregate the plot notes from the USACE Phase 2 Forest Inventory
#   dataset, and summarize it in the appropriate FMG table. Last Updated: 26FEB2013

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

#creates a Python variable from an SQL expression
notnull = "\"MISC\" IS NOT NULL"

#Identifies the user-provided parameters from the GUI
arcpy.AddMessage('Identifying parameters')
prism = arcpy.GetParameterAsText(0)
fixed = arcpy.GetParameterAsText(1)
age = arcpy.GetParameterAsText(2)
notes = arcpy.GetParameterAsText(3)
arcpy.AddMessage('Parameters identified.')

arcpy.AddMessage('Creating output table...')
out_tablename = notes.split('\\')[-1]
out_tablepath = notes.replace(out_tablename, '')
arcpy.CreateTable_management(out_tablepath, out_tablename)
arcpy.AddMessage('Adding output table fields...')
arcpy.AddField_management(notes, "SID", "TEXT")
arcpy.AddField_management(notes, "PID", "TEXT")
arcpy.AddField_management(notes, "COL_CREW", "TEXT")
arcpy.AddField_management(notes, "COL_DATE", "TEXT")
arcpy.AddField_management(notes, "MISC", "TEXT")
arcpy.AddField_management(notes, "NOTE_BY", "TEXT")
arcpy.AddField_management(notes, "NOTE_DATE", "TEXT")
arcpy.AddField_management(notes, "NOTE", "TEXT")

arcpy.AddMessage('Identifying prism plots with notes...')
prism_notes = str(env.scratchWorkspace) + "\\prism_notes"
arcpy.TableSelect_analysis(prism, prism_notes, notnull)

arcpy.AddMessage('Identifying fixed plots with notes...')
fixed_notes = str(env.scratchWorkspace) + "\\fixed_notes"
arcpy.TableSelect_analysis(fixed, fixed_notes, notnull)

arcpy.AddMessage('Identifying age plots with notes...')
age_notes = str(env.scratchWorkspace) + "\\age_notes"
arcpy.TableSelect_analysis(age, age_notes, notnull)

arcpy.AddMessage('Aggregating notes...')
arcpy.Append_management([prism_notes, fixed_notes, age_notes], notes, "NO_TEST")

arcpy.AddMessage('Cleaning output table...')
arcpy.CalculateField_management(notes, "NOTE_BY", "!COL_CREW!", "PYTHON")
arcpy.CalculateField_management(notes, "NOTE_DATE", "!COL_DATE!", "PYTHON")
arcpy.CalculateField_management(notes, "NOTE", "str(!MISC!)", "PYTHON")
arcpy.DeleteField_management(notes, ["COL_CREW", "COL_DATE", "MISC"])
arcpy.Delete_management(prism_notes)
arcpy.Delete_management(fixed_notes)
arcpy.Delete_management(age_notes)
