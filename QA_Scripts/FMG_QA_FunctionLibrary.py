# -*- coding: UTF-8 -*-
# FMG QA Tools Function Library

import arcpy
import os, sys, math



def check_Plot_IDs(FC_Master, Master_PlotID_Field, FC_Check, Check_PlotID_Field):
    # NEED TO CHECK MASTER FC TO ENSURE PLOT ID FIELD IS OF TYPE SHORT INTEGER
    """Checks plot id's on a given input FMG field dataset (Fixed, Prism, Age) based on a list
    of plot IDs generated from a master set of plot IDs, this master set of plot IDs can be the
    target shapefile of plot locations used in TerraSync, the target Plot feature class used in
    TerraFlex/Collector or the Fixed plot locations, assuming that the fixed plots have correct
    Plot IDs. The function returns the string path to the checked dataset.

    Keyword Arguments:
    FC_Master           --  The path to the feature class or table that contains the full list
                            of plot IDs, against which the field data will be checked.
    Master_PlotID_Field --  The field name containing Plot IDs
    FC_Check            --  The path to the feature classs or table that contains the field
                            data requiring plot ID checks
    Check_PlotID_Field  --  The field name containing Plot IDs
    """

    # Check Plot ID Fields to ensure they are integer
    MasterDescribe = arcpy.Describe(FC_Master)
    for M_Field in MasterDescribe.fields:
        if M_Field.name == Master_PlotID_Field:
            if M_Field.type not in ('SmallInteger', 'Integer'):
                arcpy.AddError('Master Plot ID field type must be short or long integer, quitting.')
                sys.exit(0)
                
    CheckDescribe = arcpy.Describe(FC_Check)
    for C_Field in CheckDescribe.fields:
        if C_Field.name == Check_PlotID_Field:
            if C_Field.type not in ('SmallInteger', 'Integer'):
                arcpy.AddError('Check Plot ID field type must be short or long integer, quitting.')
                sys.exit(0)
                
    # Create a set of all valid PLOT IDs
    Plot_IDs = set([row[0] for row in arcpy.da.SearchCursor(FC_Master, Master_PlotID_Field)])

    # Add a field to the Feature Class being Checked
    FlagField = arcpy.AddField_management(in_table = FC_Check,
                              field_name = "VALID_PLOT_ID",
                              field_type = 'TEXT',
                              field_length = 3)
    arcpy.AddMessage('VALID_PLOT_ID field added to '.format(FC_Check))

    # Run through the Feature Class being Checked, using new field to flag rows with Plot IDs that
    # do not match the list initially created
    with arcpy.da.UpdateCursor(FC_Check, [Check_PlotID_Field, "VALID_PLOT_ID"]) as cursor:
        for row in cursor:
            if row[0] in Plot_IDs:
                row[1] = 'Yes'
            elif row[0] not in Plot_IDs:
                row[1] = 'No'
            cursor.updateRow(row)
        del row, cursor
        
    arcpy.AddMessage('VALID_PLOT_ID populated, check complete')

    return FC_Check


def check_Fixed_Offset(FC_PlotLocations, PlotID_Field, FC_Fixed, Fixed_PlotID_Field):
    """Checks the location of fixed plots against the initial set of target plots by creating
    a new field on the fixed plot dataset and populating it with the distsnce it is from the
    target plot location. This distance should be in meters, which means both input feature
    classes must have a coordinate system in meters.

    Keyword Arguments:
    FC_PlotLocations    --  The path to the feature class containing the target plot locations
    PlotID_Field        --  The field name containing Plot IDs of the target plot locations
    FC_Fixed            --  The path to the feature class containing fixed plot locations
    Fixed_PlotID_Field  --  The field name containing Plot IDs of the fixed plot locations
    """

    # Add field to Fixed plots to hold the offset distance in meters
    arcpy.AddField_management(in_table = FC_Fixed,
                              field_name = "DIST_FROM_TARGET_M",
                              field_type = "DOUBLE")
    arcpy.AddMessage('Field DIST_FROM_TARGET_M added to {0}'.format(FC_Fixed))

    # Define an empty list to hold master plot locations
    Master_Plot_Locations = []

    # Create a list of tuples from the Plot Locations tuple format will be (Plot ID, X, Y)
    with arcpy.da.SearchCursor (FC_PlotLocations, (PlotID_Field, 'SHAPE@X', 'SHAPE@Y')) as cursor:
        for row in cursor:
            Master_Plot_Locations.append(row)
        del row, cursor

    # Create an update cursor on the Fixed plot locations
    arcpy.AddMessage('Calculating horizontal offset between Fixed plots and plot centers')
    with arcpy.da.UpdateCursor (FC_Fixed, (Fixed_PlotID_Field, 'SHAPE@X', 'SHAPE@Y', 'DIST_FROM_TARGET_M')) as cursor:
        for row in cursor:
            for MPL in Master_Plot_Locations:
                if row[0] == MPL[0]:
                    # Calculate the fixed plot offset from the target plot location
                    dX = float(MPL[1]) - float(row[1])
                    dY = float(MPL[2]) - float(row[2])
                    dXY = math.sqrt((float(dX)**2) + (float(dY)**2))
                    row[3] = float(dXY)
                cursor.updateRow(row)
        del row, cursor
    arcpy.AddMessage('Offsets calculated')

    return FC_Fixed


                    
def check_Prism_Fixed (FC_Prism, Prism_PlotID, FC_Fixed, Fixed_PlotID):
    """ Checks to make sure there is a prism plot for every fixed plot and that there is a
    prism plot for each fixed plot. This is accomplished by comparing unique sets of plot
    IDs present for each feature class and populating fields indicating if this relationship
    holds true

    Keyword Arguments:
    FC_Prism      -- Path to prism feature class
    Prism_PlotID  -- Prism feature class plot ID field
    FC_Fixed      -- Path to fixed plot feature class
    Fixed_PlotID  -- Fixed feature class plot ID field
    """

    # Create sets of unique prism plot IDs and unique fixed plot IDs
    PrismPlotIDs = set([row[0] for row in arcpy.da.SearchCursor(FC_Prism, Prism_PlotID)])
    FixedPlotIDs = set([row[0] for row in arcpy.da.SearchCursor(FC_Fixed, Fixed_PlotID)])

    # Add fields to fixed and prism feature classes
    arcpy.AddField_management(in_table = FC_Prism,
                              field_name = "HAS_FIXED",
                              field_type = "TEXT",
                              field_length = 5)
    arcpy.AddMessage('HAS_FIXED field added to {0}'.format(FC_Prism))
    
    arcpy.AddField_management(in_table = FC_Fixed,
                              field_name = "HAS_PRISM",
                              field_type = "TEXT",
                              field_length = 5)
    arcpy.AddMessage('HAS_PRISM field added to {0}'.format(FC_Fixed))

    # Populate HAS_FIXED field, yes if there is a corresponding Fixed Plot, no if there isn't
    with arcpy.da.UpdateCursor(FC_Prism, [Prism_PlotID, "HAS_FIXED"]) as cursor:
        for row in cursor:
            if row[0] in FixedPlotIDs:
                row[1] = 'Yes'
            elif row[0] not in FixedPlotIDs:
                row[1] = 'No'
            cursor.updateRow(row)
        del row, cursor
    arcpy.AddMessage('Prism points {0} checked for corresponding fixed points'.format(FC_Prism))

    # Populate HAS_PRISM field, yes if there is a corresponding prism plot and no if there isn't
    with arcpy.da.UpdateCursor(FC_Fixed, [Fixed_PlotID, "HAS_PRISM"]) as cursor:
        for row in cursor:
            if row[0] in PrismPlotIDs:
                row[1] = 'Yes'
            elif row[0] not in PrismPlotIDs:
                row[1] = 'No'
            cursor.updateRow(row)
        del row, cursor
    arcpy.AddMessage('Fixed points {0} checked for corresponding prism points'.format(FC_Fixed))
        
    return [FC_Prism, FC_Fixed]
    

def check_Contractor_Age_Plots(FC_Plots, Plots_PlotID, Age_FlagField, FC_Age, Age_PlotID):
    """Checks prescribed age plots against collected age plots. Returns the prescribed age
    plots with a flag field indicating if an age plot was collected.

    Keyword Arguments:
    FC_Plots       --  Path to feature class of required plot locations
    Plots_PlotID   --  Field name of Plot ID column for required plot location feature class
    Age_FlagField  --  Field name of age requirement flag field for required plot location feature class
    FC_Age         --  Path to feature class of contractor submitted age plots
    Age_PlotID     --  Field name of Plot ID column for contractor submitted age plot feature class
    """

    # Create sets of Plots ID for collected age plots
    Required_Age_PlotIDs = set([row[0] for row in arcpy.da.SearchCursor(FC_Plots, Plots_PlotID, "{0} = 'A'".format(Age_FlagField))])
    Existing_Age_PlotIDs = set([row[0] for row in arcpy.da.SearchCursor(FC_Age, Age_PlotID)])
    

    # Check to ensure Age plots exit where required, adding and populating a flag field on the Plot feature class
    arcpy.AddField_management(in_table = FC_Plots,
                              field_name = "HAS_AGE",
                              field_type = "TEXT",
                              field_length = 5)
    arcpy.AddMessage('Field HAS_AGE added to {0}'.format(FC_Plots))

    with arcpy.da.UpdateCursor(FC_Plots, [Plots_PlotID, "HAS_AGE"]) as cursor:
        for row in cursor:
            if row[0] in Existing_Age_PlotIDs:
                row[1] = 'Yes'
            elif row[0] not in Existing_Age_PlotIDs:
                row[1] = 'No'
            cursor.updateRow(row)
        del row, cursor
    arcpy.AddMessage('Plot points checked for corresponding age record')

    return FC_Plots


def check_Required_Fields_Prism(FC_Prism):

    arcpy.AddMessage("Begin check on Prism points")

    # List of required fields
    RF_Prism = ['TR_SP', 'TR_DIA', 'TR_CL', 'TR_HLTH', 'TR_CREW', 'TR_DATE', 'HAS_MIS_FIELD', 'MIS_FIELD']
    
    # Add check fields to input feature classes
    arcpy.AddField_management(in_table = FC_Prism,
                              field_name = "HAS_MIS_FIELD",
                              field_type = "TEXT",
                              field_length = 5)
    arcpy.AddField_management(in_table = FC_Prism,
                              field_name = "MIS_FIELD",
                              field_type = "TEXT",
                              field_length = 80)
    arcpy.AddMessage('    Fields added to {0}'.format(FC_Prism))

    # Populate HAS_MIS_FIELD if null values exist in required fields where TR_SP = NONE
    row_count = len(list(i for i in arcpy.da.SearchCursor(FC_Prism, RF_Prism, "TR_SP = 'NONE'")))
    if row_count == 0:
        arcpy.AddMessage('    No records found where TR_SP = NONE')
    elif row_count != 0:
        with arcpy.da.UpdateCursor(FC_Prism, RF_Prism, "TR_SP = 'NONE'")as cursor:
            for row in cursor:
                if None in row[4:6]:
                    row[6] = 'Yes'
                elif None not in row[4:6]:
                    row[6] = 'No'
                cursor.updateRow(row)
            del row, cursor
        arcpy.AddMessage('    HAS_MIS_FIELD populated for no tree records')
    

    # Populate HAS_MIS_FIELD if null values exist in required fields for all other records
    row_count = len(list(i for i in arcpy.da.SearchCursor(FC_Prism, RF_Prism, "TR_SP <> 'NONE' OR TR_SP IS NULL")))
    if row_count == 0:
        arcpy.AddMessage(    "No records contain tree species")
    elif row_count != 0:
        with arcpy.da.UpdateCursor(FC_Prism, RF_Prism, "TR_SP <> 'NONE' OR TR_SP IS NULL")as cursor:
            for row in cursor:
                if None in row[0:6]:
                    row[6] = 'Yes'
                elif None not in row[0:6]:
                    row[6] = 'No'
                cursor.updateRow(row)
            del row, cursor
        arcpy.AddMessage('    HAS_MIS_FIELD populated for treed records')   

    # Check to ensure rows exist with tree species type 'NONE' and missing fields, then populate MIS_FIELD with missing field names
    arcpy.MakeQueryTable_management(in_table = FC_Prism,
                                    out_table = 'Q_Table',
                                    in_key_field_option = "NO_KEY_FIELD",
                                    where_clause = "HAS_MIS_FIELD = 'Yes' AND TR_SP = 'NONE'") # Query validated
    QueryRows = int(arcpy.GetCount_management('Q_Table').getOutput(0))
    arcpy.Delete_management('Q_Table') 
    if QueryRows != 0:
        with arcpy.da.UpdateCursor(FC_Prism, RF_Prism, "HAS_MIS_FIELD = 'Yes' AND TR_SP = 'NONE'") as cursor:
            for row in cursor:
                MissingFields = []
                if row[4] is None:
                    MissingFields.append(RF_Prism[4])
                elif row[5] is None:
                    MissingFields.append(RF_Prism[5])
                row[7] = (', '.join(map(str, MissingFields)))
                cursor.updateRow(row)
                MissingFields = []
            del row, cursor
    arcpy.AddMessage('    MIS_FIELDS populated for no tree records')

    # Populate MIS_FIELDS with missing field names for all other cases
    arcpy.MakeQueryTable_management(in_table = FC_Prism,
                                    out_table = 'Q_Table',
                                    in_key_field_option = "NO_KEY_FIELD",
                                    where_clause = "HAS_MIS_FIELD = 'Yes' AND TR_SP <> 'NONE' OR TR_SP IS NULL")
    QueryRows = int(arcpy.GetCount_management('Q_Table').getOutput(0))
    arcpy.Delete_management('Q_Table')
    if QueryRows != 0:
        with arcpy.da.UpdateCursor(FC_Prism, RF_Prism, "HAS_MIS_FIELD = 'Yes' AND TR_SP <> 'NONE' OR TR_SP IS NULL") as cursor:
            for row in cursor:
                MissingFields = []
                for i in range(0, len(row[2:])):
                    if row[i] is None:
                        MissingFields.append(RF_Prism[i])
                row[7] = (', '.join(map(str, MissingFields)))
                cursor.updateRow(row)
                MissingFields = []
            del row, cursor  
    arcpy.AddMessage('    MIS_FIELDS populated for treed records')

    return FC_Prism
    
        
def check_Required_Fields_Age(FC_Age):

    arcpy.AddMessage("Begin check on Age points")

    # List of required fields
    RF_Age = ['AGE_SP', 'AGE_DIA', 'AGE_HT', 'AGE_ORIG', 'AGE_GRW', 'AGE_CREW', 'AGE_DATE', 'HAS_MIS_FIELD', 'MIS_FIELD']

    # Add check fields to input feature classes
    arcpy.AddField_management(in_table = FC_Age,
                              field_name = "HAS_MIS_FIELD",
                              field_type = "TEXT",
                              field_length = 5)
    arcpy.AddField_management(in_table = FC_Age,
                              field_name = "MIS_FIELD",
                              field_type = "TEXT",
                              field_length = 80)
    arcpy.AddMessage('    Fields added to {0}'.format(FC_Age))

    # Populate HAS_MIS_FIELD
    with arcpy.da.UpdateCursor(FC_Age, RF_Age)as cursor:
        for row in cursor:
            if None in row[0:7]:
                row[7] = 'Yes'
            elif None not in row[0:7]:
                row[7] = 'No'
            cursor.updateRow(row)
        del row, cursor
    arcpy.AddMessage('    HAS_MIS_FIELD populated')
    
    # Populate MIS_FIELDS with missing field names for all other cases
    arcpy.MakeQueryTable_management(in_table = FC_Age,
                                    out_table = 'Q_Table',
                                    in_key_field_option = "NO_KEY_FIELD",
                                    where_clause = "HAS_MIS_FIELD = 'Yes'")
    QueryRows = int(arcpy.GetCount_management('Q_Table').getOutput(0))
    arcpy.Delete_management('Q_Table')
    if QueryRows != 0:
        with arcpy.da.UpdateCursor(FC_Age, RF_Age, "HAS_MIS_FIELD = 'Yes'") as cursor:
            for row in cursor:
                MissingFields = []
                for i in range(0, len(row[2:])):
                    if row[i] is None:
                        MissingFields.append(RF_Age[i])
                row[8] = (', '.join(map(str, MissingFields)))
                cursor.updateRow(row)
                MissingFields = []
            del row, cursor  
    arcpy.AddMessage('    MIS_FIELDS populated')

    return FC_Age

    

    
    
def check_Required_Fields_Fixed(FC_Fixed):

    arcpy.AddMessage('Begin check on Fixed plots')

    # List of required fields
    RF_Fixed = ['OV_CLSR', 'OV_HT', 'UND_HT', 'UND_COV', 'UND_SP1', 'GRD_SP1', 'FP_CREW', 'FP_DATE', 'HAS_MIS_FIELD', 'MIS_FIELD']

    # Add check fields to input feature classes
    arcpy.AddField_management(in_table = FC_Fixed,
                              field_name = "HAS_MIS_FIELD",
                              field_type = "TEXT",
                              field_length = 5)
    arcpy.AddField_management(in_table = FC_Fixed,
                              field_name = "MIS_FIELD",
                              field_type = "TEXT",
                              field_length = 80)
    arcpy.AddMessage('    Fields added to {0}'.format(FC_Fixed))

    # Populate HAS_MIS_FIELD
    with arcpy.da.UpdateCursor(FC_Fixed, RF_Fixed) as cursor:
        for row in cursor:
            if None in row[0:8]:
                row[8] = 'Yes'
            elif None not in row[0:8]:
                row[8] = 'No'
            cursor.updateRow(row)
        del row, cursor
    arcpy.AddMessage('    HAS_MIS_FIELD populated')
    
    # Populate MIS_FIELDS with missing field names for all other cases
    arcpy.MakeQueryTable_management(in_table = FC_Fixed,
                                    out_table = 'Q_Table',
                                    in_key_field_option = "NO_KEY_FIELD",
                                    where_clause = "HAS_MIS_FIELD = 'Yes'")
    QueryRows = int(arcpy.GetCount_management('Q_Table').getOutput(0))
    arcpy.Delete_management('Q_Table')
    if QueryRows != 0:
        with arcpy.da.UpdateCursor(FC_Fixed, RF_Fixed, "HAS_MIS_FIELD = 'Yes'") as cursor:
            for row in cursor:
                MissingFields = []
                for i in range(0, len(row[2:])):
                    if row[i] is None:
                        MissingFields.append(RF_Fixed[i])
                row[9] = (', '.join(map(str, MissingFields)))
                cursor.updateRow(row)
                MissingFields = []
            del row, cursor  
    arcpy.AddMessage('    MIS_FIELDS populated')

    return FC_Fixed
                                     



    
                       
    

    
        
                                
    


	
	

    
            
    
    
                  
    
