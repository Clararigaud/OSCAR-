# RLE -> mineral file translator
# based on RLE encoding as described there -> http://www.conwaylife.com/wiki/RLE 
from getConfigFromFile import *
from classes import *
def translate(file, objectposx, objectposy):
    worldwidth = 36
    worldheight = 9
    tobeclosed = open("initfiles/"+file+".rle", 'r')
    c = tobeclosed.read()
    lines = c.split("\n")
    width = 0
    height = 0
    linecounter = objectposy
    colcounter = objectposx
    
    strdead = "agent dead"
    strlive = "agent live"
    digits = ["0","1","2","3","4","5","6","7","8","9"]
    multiple = ""
    for line in lines:
        if line[0] == "x":
            sizeparam = line.split(",")
            width = int(sizeparam[0].split("=")[1])
            height = int(sizeparam[1].split("=")[1])

        elif line[0] in digits or line[0] == "o" or line[0] == "O" or line[0] == "b" or line[0] == "B" or line[0] == "$" or line[0] == "!":
            for char in line:
                if char == "o" or char =="O":
                    if multiple == "":
                        strlive+=" (%s,%s)"%(colcounter,linecounter)
                        colcounter+=1
                    else :
                        m = int(multiple)
                        strlive+=" (%s:%s,%s)"%(colcounter,m+colcounter,linecounter)
                        multiple = ""
                        colcounter+=m
                elif char == "b" or char =="B":
                    if multiple == "":
                        strdead+=" (%s,%s)"%(colcounter,linecounter)
                        colcounter+=1
                    else :
                        m = int(multiple)
                        strdead+=" (%s:%s,%s)"%(colcounter,m+colcounter,linecounter)
                        multiple = ""
                        colcounter+=m
                        
                elif char =="$":
                    if colcounter < width:
                        strdead+=" (%s:%s,%s)"%(colcounter,width,linecounter)
                    linecounter+=1
                    colcounter = objectposx
                elif char =="!":
                    if colcounter < width:
                        strdead+=" (%s:%s,%s)"%(colcounter,width,linecounter)
                    linecounter+=1
                    colcounter = objectposx
                    if linecounter < height:
                        strdead+=" (0:%s,%s:%s)"%(width,linecounter,height)
                    linecounter = height
                elif char in digits:
                    multiple+= char

    gameoflifecontent = "world %s %s #FF0"%(width,height)
    gameoflifecontent+="\n\nmineral dead #FFF\nvar neighbour\nstatus neighbour = 3 live\nsensor neighbour life 1\n\nmineral live #000\nvar life 2\nvar neighbour\nstatus neighbour < 2 dead\nstatus neighbour > 1 live\nstatus neighbour > 3 dead\nfield life -1\nsensor neighbour life 1\n\n"
    gameoflifecontent+= strdead+"\n"
    gameoflifecontent+=strlive
    tobeclosed.close()
    new = open("initfiles/"+file+".txt", 'w')

    new.write(gameoflifecontent)
    
    print(gameoflifecontent)
    new.close()
    
if __name__ == "__main__" :
    file = "gosperglidergun"
    translate(file,0,0)
    dico =getConfigFromFile("initfiles/"+file+".txt")
    #bigbang
    World(dico)
