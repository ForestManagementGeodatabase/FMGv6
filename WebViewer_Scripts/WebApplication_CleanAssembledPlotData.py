#Do the imports
import arcpy
import arcgis
import numpy
import pandas
import os

# Define some globals
inDirtyData = arcpy.GetParameterAsText(0) #r"\\mvrdfs.mvr.ds.usace.army.mil\egis\Work\EMP\HREP_Projects\Pool_12_Forestry\Data\ForestInventory_ForAGOL\Forest_Inventory_AGOL.gdb\Pool12_ForestInventory_Plots_Testing"
outCleanData = arcpy.GetParameterAsText(1) #r"\\mvrdfs.mvr.ds.usace.army.mil\egis\Work\EMP\HREP_Projects\Pool_12_Forestry\Data\ForestInventory_ForAGOL\Forest_Inventory_AGOL.gdb\Pool12_ForestInventory_Plots_Clean"
sumLevel = arcpy.GetParameterAsText(2) #'PID'
arcpy.SetParameterAsText(3, outCleanData)

# Define Field Alias Dictionary
FMGalias = {"OV_CLSR" : "Overstory Closure Percent",
            "OV_HT" : "Overstory Height",
            "UND_COV" : "Understory Cover Percent",
            "UND_HT" : "Understory Height",
            "UND_SP1" : "Understory Species 1",
            "UND_SP2" : "Understory Species 2",
            "UND_SP3" : "Understory Species 3",
            "GRD_SP1" : "Ground Species 1",
            "GRD_SP2" : "Ground Species 2",
            "GRD_SP3" : "Ground Species 3",
            "NOT_SP1" : "Notable Species 1",
            "NOT_SP2" : "Notable Species 2",
            "NOT_SP3" : "Notable Species 3",
            "NOT_SP4" : "Notable Species 4",
            "NOT_SP5" : "Notable Species 5",
            "FIELD_DATE" : "Field Date",
            "OVERALL_HLTH" : "Overall Health",
            "HARD_MAST_HLTH" : "Hard Mast Health",
            "MP_TYP_HLTH" : "Typical Sp Health",
            "MP_TYP_SP" : "Most Prevalent Typical Sp",
            "MP_NTYP_HLTH" : "Non Typical Sp Health",
            "MP_NTYP_SP" : "Most Prevalent Non Typical Sp",
            "CANOPY_HLTH" : "Canopy Health",
            "MP_CANOPY_SP" : "Most Prevalent Canopy Sp",
            "INVASIVE_PRESENT" : "Invasive Species Present",
            "INVASIVE_SP" : "Invasive Species"}

arcpy.AddMessage ('Modules imported, globals defined')

# Import dirty data as pandas dataframe
BaseDF = pandas.DataFrame.spatial.from_featureclass(inDirtyData)
arcpy.AddMessage ('Spatial Dataframe created')

# Generate a list of health fields
HlthFields = BaseDF.loc[:,['HLTH' in i for i in BaseDF.columns]].columns.values.tolist()

# Iterate through the Health fields changing codes to words
for item in HlthFields:
    BaseDF.loc[BaseDF[item]=='H', item] = 'Healthy'
    BaseDF.loc[BaseDF[item]=='S', item] = 'Stressed'
    BaseDF.loc[BaseDF[item]=='SD', item] = 'Significant Decline'
    BaseDF.loc[BaseDF[item]=='D', item] = 'Dead'
arcpy.AddMessage ('Health field values converted from codes to descriptions')

# Convert Overstory Closure Percentage to integer
BaseDF.OV_CLSR = BaseDF.OV_CLSR.fillna(0).astype(int)
arcpy.AddMessage ('OV_CLSR converted to int')

# Convert Overstory Height to integer
BaseDF.OV_HT = BaseDF.OV_HT.fillna(0).astype(int)
arcpy.AddMessage ('OV_HT converted to int')

# Convert Understory Cover to integer
BaseDF.UND_COV = BaseDF.UND_COV.fillna(0).astype(int)
arcpy.AddMessage ('UND_COV converted to int')

# Create new FIELD_DATE_DT to strip time from Date time field
DateField = str([f.name for f in arcpy.ListFields(inDirtyData, '*Date')][0])
BaseDF['FIELD_DATE'] = BaseDF[DateField]#.dt.strftime('%m/%d/%Y')

# Create new clean dataframe for export: rounding floats to 1 decimal, removing and renaming fields
naKeys = list(BaseDF.select_dtypes(['float64']))
naVals = [0]*len(naKeys)
naDict = dict(zip(naKeys, naVals))
CleanDF = BaseDF[BaseDF['FIELD_DATE'].notnull()].round(1).drop(columns=[DateField]).fillna(value=naDict)
arcpy.AddMessage ('Created new clean dataframe, rounding floats and filling NaNs') 

# Export Clean dataframe back to file geodatabase
CleanDF.spatial.to_featureclass(location=outCleanData)
arcpy.AddMessage ('Clean dataframe exported into GDB: {0}'.format(outCleanData))

# Set field aliases on clean data
for field, alias in FMGalias.items():
    arcpy.AddMessage ('Setting alias on {0}'.format(field))
    arcpy.AlterField_management(in_table=outCleanData,
                                field=field,
                                new_field_alias=alias)
arcpy.AddMessage('Field Aliases set')
arcpy.AddMessage('Script complete')


            
