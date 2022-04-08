# Do the imports
import arcpy
import os

# Define Inputs
inGeom = arcpy.GetParameterAsText(0) #r"\\mvrdfs.mvr.ds.usace.army.mil\egis\Work\EMP\HREP_Projects\Pool_12_Forestry\Data\ForestInventory_ForAGOL\Forest_Inventory_AGOL.gdb\Pool12_ForestInventory_Plots_Testing"
inFixedPlots = arcpy.GetParameterAsText(1) #r"\\mvrdfs.mvr.ds.usace.army.mil\egis\Work\EMP\HREP_Projects\Pool_12_Forestry\Data\ForestInventory_ForAGOL\Forest_Inventory_AGOL.gdb\Final_Pool12_Fixed"
inPandasSum = arcpy.GetParameterAsText(2) #r"\\mvrdfs.mvr.ds.usace.army.mil\egis\Work\EMP\HREP_Projects\Pool_12_Forestry\Data\ForestInventory_ForAGOL\Forest_Inventory_AGOL.gdb\Plot_WebVarPandas"
arcpy.SetParameterAsText(3, inGeom)

FixedFields = ["OV_CLSR",
               "OV_HT",
               "UND_COV",
               "UND_HT",
               "UND_SP1",
               "UND_SP2",
               "UND_SP3",
               "GRD_SP1",
               "GRD_SP2",
               "GRD_SP3",
               "NOT_SP1",
               "NOT_SP2",
               "NOT_SP3",
               "NOT_SP4",
               "NOT_SP5",
               "FP_DATE",
               "COL_DATE"]

PandasFields = ["OVERALL_HLTH",
             "HARD_MAST_HLTH",
             "MP_TYP_HLTH",
             "MP_TYP_SP",
             "MP_NTYP_HLTH",
             "MP_NTYP_SP",
             "CANOPY_HLTH",
             "MP_CANOPY_SP"]
arcpy.AddMessage ('Modules imported, global variables defined')

# Join Pandas Summary Fields
arcpy.JoinField_management(in_data=inGeom,
                           in_field='PID',
                           join_table=inPandasSum,
                           join_field='PID',
                           fields=PandasFields)
arcpy.AddMessage ('Pandas summary fields joined to Plot geometry')

# Join Fixed Plot Fields
arcpy.JoinField_management(in_data=inGeom,
                           in_field='PID',
                           join_table=inFixedPlots,
                           join_field='PID',
                           fields=FixedFields)
arcpy.AddMessage ('Fixed Plot fields joined to Plot geometry')

# Add and populate Invasive Species columns
arcpy.AddField_management(in_table=inGeom,
                          field_name='INVASIVE_PRESENT',
                          field_type='TEXT',
                          field_length=10)
print ('Invasive_Present field added')

arcpy.AddField_management(in_table=inGeom,
                          field_name='INVASIVE_SP',
                          field_type='TEXT',
                          field_length=50)
arcpy.AddMessage ('Invasive_Sp field added')

# Use an update cursor to populate the fields based on species presence
SpFields = ["GRD_SP1", "GRD_SP2", "GRD_SP3", "NOT_SP1", "NOT_SP2", "NOT_SP3", "NOT_SP4", "NOT_SP5", "INVASIVE_PRESENT", "INVASIVE_SP"]
with arcpy.da.UpdateCursor(inGeom, SpFields) as cursor:
    for row in cursor:
        SpList = []
        if row.count('HUJA') > 0:
            SpList.append('HUJA')
        elif row.count('PHAR3') > 0:
            SpList.append('PHAR3')
        elif row.count('PHAU7') > 0:
            SpList.append('PHAU7')
        if len(SpList) > 0:
            row[8] = 'Yes'
            row[9] = ", ".join(SpList)
        elif len(SpList) == 0:
            row[8] = 'No'
            row[9] = 'None'
        cursor.updateRow(row)
        del SpList
arcpy.AddMessage ('Invasive_Present and Invasive_Sp fields populated')
arcpy.AddMessage ('Script complete')

