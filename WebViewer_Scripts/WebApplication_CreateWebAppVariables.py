# Do the imports
import numpy
import pandas
import arcpy
import arcgis
import os
arcpy.AddMessage('imports done')

# Define some testing datasets
inOPH = arcpy.GetParameterAsText(0) #r"\\mvrdfs.mvr.ds.usace.army.mil\egis\Work\EMP\HREP_Projects\Pool_12_Forestry\Data\ForestInventory_ForAGOL\Forest_Inventory_AGOL.gdb\Plot_OV_Health"
inHMH = arcpy.GetParameterAsText(1) #r"\\mvrdfs.mvr.ds.usace.army.mil\egis\Work\EMP\HREP_Projects\Pool_12_Forestry\Data\ForestInventory_ForAGOL\Forest_Inventory_AGOL.gdb\Plot_HM_Health"
inTSH = arcpy.GetParameterAsText(2) #r"\\mvrdfs.mvr.ds.usace.army.mil\egis\Work\EMP\HREP_Projects\Pool_12_Forestry\Data\ForestInventory_ForAGOL\Forest_Inventory_AGOL.gdb\Plot_TYP_Health"
inNSH = arcpy.GetParameterAsText(3) #r"\\mvrdfs.mvr.ds.usace.army.mil\egis\Work\EMP\HREP_Projects\Pool_12_Forestry\Data\ForestInventory_ForAGOL\Forest_Inventory_AGOL.gdb\Plot_NTYP_Health"
inCNP = arcpy.GetParameterAsText(4) #r"\\mvrdfs.mvr.ds.usace.army.mil\egis\Work\EMP\HREP_Projects\Pool_12_Forestry\Data\ForestInventory_ForAGOL\Forest_Inventory_AGOL.gdb\Plot_CNP_Health"
inSUM = arcpy.GetParameterAsText(5) #r"\\mvrdfs.mvr.ds.usace.army.mil\egis\Work\EMP\HREP_Projects\Pool_12_Forestry\Data\ForestInventory_ForAGOL\Forest_Inventory_AGOL.gdb\Pool12_ForestInventory_Plots_Testing"
sumLevel = arcpy.GetParameterAsText(6) #'PID'
outDF = arcpy.GetParameterAsText(7) #r"\\mvrdfs.mvr.ds.usace.army.mil\egis\Work\EMP\HREP_Projects\Pool_12_Forestry\Data\ForestInventory_ForAGOL\Forest_Inventory_AGOL.gdb\Plot_WebVarPandas"
arcpy.AddMessage('variables defined')

# Create Base DF - used to join variables to
SUMdf = pandas.DataFrame(data=arcpy.da.TableToNumPyArray(in_table=inSUM,field_names=sumLevel)).set_index(sumLevel)
arcpy.AddMessage('base data frame created')

## Overall Plot Health: FMG Health Summary Tool, no options set. Resutls in OVERALL_HLTH variable ##
# Create pandas dataframe from File Geodatabase table
arcpy.AddMessage('starting Overall Plot Health')
OPHdf = pandas.DataFrame(data=arcpy.da.TableToNumPyArray(in_table=inOPH,field_names='*'))
arcpy.AddMessage('    DF Created')
# Create pandas dataframe with most prevalant Health rating for given summary level using max TPA
OPHdf_max = OPHdf.groupby(by=sumLevel)['AV_TPA'].max().reset_index()
arcpy.AddMessage('    max DF Created')
# Join most prevalant health rating back to orig. dataframe, using an inner join to remove less prevalent health ratings
OPHdf_join = OPHdf.merge(OPHdf_max,how='inner',left_on=[sumLevel, 'AV_TPA'],right_on=[sumLevel, 'AV_TPA']).reset_index().drop(columns=['OBJECTID', 'COUNT_COMP', 'index'])
arcpy.AddMessage('    join DF Created')
# Create new column and assign numeric values to health codes. Used to sort records, and drop all but the most healthy category dealing with duplicate record edge cases
conditions = [(OPHdf_join['TR_HLTH'] == 'H'),(OPHdf_join['TR_HLTH'] == 'S'),(OPHdf_join['TR_HLTH'] == 'SD'),(OPHdf_join['TR_HLTH'] == 'D')]
values = [1, 2, 3, 4]
OPHdf_join['TR_HLTH_NUM'] = numpy.select(conditions, values)
# Drop duplicate rows, keeping most healthy record, then remove intermediate field as new dataframe
OPH_clean = OPHdf_join.sort_values(by=[sumLevel, 'TR_HLTH_NUM']).drop_duplicates(sumLevel, keep='first').drop(columns=['TR_HLTH_NUM', 'AV_TPA']).rename(columns={'TR_HLTH':'OVERALL_HLTH'}).set_index(sumLevel)
arcpy.AddMessage('    clean DF Created')

##Overall Plot Health: FMG Health Summary Tool, no options set. Resutls in H_TPA, S_TPA, SD_TPA, D_TPA variables
OPH_TPA = OPHdf.pivot_table(index=[sumLevel], columns='TR_HLTH', values='AV_TPA').rename(columns={'H':'H_TPA', 'S':'S_TPA', 'SD':'SD_TPA', 'D':'D_TPA'})
                                                                                                                    
## Hard Mast Health: FMG Health Summary Tool, with Mast option. Results in HARD_MAST_HLTH variable. ##                                                                                                                   
# Create pandas dataframe from File Geodatabase table
arcpy.AddMessage('starting Hard Mast Health')
HMHdf = pandas.DataFrame(data=arcpy.da.TableToNumPyArray(in_table=inHMH,field_names='*'))
arcpy.AddMessage('    DF Created')
# Create pandas dataframe with most prevalant Health rating for hard mast for given summary level using max TPA
MastValues = ['HARD', 'hard', 'Hard', 'H', 'h']
HMHdf_max = HMHdf[HMHdf.MAST_TYPE.isin(MastValues)].groupby(by=[sumLevel,'MAST_TYPE'])['AV_TPA'].max().reset_index()
arcpy.AddMessage('    max DF Created')
# Join most prevalant health rating back to orig. dataframe, using an inner join to remove less prevalent health ratings
HMHdf_join = HMHdf.merge(HMHdf_max,how='inner',left_on=[sumLevel, 'AV_TPA'],right_on=[sumLevel, 'AV_TPA']).reset_index().drop(columns=['OBJECTID', 'MAST_TYPE_x', 'COUNT_COMP', 'index']).rename(columns={'MAST_TYPE_y':'MAST_TYPE'})
arcpy.AddMessage('    join DF Created')
# Create new column and assign numeric values to health codes. Used to sort records, and drop all but the most healthy category dealing with duplicate record edge cases
conditions = [(HMHdf_join['TR_HLTH'] == 'H'),(HMHdf_join['TR_HLTH'] == 'S'),(HMHdf_join['TR_HLTH'] == 'SD'),(HMHdf_join['TR_HLTH'] == 'D')]
values = [1, 2, 3, 4]
HMHdf_join['TR_HLTH_NUM'] = numpy.select(conditions, values)
# Drop duplicate rows, keeping most healthy record, then remove intermediate field as new dataframe
HMH_clean = HMHdf_join.sort_values(by=[sumLevel, 'TR_HLTH_NUM']).drop_duplicates(sumLevel, keep='first').drop(columns=['TR_HLTH_NUM', 'AV_TPA', 'MAST_TYPE']).rename(columns={'TR_HLTH':'HARD_MAST_HLTH'}).set_index(sumLevel)
arcpy.AddMessage('    clean DF Created')

                                                                                                                       
## Typical Species Health: FMG Health Summary Tool, def query of typical species on prism plot, with species option. Results in MP_TYP_HLTH and MP_TYP_SP variables. ##
# Create pandas dataframe from File Geodatabase table
arcpy.AddMessage('starting Typical Species Health')
TSHdf = pandas.DataFrame(data=arcpy.da.TableToNumPyArray(in_table=inTSH, field_names='*'))
arcpy.AddMessage('    DF Created')
# Create pandas dataframe with max TPA by given summary level
TSHdf_max = TSHdf.groupby(by=sumLevel)['AV_TPA'].max().reset_index()
arcpy.AddMessage('    max DF Created')
# Join max tpa back to full table
TSHdf_join = TSHdf.merge(TSHdf_max, how='inner', left_on=[sumLevel, 'AV_TPA'], right_on=[sumLevel, 'AV_TPA']).reset_index().drop(columns=['OBJECTID', 'COUNT_COMP', 'index'])
arcpy.AddMessage('    join DF Created')
# Create new column and assign numeric values to health codes. Used to sort records, and drop all but the most healthy category dealing with duplicate record edge cases
conditions = [(TSHdf_join['TR_HLTH'] == 'H'),(TSHdf_join['TR_HLTH'] == 'S'),(TSHdf_join['TR_HLTH'] == 'SD'),(TSHdf_join['TR_HLTH'] == 'D')]
values = [1, 2, 3, 4]
TSHdf_join['TR_HLTH_NUM'] = numpy.select(conditions, values)
# Drop duplicate rows, keeping most healthy record, then remove intermediate field as new dataframe
TSH_clean = TSHdf_join.sort_values(by=[sumLevel, 'TR_HLTH_NUM']).drop_duplicates(sumLevel, keep='first').drop(columns=['TR_HLTH_NUM', 'AV_TPA']).rename(columns={'TR_HLTH':'MP_TYP_HLTH', 'TR_SP':'MP_TYP_SP'}).set_index(sumLevel)
arcpy.AddMessage('    clean DF Created')                                                                                                                        


## Non Typical Species Health: FMG Health Summary Tool, def query of non typical species on prism plot, with species option. Results in MP_NTYP_HLTH and MP_NTYP_SP variables. ##
# Create pandas dataframe from File Geodatabase table
arcpy.AddMessage('starting Non Typical Species Health')
NSHdf = pandas.DataFrame(data=arcpy.da.TableToNumPyArray(in_table=inNSH, field_names='*'))
arcpy.AddMessage('    DF Created')
# Create pandas dataframe with max TPA by given summary level
NSHdf_max = NSHdf.groupby(by=sumLevel)['AV_TPA'].max().reset_index()
arcpy.AddMessage('    max DF Created')
# Join max tpa back to full table
NSHdf_join = NSHdf.merge(NSHdf_max, how='inner', left_on=[sumLevel, 'AV_TPA'], right_on=[sumLevel, 'AV_TPA']).reset_index().drop(columns=['OBJECTID', 'COUNT_COMP', 'index'])
arcpy.AddMessage('    join DF Created')
# Create new column and assign numeric values to health codes. Used to sort records, and drop all but the most healthy category dealing with duplicate record edge cases
conditions = [(NSHdf_join['TR_HLTH'] == 'H'),(NSHdf_join['TR_HLTH'] == 'S'),(NSHdf_join['TR_HLTH'] == 'SD'),(NSHdf_join['TR_HLTH'] == 'D')]
values = [1, 2, 3, 4]
NSHdf_join['TR_HLTH_NUM'] = numpy.select(conditions, values)
# Drop duplicate rows, keeping most healthy record, then remove intermediate field as new dataframe
NSH_clean = NSHdf_join.sort_values(by=[sumLevel, 'TR_HLTH_NUM']).drop_duplicates(sumLevel, keep='first').drop(columns=['TR_HLTH_NUM', 'AV_TPA']).rename(columns={'TR_HLTH':'MP_NTYP_HLTH', 'TR_SP':'MP_NTYP_SP'}).set_index(sumLevel)
arcpy.AddMessage('    clean DF Created')


## Canopy Health: FMG Health Summary Tool, def query of dom & co-dom trees on prism plot, with species option. Results in CANOPY_HLTH and MP_CANOPY_SP variables. ##
# Create pandas dataframe from File Geodatabase table
arcpy.AddMessage('starting Canopy Health')
CNPdf = pandas.DataFrame(data=arcpy.da.TableToNumPyArray(in_table=inCNP, field_names='*'))
arcpy.AddMessage('    DF Created')
# Create pandas dataframe with max TPA by given summary level
CNPdf_max = CNPdf.groupby(by=sumLevel)['AV_TPA'].max().reset_index()
arcpy.AddMessage('    max DF Created')
# Join max tpa back to full table
CNPdf_join = CNPdf.merge(CNPdf_max, how='inner', left_on=[sumLevel, 'AV_TPA'], right_on=[sumLevel, 'AV_TPA']).reset_index().drop(columns=['OBJECTID', 'COUNT_COMP', 'index'])
arcpy.AddMessage('    join DF Created')
# Create new column and assign numeric values to health codes. Used to sort records, and drop all but the most healthy category dealing with duplicate record edge cases
conditions = [(CNPdf_join['TR_HLTH'] == 'H'),(CNPdf_join['TR_HLTH'] == 'S'),(CNPdf_join['TR_HLTH'] == 'SD'),(CNPdf_join['TR_HLTH'] == 'D')]
values = [1, 2, 3, 4]
CNPdf_join['TR_HLTH_NUM'] = numpy.select(conditions, values)
# Drop duplicate rows, keeping most healthy record, then remove intermediate field as new dataframe
CNP_clean = CNPdf_join.sort_values(by=[sumLevel, 'TR_HLTH_NUM']).drop_duplicates(sumLevel, keep='first').drop(columns=['TR_HLTH_NUM', 'AV_TPA']).rename(columns={'TR_HLTH':'CANOPY_HLTH', 'TR_SP':'MP_CANOPY_SP'}).set_index(sumLevel)
arcpy.AddMessage('    clean DF Created')

# Assemble clean dataframes into a single dataframe for export
arcpy.AddMessage ('assembling component data frames')
OUT_DF = SUMdf.join([OPH_clean, HMH_clean, TSH_clean, NSH_clean, CNP_clean, OPH_TPA]).reset_index()
arcpy.AddMessage ('assembly complete')

# Export assembled dataframe into ESRI-Land
OUT_DF.spatial.to_table(location=outDF)
arcpy.AddMessage ('export complete')
arcpy.AddMessage ('script complete')

































