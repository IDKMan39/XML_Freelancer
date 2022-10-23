import sys
import xml.etree.ElementTree as ET
import os
import re
import copy
print("_____________________________________")

global counter
def findinsides(dlroot,hrefstrings):
    list = []
    searchlist = []
    for i in dlroot.findall("dlentry"):
        p = ET.Element("p")
        ph = ET.Element("ph")
        ph.set("otherprops","(@condition)")
        phnot = ET.Element("ph")
        phnot.set("otherprops","(!@condition)")


        xref = ET.SubElement(ph,"xref")
        xref.set("href",hrefstrings[dlroot.findall("dlentry").index(i)])
        first = i.find("dt")

        xref.text = first.text
        phnot.text = first.text
        p.text = first.text
        for e in first:
            xref.append(e)
            phnot.append(e)
            p.append(e)
        xref.tail = first.tail
        phnot.tail = first.tail
        p.tail = first.tail
        searcher = ET.tostring(p,"unicode").replace("<p>","").replace("</p>","")
        #print(ET.tostring(ph, 'unicode'))
        #print(ET.tostring(phnot, 'unicode'))
        list.append([ph,phnot])
        searchlist.append([searcher.rstrip(),p.text.rstrip(),p.tail.rstrip()])
    return [list,searchlist]

def domap(rootmap,searcherlist,builderlist,directory,hrefstrings) :
    global counter
    lineslist = []
    #print("call")
    for i in rootmap:
        add = ""
        if i.get("href") is not None:
            topicpath = i.get("href").replace("..","")
            if os.path.exists(directory + topicpath):

                topicpath = directory + topicpath
                with open(topicpath,"r+") as file:
                        for line in file.readlines():
                            if "<?xml" in line :
                                add += line
                            if "<!DOCTYPE" in line:
                                add += line

                lineslist.append(add)
                topicroot = ET.parse(topicpath)
                currentbodyroot = topicroot.find("body")
                fixlist(currentbodyroot,hrefstrings)
    for i in rootmap:
        if i.get("href") is not None:
            topicpath = i.get("href").replace("..","")
            if os.path.exists(directory + topicpath):
                parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True)) # Python 3.8

                topicpath = directory + topicpath
                topicroot = ET.parse(topicpath,parser)
                currentbodyroot = topicroot.find("body")

                #print(searcherlist)
                #print(builderlist)
                #print(lineslist)
                counter = 0
                while  counter < len(searcherlist) :
                    recur(currentbodyroot,searcherlist[counter][0],searcherlist[counter][1],searcherlist[counter][2],builderlist[counter][0],builderlist[counter][1],counter)
                    counter += 1

                topicroot.write(topicpath)
                content = open(topicpath, 'r+').read()
                with open(topicpath,"r+") as file:
                    file.seek(0)
                    file.write(lineslist[0] + content)
                    lineslist.pop(0)
                #print(ET.tostring(currentbodyroot,"unicode") + "<<<<NEWbody")

def recur(node,key,text,tail,ph,phnot,index) :
    global counter
    #if node.tag == "body" :
        #print("++++++++++++++++++++++++++++++++++++=")
    #print("searching " + node.tag + " " + key + " " + str(index))
    runs = False
    el = ET.tostring(node,'unicode')
    found = False
    #print(el)
    if el.find(key) == -1:  #The 0th element is the identifier string
        return False

    for i in node :
        runs = True
        found = False
        #print(key)
        istr = ET.tostring(i,'unicode')
        #print(istr)
        if istr.find(key) != -1 :
            #print(key)
            found = True
            if i.tag != "xref" and i.tag != "ph":
                if not recur(i,key,text,tail,ph,phnot,index):

                    #if i.tag == "ul" :

                        #print("PROBLEM____________")
                        #input()

                    #print(el)
                    if i.text is not None:
                        i.text = i.text.replace(text,"")
                    if "<" in key:
                        substring = key[key.find("<")+1:key.find(">")]
                        i.remove(i.find(substring))
                    i.append(ph)
                    i.append(phnot)

                    if i.tail is not None:

                        i.tail =  i.tail.replace(tail,"")

                    #print(el)
                    #input()
                    #print(searcherlist[index])
                    searcherlist.pop(index)
                    builderlist.pop(index)
                    counter -=1
                    return True

    if not runs :
        return False

    if found:
        return True

def fixlist(bodyroot,hrefstrings):
    global counter
    for i in bodyroot.iter():
        if i.tag == "xref" :
            if i.get("href") in hrefstrings :

                index = hrefstrings.index(i.get("href"))
                searcherlist.pop(index)
                builderlist.pop(index)
                hrefstrings.pop(index)


argumentslist = sys.argv
directory = os.getcwd()
outputfile = argumentslist[2]
#treeinput = ET.parse("input.dita")
mapfilename = str(directory + "\\maps\\" + argumentslist[1])
outputfilename = str( directory + "\\topics\\" + argumentslist[2])
print(f"{mapfilename} <--- MAP ")
print(f"{outputfilename} <--- OUTPUT ")



maptree = ET.parse(mapfilename)
rootmap = maptree.getroot()
outputtree = ET.parse(outputfilename)
rootoutput = outputtree.getroot() # TOPIC TAG
hrefstrings = []
outputid = rootoutput.attrib.get("id") #This is the ID needed for the xref
dlroot = rootoutput.find("body").find("dl") #List start

for i in dlroot.findall("dlentry"):
    hrefstrings.append(outputfile + "#" + outputid + "/" + i.attrib.get("id"))
infolist = findinsides(dlroot,hrefstrings)
builderlist = infolist[0]
searcherlist = infolist[1]
    #<xref href="output.dita#id-jadjhad-asjdhkjshd-ksadjgdsjhgsd/Term_1_TERM">Term 1</xref>
    #            output.dita#id-jadjhad-asjdhkjshd-ksadjgdsjhgsd/Term_1_TERM
domap(rootmap,searcherlist, builderlist,directory,hrefstrings)
