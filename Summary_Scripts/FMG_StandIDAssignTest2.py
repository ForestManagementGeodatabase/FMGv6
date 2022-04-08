# This script is intended to assign SID from a stand layer to plot data from the USACE Phase 2 Forest Inventory
#   dataset. Last Updated: 04SEPT2013

# Imports the prefixes for ArcGIS specific codes
import arcpy
from arcpy import env

# Comments written above code

arcpy.AddMessage('Beginning...')

arcpy.AddMessage('Identifying parameters')
stand = arcpy.GetParameterAsText(0)  # stand polygon data
sid = arcpy.GetParameterAsText(1)  # unique stand identifier text field from stand layer
fp_pts = arcpy.GetParameterAsText(2)  # fixed plot points data
pr_pts = arcpy.GetParameterAsText(3)  # prism point data
age_pts = arcpy.GetParameterAsText(4)  # age point data
p_sid = arcpy.GetParameterAsText(5)  # unique stand identifier text field from fixed plot data
pid = arcpy.GetParameterAsText(6)  # unique plot identifier from fixed plots data
arcpy.AddMessage('Parameters identified.')

env.workspace = fp_pts

# adds each SID to a list and looks for repeats of an SID

arcpy.AddMessage('Identifying stands...')
arcpy.SelectLayerByLocation_management(stand, "CONTAINS", fp_pts, "", "NEW_SELECTION")
cursor = arcpy.da.SearchCursor(stand, sid)
sid_list = []
t = 0
for row in cursor: 
    # global t
    step1 = str(row)
    step2 = step1.split("'")[1]
    if sid_list.count(str(step2)) == 0:
        sid_list.append(step2)
        t += 1
        if t == 1:
            arcpy.AddMessage("Identified "+str(t)+" stand...")
        else:
            arcpy.AddMessage("Identified "+str(t)+" stands...")
    else:
        arcpy.AddMessage('!!!!Error: Stand ID (SID) "'+str(step2)+'" occurs '+str(sid_list.count(step2)+1)+' times!!!!')
        import sys
        sys.exit(0)
del cursor

# For each Fixed Plot SID, selects points within the stand and updates the SID of those points
arcpy.AddMessage('Assigning stand ID (SID) to Fixed Plots...')
if len(sid_list) > 0:
    for i in sid_list:
        arcpy.SelectLayerByAttribute_management(stand, "NEW_SELECTION", str(sid)+"='"+str(i)+"'")
        arcpy.SelectLayerByLocation_management(fp_pts, "WITHIN", stand)
        # with arcpy.da.UpdateCursor(pts, [p_sid]) as cursor1:
        with arcpy.da.UpdateCursor(fp_pts, p_sid) as cursor1:
            arcpy.AddMessage("Point SID field = {}".format(p_sid))
            for plot in cursor1:
                plot = i
                cursor1.updateRow(plot)
    del cursor1

    arcpy.AddMessage('Flagging points outside of stands...')
    arcpy.SelectLayerByAttribute_management(stand, "NEW_SELECTION", '"OBJECTID" >= 0')
    arcpy.SelectLayerByAttribute_management(fp_pts, "NEW_SELECTION", '"OBJECTID" >= 0')
    arcpy.SelectLayerByLocation_management(fp_pts, "WITHIN", stand, "", "REMOVE_FROM_SELECTION")
    with arcpy.da.UpdateCursor(fp_pts, p_sid) as cursor2:
        for plot in cursor2:
            plot = '"FLAGGED_"' + '!'+str(p_sid)+'!'
            cursor2.updateRow(plot)
    del cursor2
    arcpy.SelectLayerByAttribute_management(fp_pts, "NEW_SELECTION", '"OBJECTID" < 0')
    arcpy.SelectLayerByAttribute_management(stand, "NEW_SELECTION", '"OBJECTID" < 0')
else:
    arcpy.AddMessage('Issue...')

# Updates the SID of Prism and Age plot features associated with each fixed plot
arcpy.AddMessage('Updating stand ID (SID) for Prism Plots...')
arcpy.AddJoin_management(pr_pts, pid, fp_pts, pid, "KEEP_COMMON")
arcpy.CalculateField_management(pr_pts, p_sid, "!"+str(fp_pts)+"."+str(p_sid)+"!", "PYTHON")
arcpy.RemoveJoin_management(pr_pts, fp_pts)

arcpy.AddMessage('Updating stand ID (SID) for Age Plots...')
arcpy.AddJoin_management(age_pts, pid, fp_pts, pid, "KEEP_COMMON")
arcpy.CalculateField_management(age_pts, p_sid, "!"+str(fp_pts)+"."+str(p_sid)+"!", "PYTHON")
arcpy.RemoveJoin_management(age_pts, fp_pts)

del list1
del t
del stand
del sid
del fp_pts
del pr_pts
del age_pts
del p_sid
del pid
