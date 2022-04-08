#Do the imports
import arcpy
import os

# Define Inputs
inGeom = arcpy.GetParameterAsText(0) #r"\\mvrdfs.mvr.ds.usace.army.mil\egis\Work\EMP\HREP_Projects\Pool_12_Forestry\Data\ForestInventory_ForAGOL\Forest_Inventory_AGOL.gdb\Pool12_ForestInventory_Sites"
inStandSum = arcpy.GetParameterAsText(1) #r"\\mvrdfs.mvr.ds.usace.army.mil\egis\Work\EMP\HREP_Projects\Pool_12_Forestry\Data\ForestInventory_ForAGOL\Forest_Inventory_AGOL.gdb\Site_StandSummary"
inPlotSum = arcpy.GetParameterAsText(2) #r"\\mvrdfs.mvr.ds.usace.army.mil\egis\Work\EMP\HREP_Projects\Pool_12_Forestry\Data\ForestInventory_ForAGOL\Forest_Inventory_AGOL.gdb\Site_PlotSummary"
inPandasSum = arcpy.GetParameterAsText(3) #r"\\mvrdfs.mvr.ds.usace.army.mil\egis\Work\EMP\HREP_Projects\Pool_12_Forestry\Data\ForestInventory_ForAGOL\Forest_Inventory_AGOL.gdb\Site_WebVarPandas"
inSumLevel = arcpy.GetParameterAsText(4) #'SITE'
arcpy.SetParameterAsText(5, inGeom)

PandasFields = ["OVERALL_HLTH",
                "HARD_MAST_HLTH",
                "MP_TYP_HLTH",
                "MP_TYP_SP",
                "MP_NTYP_HLTH",
                "MP_NTYP_SP",
                "CANOPY_HLTH",
                "MP_CANOPY_SP",
                "H_TPA",
                "S_TPA",
                "SD_TPA",
                "D_TPA"
                ]

PlotSumFields = ["OV_CLSR",
                 "OV_HT",
                 "UND_COV",
                 "UND_HT",
                 "TR_AGE"
                 ]

StandSumFields = ["NUM_TR",
                  "SPP_RICH",
                  "AV_BA",
                  "AV_TPA",
                  "SAP_TPA",
                  "POL_TPA",
                  "SAW_TPA",
                  "MAT_TPA",
                  "OVM_TPA",
                  "SNAG_TPA",
                  "LG_SNAG_TPA",
                  "HRD_MAST",
                  "SFT_MAST",
                  "NUM_PL",
                  "QM_DBH"
                  ]
arcpy.AddMessage ('imports done & global variables defined')

# Join Pandas Summary Variables
arcpy.JoinField_management(in_data=inGeom,
                           in_field=inSumLevel,
                           join_table=inPandasSum,
                           join_field=inSumLevel,
                           fields=PandasFields)
arcpy.AddMessage ('Pandas summary fields joined to geometry')


# Join Plot Summary Variables
arcpy.JoinField_management(in_data=inGeom,
                           in_field=inSumLevel,
                           join_table=inPlotSum,
                           join_field=inSumLevel,
                           fields=PlotSumFields)
arcpy.AddMessage ('Plot summary fields joined to geometry')

# Join Stand Summary Variables

arcpy.JoinField_management(in_data=inGeom,
                           in_field=inSumLevel,
                           join_table=inStandSum,
                           join_field=inSumLevel,
                           fields=StandSumFields)
arcpy.AddMessage ('Stand summary fields joined to geometry')
arcpy.AddMessage ('Joins complete, script complete')
                                

