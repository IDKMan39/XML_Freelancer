import sys
import xml.etree.ElementTree as ET
import os
import re

global ids
ids = []

def parsetable(table,id):
    dl = ET.Element("dl")
    dl.set("id",id)
    for row in table:
        if row.tag == "row":
            name = ""
            dlentry = ET.SubElement(dl, "dlentry")
            if len(row.attrib) > 0 :
                for i in row.attrib.keys():
                    dlentry.set(i,row.attrib.get(i))

            for i in range(len(row)) :
                term = row[i]
                if i == 0 and "id" not in row.attrib.keys() :
                    for n in term.itertext():
                        name += re.sub("[^A-Za-z0-9]+","_",n)

                    if name[-1]== "_" :
                        name+= "Term"
                    else :
                        name += "_Term"
                    if name[0] == "_":
                        name = name.replace("_","",1)

                    if name in ids :
                        name += "_"+str(ids.count(name)+1)
                    ids.append(name)
                    dlentry.set("id",name)

                if term.find("p") is not None:
                    term = term.find("p")


                if i == 0:
                    tag = "dt"
                else :
                    tag = "dd"
                dt = ET.SubElement(dlentry, tag)
                dt.text = term.text
                for e in term:
                    dt.append(e)
                dt.tail = term.tail


    return dl

argumentslist = sys.argv
#treeinput = ET.parse("input.dita")
inputfilename = str(argumentslist[1])
outputfilename = str(argumentslist[2])



print(outputfilename)
print(inputfilename)
treeinput = ET.parse(inputfilename)
rootinput = treeinput.getroot()

bodyroot = rootinput.find("body")
tableroot = bodyroot.find("table")
num = 0
numentry = 0
tableroot.find("tgroup").remove(tableroot.find("tgroup").find("thead"))
tablebodyroot = tableroot.find("tgroup").find("tbody")

newdl = parsetable(tablebodyroot,tableroot.get("id"))

bodyroot.remove(tableroot)
bodyroot.append(newdl)

print('----------------')
ET.indent(treeinput,space = "   ", level =0)


treeinput.write(outputfilename)
add = ""
with open(inputfilename,"r") as f:
    with open(outputfilename, 'r+') as f1:
        content = open(outputfilename, 'r+').read()
        for line in f.readlines():
            if "<?xml" in line :
                add += line
            if "<!DOCTYPE" in line:
                add += line

        f1.seek(0)
        f1.write(add  + content)
