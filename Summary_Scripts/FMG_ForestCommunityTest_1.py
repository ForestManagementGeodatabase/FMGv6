#This script is intended to generate a plot-level forest community types from the USACE Phase 2 Forest Inventory
#   dataset. Last Updated: 26MAR2013

#Comments written above code

arcpy.AddMessage('Beginning...')

#Imports the prefixes for ArcGIS specific codes
import arcpy
from arcpy import env

#Identifies the user-provided parameters from the GUI
arcpy.AddMessage('Identifying parameters...')
ivtable = arcpy.GetParameterAsText(0)
level = arcpy.GetParameterAsText(1)
tr_spp = arcpy.GetParameterAsText(2)
iv = arcpy.GetParameterAsText(3)
out_table = arcpy.GetParameterAsText(4)
out_table1 = arcpy.GetParameter(4)
pid_sum= arcpy.GetParameterAsText(5)
arcpy.AddMessage('Parameters identified.')

#Sets the workplace (where temporary files are written)
env.workspace = ivtable

#The codeblock that removes null values from the intermediate table's "INC_SPP" field
removenull = """def removenull(x):
    if x is None:
        return str('notsig')
    return x
    """


#The codeblock that defines the fuction used in determining the intermediate table's "INC_SPP" field for plots
plimpsppcode = """id = ""
n = 0
def comspp(a, b, c):
    global pid
    global n
    if a <> id:
        id = a
        n = c
        if c < 50:
            return b.lower()
        else:
            return b
    else:
        while n < 150:
            n += c
            if c < 50:
                return b.lower()
            else:
                return b
        else:
            return """""

#The codeblock that defines the fuction used in determining the intermediate table's "INC_IV" field for plots
plimpvalcode= """id =""
n = 0
def comsppiv(a, b, c):
    global id
    global n
    if a <> id:
        pid = a
        n = c
        return c
    else:
        while n < 150:
            n += c
            return c
        else:
            return 0"""


#The codeblock that defines the fuction used in determining the intermediate table's "INC_SPP" field for stands
stimpsppcode = """id = ""
n = 0
def comspp(a, b, c):
    global id
    global n
    if a <> id:
        id = a
        n = c
        if c < 75:
            return b.lower()
        else:
            return b
    else:
        while n < 225:
            n += c
            if c < 75:
                return b.lower()
            else:
                return b
        else:
            return """""

#The codeblock that defines the fuction used in determining the intermediate table's "INC_IV" field for stands
stimpvalcode= """id =""
n = 0
def comsppiv(a, b, c):
    global id
    global n
    if a <> id:
        id = a
        n = c
        return c
    else:
        while n < 225:
            n += c
            return c
        else:
            return 0"""

##################################################################################################################
##################################################################################################################

#Sorts input table by PID and importance value for more efficient plot level composition identification
sort_table = str(env.scratchWorkspace) + "\\sort_table"
arcpy.Sort_management(ivtable, sort_table, [[level, "ASCENDING"], [iv,"DESCENDING"]])

#Adds a field to identified species to include in the output table's "COM_SPP"
arcpy.AddField_management(sort_table, "INC_SPP", "TEXT")
#Adds a field for the importance value of individual species included in the output table's "COM_SPP" field
arcpy.AddField_management(sort_table, "INC_IV", "DOUBLE")

if pid_sum.lower() == "true":
    #Determines the included species using a custom defined function via the codeblock
    arcpy.CalculateField_management(sort_table, "INC_SPP", "comspp(!"+str(level)+"!, !"+str(tr_spp)+"!, !"+str(iv)+"!)", "PYTHON", plimpsppcode)
    #Determines the included species' importance values using a custom defined function via the codeblock
    arcpy.CalculateField_management(sort_table, "INC_IV", "comsppiv(!"+str(level)+"!, !"+str(tr_spp)+"!, !"+str(iv)+"!)", "PYTHON", plimpvalcode)
else:
    #Determines the included species using a custom defined function via the codeblock
    arcpy.CalculateField_management(sort_table, "INC_SPP", "comspp(!"+str(level)+"!, !"+str(tr_spp)+"!, !"+str(iv)+"!)", "PYTHON", stimpsppcode)
    #Determines the included species' importance values using a custom defined function via the codeblock
    arcpy.CalculateField_management(sort_table, "INC_IV", "comsppiv(!"+str(level)+"!, !"+str(tr_spp)+"!, !"+str(iv)+"!)", "PYTHON", stimpvalcode)

#Removes null values from "INC_SPP" field
arcpy.CalculateField_management(sort_table, "INC_SPP", "removenull(!INC_SPP!)", "PYTHON", removenull)

#Creats the final output table and provides a sum of the importance values for species that make up each plot's composition
arcpy.AddMessage('Building output table...')
arcpy.Statistics_analysis(sort_table, out_table, [["INC_IV", "SUM"]], level)
#Creates a field where the species that make of the community type will be listed
arcpy.AddField_management(out_table, "COM_SPP", "TEXT")
#Creates a field where the community type code will be provided
arcpy.AddField_management(out_table, "FCOM", "SHORT")

arcpy.AddMessage('Identifying forest communities...')
cursor1 = arcpy.da.SearchCursor(out_table, [level])
list1 = []
for row in cursor1:
    step1 = str(row)
    if step1 <> '(None),':
        step2 = step1.split("'")
        step3 = str(step2[1])
        if len(step3) == 0:
                arcpy.AddMessage('!!!!Error: '+level+' not being identified!!!!')
                import sys
                sys.exit(0)
        list1.append(step3)
    else:
        arcpy.AddMessage('!!!!Error: '+level+' not being identified!!!!')
        import sys
        sys.exit(0)
del row
del cursor1

p = len(list1)
n = 1


codeblock= """def calc(a, b, c, d):
    if str(a) == str(b):
        return c
    else:
        return d"""

#creates a concatenated text string of species that make up a plot's community composition
if n <= p:
    for x in list1:
        cursor2 = arcpy.da.SearchCursor(sort_table, ["INC_SPP"], '"'+str(level) + '"'+"='"+str(x)+"'")
        list2 = []
        for spp in cursor2:
            step1 = str(spp)
            if step1 <> "(u'notsig',)":
                step2 = step1.split("'")
                step3 = str(step2[1])
                if len(step3) == 0:
                    arcpy.AddMessage('!!!!Error: Species composition not being identified!!!!')
                    import sys
                    sys.exit(0)
                list2.append(step3)
            list2.sort()
        del spp
        del cursor2
        spot=""
        for y in list2:
            spot = str(spot)+str(y)
        arcpy.CalculateField_management(out_table, "COM_SPP", "calc(!"+str(level)+"!, '"+str(x)+"', '"+str(spot)+"', !COM_SPP!)", "PYTHON", codeblock)
        arcpy.AddMessage(str(level)+''+str(x)+' has a composition of '+str(spot)+'...')
        arcpy.AddMessage(str(p-(n))+' plots remaining...')
        n+=1

##################################################################################################################
##################################################################################################################
        
arcpy.AddMessage('Assigning forest community codes...')
#The codeblock that defines the custom fuction responsible for assigning forest community type codes
#####################################################
#Edit this codeblock if errors are made with assigning a code to a particular community type
#Changes in the order of the code definitions may fix or cause errors in assigning community type codes
fcomcode= """def fcom(x):
    if x == "ACNE2":
        return 12
    elif x == "ACSA2":
        return 1
    elif x == "FRPE":
        return 5
    elif x == "PODE3":
        return 7
    elif x == "SANI" or x == "SAIN3" or x=="SALIX":
        return 9
    elif x == "CEOC2" or x == "FOAC" or x.startswith("FOACSA") or x.startswith("FRPESA"):
        return 11
    elif x == "PLOC":
        return 13
    elif x=="CAAL27" or  x=="CAOV2" or x=="QUMA2" or x=="QUPA2" or x.startswith("CAIL2QU") or x.startswith("CAAL27ca"):
        return 10
    elif x == "CAIL2":
        return 14
    elif x == "JUNI":
        return 15
    elif x == "NONE":
        return 16
    elif x.startswith("PODE3SA") or x.startswith("ACSA2PODE3SA"):
        return 4
    elif x.startswith("ACNE2SA") or x.startswith("ACSA2SA") or x.startswith("ACSA2FRPESA"):
        return 8
    elif x.startswith("ACSA2PODE3") or x.startswith("FRPEPODE3") or x.startswith("ACNE2ACSA2PODE3") or x.startswith("ACNE2PODE3") or x.startswith("PODE3ac") or x.startswith("PODE3ULAM") or x.startswith("PODE3ulam"):
        return 3
    elif x.startswith("ac") or x.startswith("ULAM") or x.startswith("ACSA2sa") or x.startswith("ACSA2frpe") or x.startswith("FRPEac") or x.startswith("ACSA2ULAM") or x.startswith("ACSA2ulam") or x.startswith("ACNE2ACSA2") or x.startswith("ACSA2acne2") or x.startswith("ACNE2FRPE") or x.startswith("ACSA2FRPE"):
        return 2
    else:
        return 6"""
#####################################################

arcpy.CalculateField_management(out_table, "FCOM", "fcom(!COM_SPP!)", "PYTHON", fcomcode)

arcpy.Delete_management(sort_table)
arcpy.AddMessage('Tool complete.')
