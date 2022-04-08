#Do the imports
import arcpy
import arcgis
import numpy
import pandas
import os

# Define some globals
inDirtyData = arcpy.GetParameterAsText(0) #r"\\mvrdfs.mvr.ds.usace.army.mil\egis\Work\EMP\HREP_Projects\Pool_12_Forestry\Data\ForestInventory_ForAGOL\Forest_Inventory_AGOL.gdb\Pool12_ForestInventory_Sites"
outCleanData = arcpy.GetParameterAsText(1) #r"\\mvrdfs.mvr.ds.usace.army.mil\egis\Work\EMP\HREP_Projects\Pool_12_Forestry\Data\ForestInventory_ForAGOL\Forest_Inventory_AGOL.gdb\Pool12_ForestInventory_Sites_Clean"
sumLevel = arcpy.GetParameterAsText(2) #'SITE'
arcpy.SetParameterAsText(3, outCleanData)
baseReconReportURL = 'https://forestmanagementgeodatabase.github.io/FMG-StandWalk/Stand_Summary_'

# Define Field Alias Dictionary
FMGalias = {"OVERALL_HLTH" :"Overall Health",
            "HARD_MAST_HLTH" :"Hard Mast Health",
            "MP_TYP_HLTH" :"Typical Sp Health",
            "MP_TYP_SP" : "Most Prevalent Typical Sp",
            "MP_NTYP_HLTH" : "Non Typical Sp Health",
            "MP_NTYP_SP" : "Most Prevalent Non Typical Sp",
            "CANOPY_HLTH" : "Canopy Health",
            "MP_CANOPY_SP" : "Most Prevalent Canopy Sp",
            "OV_CLSR" : "Overstory Closure Percent",
            "OV_HT" : "Overstory Height",
            "UND_COV" : "Understory Cover Percent",
            "UND_HT" : "Understory Height",
            "TR_AGE" : "Tree Age",
            "NUM_TR" : "Tree Count",
            "SPP_RICH" : "Species Richness",
            "AV_BA" : "Average Basal Area",
            "AV_TPA" : "Average Trees Per Acre",
            "SAP_TPA" : "Sapling TPA",
            "POL_TPA" : "Pole Timber TPA",
            "SAW_TPA" : "Saw Timber TPA",
            "MAT_TPA" : "Mature Timber TPA",
            "OVM_TPA" : "Over Mature Timber TPA",
            "SNAG_TPA" : "Snag Or Dead TPA",
            "LG_SNAG_TPA" : "Large Snag TPA",
            "HRD_MAST" : "Hard Mast TPA",
            "SFT_MAST" : "Soft Mast TPA",
            "H_TPA" : "Healthy TPA",
            "S_TPA" : "Stressed TPA",
            "SD_TPA" : "Significant Decline TPA",
            "D_TPA" : "Dead TPA",
            "NUM_PL" : "Plot Count",
            "QM_DBH" : "Quadratic Mean DBH"}

arcpy.AddMessage ('Modules imported, global variables defined')

# Import the dirty data as a pandas dataframe
BaseDF = pandas.DataFrame.spatial.from_featureclass(inDirtyData)
arcpy.AddMessage ('spatial dataframe created')

# Generate a list of health fields
HlthFields = BaseDF.loc[:,['HLTH' in i for i in BaseDF.columns]].columns.values.tolist()

# Iterate through the Health fields changing codes to words
for item in HlthFields:
    BaseDF.loc[BaseDF[item]=='H', item] = 'Healthy'
    BaseDF.loc[BaseDF[item]=='S', item] = 'Stressed'
    BaseDF.loc[BaseDF[item]=='SD', item] = 'Significant Decline'
    BaseDF.loc[BaseDF[item]=='D', item] = 'Dead'
arcpy.AddMessage ('Health field values converted from codes to descriptions')

# Convert TR_AGE to integer
BaseDF.TR_AGE = BaseDF.TR_AGE.fillna(0).astype(int)
arcpy.AddMessage ('TR_AGE converted to int')

# Convert Overstory Closure Percentage to integer
BaseDF.OV_CLSR = BaseDF.OV_CLSR.fillna(0).astype(int)
arcpy.AddMessage ('OV_CLSR converted to int')

# Convert Overstory Height to integer
BaseDF.OV_HT = BaseDF.OV_HT.fillna(0).astype(int)
arcpy.AddMessage ('OV_HT converted to int')

# Convert Understory Cover to integer
BaseDF.UND_COV = BaseDF.UND_COV.fillna(0).astype(int)
arcpy.AddMessage ('UND_COV converted to int')

# Create new UND_HT_RNG to show ranges instead of numbers
conditions = [(BaseDF['UND_HT'] >= 0) & (BaseDF['UND_HT'] < 2),
              (BaseDF['UND_HT'] >= 2) & (BaseDF['UND_HT'] < 5),
              (BaseDF['UND_HT'] >= 5) & (BaseDF['UND_HT'] < 10),
              (BaseDF['UND_HT'] >= 10) & (BaseDF['UND_HT'] < 15),
              (BaseDF['UND_HT'] >= 15) & (BaseDF['UND_HT'] < 20),
              (BaseDF['UND_HT'] >= 20) & (BaseDF['UND_HT'] < 25),
              (BaseDF['UND_HT'] >= 25) & (BaseDF['UND_HT'] < 30),
              (BaseDF['UND_HT'] >= 30) & (BaseDF['UND_HT'] < 35),
              (BaseDF['UND_HT'] >= 35) & (BaseDF['UND_HT'] < 40),
              (BaseDF['UND_HT'] >= 40) & (BaseDF['UND_HT'] < 45),
              (BaseDF['UND_HT'] >= 45) & (BaseDF['UND_HT'] < 50),
              (BaseDF['UND_HT'] >= 50)]

values = ['<2', '2-5', '5-10', '10-15', '15-20', '20-25', '25-30', '30-35', '35-40', '40-45', '45-50', '>50']

BaseDF['UND_HT_RNG'] = numpy.select(conditions, values)
arcpy.AddMessage ('UND_HT converted back to ranges')

# Create new clean dataframe for export, rounding floats to 1 decimal place and removing and renaming a field, set floating nans to zero
naKeys = list(BaseDF.select_dtypes(['float64']))
naVals = [0]*len(naKeys)
naDict = dict(zip(naKeys, naVals))
CleanDF = BaseDF[BaseDF['NUM_PL'].notnull()].round(1).drop(columns=['UND_HT']).rename(columns={'UND_HT_RNG':'UND_HT'}).fillna(value=naDict)
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

# Add and calculate area field
arcpy.AddField_management(in_table=outCleanData,
                          field_name='AREA_ACRES',
                          field_type = 'DOUBLE',
                          field_alias = 'Area')
arcpy.CalculateGeometryAttributes_management(in_features=outCleanData,
                                             geometry_property=[['AREA_ACRES', 'AREA_GEODESIC']],
                                             area_unit='ACRES')
arcpy.AddMessage ('Area field added and calculated')

# Add and calculate Forest Recon Sheet URL
arcpy.AddField_management(in_table=outCleanData,
                          field_name='RECON_REPORT',
                          field_type='TEXT',
                          field_length=250,
                          field_alias='Forest Recon Report')

arcpy.CalculateField_management(in_table=outCleanData,
                                field='RECON_REPORT',
                                expression="""'{0}' + !{1}! + '.html'""".format(baseReconReportURL, sumLevel))
arcpy.AddMessage ('Recon report URL field added and populated')
arcpy.AddMessage ('script complete')
 
                                
                                 









