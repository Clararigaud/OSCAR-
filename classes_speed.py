# ========================================================================================================================
"""OSCAR"""
# ========================================================================================================================
__author__  = "Clara Rigaud"
__version__ = "2.0" 
__date__    = "2016-12-06"
# ========================================================================================================================
from tkinter import *
from random import randint as rd
from getConfigFromFile import *
import copy
import numpy
# ------------------------------------------------------------------------------------------------------------------------
class World(object):
    """ """
    def __init__(self, config):
        self.nbCol = config["world"]["nbCol"]
        self.nbRow = config["world"]["nbRow"]
        self.color = config["world"]["color"]       
        self.agents = []
        self.occupied = [[False for i in range(self.nbCol)]for j in range(self.nbRow)]
        self.models = {}
        self.species = {}
        self.age = 0
        self.instances = None
        if config["instances"] != {}:   
            self.instances = config["instances"]
        else :
            print("Attention, aucune instanciation dans le fichier de config, il ne va pas se passer grand chose")
        #fenetre params 
        self.win = Tk()
        self.win.title("Oscar")
        self.header = Frame(self.win)
        self.timerlabel = Label(self.header, text="T"+str(self.age))
        self.timerlabel.grid(row = 0, column=0)
        self.button = Button(self.header, command = self.startTime, text="start")
        self.button.grid(row =0, column=1)
        self.header.pack()
        self.largeur = 25
        self.simuspeed = 500 #ms
        self.frame = Canvas(self.win, width = self.largeur*self.nbCol, height = self.largeur*self.nbRow, bg=self.color)        
        self.fieldMap = {}
        for i in range(self.nbRow):
            x0,x1 = i*self.largeur,(i+1)*self.largeur
            for j in range(self.nbCol):
                y0,y1 = j*self.largeur,(j+1)*self.largeur
                self.frame.create_rectangle(x0,y0,x1,y1, fill = self.color)

        #création des classes
        for famille, sousfamille in config["agents"].items():
            for nom, params in sousfamille.items():
                self.species[nom] = self.createClass(eval(famille), nom, self, **params)
                self.models[nom] = self.species[nom](0,0)
        if self.instances: self.createAgents()
              
        print("Created a world",self.nbRow,"x",self.nbCol,"with",len(self.species),"species !")
        self.frame.pack()
        self.start = False
        print("Nb agents:", len(self.agents))
        self.win.mainloop()
        
    def createClass(self, derivedFrom, classname, world, **kwargs):
        if "field" in kwargs:
            
            for key,val in kwargs["field"].items():
                self.fieldMap[key] = {}
                self.fieldMap[key]["now"] = numpy.zeros((self.nbRow,self.nbCol))
                self.fieldMap[key]["futur"] = numpy.zeros((self.nbRow,self.nbCol))
        def __init__(self, posx, posy):
            derivedFrom.__init__(self, posx, posy, world, **kwargs)
        return type(classname, (derivedFrom,), {"__init__": __init__})

    def createAgents(self):
        for status,coordinates in self.instances.items() :
            for coords in coordinates:
                coords = coords.split(",")
                if ":" in coords[0] and ":" in coords[1]:
                    interX = coords[0].split(":")
                    interY = coords[1].split(":")
                    for i in range(int(interX[0]),int(interX[1])):
                        for j in range(int(interY[0]),int(interY[1])):
                            self.agents.append(self.createAgent(status, i, j))
                elif ":" in coords[0]:
                    interX = coords[0].split(":")
                    y = int(coords[1])
                    for i in range(int(interX[0]),int(interX[1])):
                        self.agents.append(self.createAgent(status, i, y))
                elif ":" in coords[1]:
                    interY = coords[1].split(":")
                    x = int(coords[0])
                    for i in range(int(interY[0]),int(interY[1])):
                        self.agents.append(self.createAgent(status, x, i))
                else :
                    self.agents.append(self.createAgent(status, int(coords[0]), int(coords[1])))
                    
        for i in range(len(self.agents)):
            for field,Map in self.fieldMap.items():
                if field in self.agents[i].fields:
                    self.fieldMap[field]["futur"]+=self.agents[i].fieldMap(field)
            
                    
    def createAgent(self, status, posx, posy):
        a = copy.deepcopy(self.models[status])
        a.posx = posx
        a.posy = posy
        a.rectangle = self.frame.create_rectangle(posx*self.largeur,posy*self.largeur,(posx+1)*self.largeur,(posy+1)*self.largeur, fill= a.color)
        a.world = self
        self.occupied[posy][posx]=True
        return a
 
    def updateAgents(self):
        for field,Map in self.fieldMap.items():
            Map["now"]=Map["futur"]
            Map["futur"]= numpy.zeros((self.nbRow,self.nbCol))
        self.agents = [agent.update() for agent in self.agents]
    
    def startTime(self):
        self.start = True
        self.button["command"] = self.pauseTime
        self.button["text"] = "stop"
        self.timeGoesOn()
        
    def pauseTime(self):
        self.start = False
        self.button["command"] = self.startTime
        self.button["text"] = "start"
        
    def timeGoesOn(self):
        if self.start:
            self.age +=1
            self.timerlabel["text"] ="T"+ str(self.age)
            self.updateAgents()
            self.win.after(self.simuspeed,self.timeGoesOn)   
# ------------------------------------------------------------------------------------------------------------------------            
class mineral(object): # à faire - privatiser les attributs lecture ecriture - verifier les types->asserts
    """"""
    def __init__(self, posx, posy, world, **params):
        """"""
        self.posx = posx
        self.posy = posy
        self.icone = None
        self.color = "#000"

        if params["colorIcone"][0]=="#":
            self.color = params["colorIcone"]
        elif params["colorIcone"][0]!= "":
            self.icone = params["colorIcone"]
        
        self.vars = {}
        if "var" in params:
            for varname,p in params["var"].items():
                self.vars[varname] = Var(varname, **p)

        self.fields = {}
        if "field" in params:
            for fieldname,p in params["field"].items():
                self.fields[fieldname] = Field(self.vars[fieldname], p["DistanceStepValue"])

        self.sensors = {}
        if "sensor" in params:
            for varname, p in params["sensor"].items():
                self.sensors[varname] = Sensor(self.vars[varname], p["FieldName"], p["SensitivityValue"])

        self.rules = []
        if "status" in params:
            for rules in params["status"]:
                if len(rules)==1:
                    self.rules.append([rules[0],"True"])                  
                else:
                    if rules[2]=="=": rules[2]+="="
                    self.rules.append([rules[0],"self.vars[\"%s\"].value"%rules[1] + rules[2] + rules[3]])
        self.world = None

    def __del__(self):
        if self.rectangle:   
            self.world.frame.delete(self.rectangle)
        
    def __str__(self):
        r = self.__class__.__name__
        r+=": "
        return r

    def fieldValueInPlace(self, fieldName, posx, posy):
        if fieldName in self.fields:
            res = self.fields[fieldName].value + self.fields[fieldName].DistanceStepValue*self.distance(posx,posy)
            if res<0:res = 0.0
            return res
        return 0.0
    
    def fieldMap(self, field):
        """return tab de taille world.nbCol, world.nbRow avec les valeurs du field sur chaque case"""
        return numpy.array([[(self.fieldValueInPlace(field,i,j))for i in range(self.world.nbCol)]for j in range(self.world.nbRow)])

    def evoluate(self):
        """Evalue toutes les regles de changement de status et renvoie un objet du nouvau statut de meme posx, posy, ou le meme """
        newStatus = None
        if self.rules:
            for rule in self.rules:
                if eval(rule[1]):
                    newStatus = rule[0]    
            if newStatus:
                if newStatus != self.__class__.__name__ :
                    a = self.world.createAgent(newStatus, self.posx, self.posy)
                    del self
                    return a
                else :
                    if self.vars:
                        for n, var in self.vars.items(): var.reset()
        return self

    def update(self):
        for nomvar, var in self.vars.items():
            if nomvar in self.sensors :
                  var.value += float(self.sensors[nomvar].SensitivityValue*self.world.fieldMap[self.sensors[nomvar].FieldName]["now"][self.posy,self.posx]- self.fieldValueInPlace(self.sensors[nomvar].FieldName, self.posx,self.posy))   
            var.update()
        temp = self.evoluate()   
        for nomvar, var in temp.vars.items():
            if nomvar in temp.world.fieldMap : temp.world.fieldMap[nomvar]["futur"]+= temp.fieldMap(nomvar)
        return temp
    
    def distance(self, posx,posy):
        res = max(abs(self.posx-posx),abs(self.posy-posy))
        return res
    
    def describeyourself(self):
        tab= " "*4
        r = "\nI'm a %s !"%self.__class__.__name__
        r += "\nColor: %s Icone:%s"%(self.color,self.icone)
        r += "\nVars :"
        if self.vars :
            for n, v in self.vars.items():
                r+="\n"+tab+"nom: %s valeur: %s TimeStepValue: %s"%(v.name,v.value,v.TimeStepValue)
        else: r+="No var"

        r+= "\nFields :"
        if self.fields :
            for n, v in self.fields.items():
                r+="\n"+tab+"nom: %s valeur: %s DistanceStepValue: %s"%(v.name,v.value,v.DistanceStepValue)
        else: r+=" No Field"
        
        r+="\nSensors:"
        if self.sensors :
            for n, v in self.sensors.items():
                r+="\n"+tab+"nom: %s FieldName: %s SensitivityValue: %s"%(v.name,v.FieldName,v.SensitivityValue)
        else: r+= " No sensor"

        r+="\nRules:"
        if self.rules :
            for rule in self.rules:
                r+="\n"+tab+"if %s then %s"%(rule[1],rule[0])
        else: r+=" No Rule"
        r+="\nPos:(%s,%s)"%(self.posx,self.posy)
        print(r)

class vegetal(mineral):
    def __init__(self, posx, posy, world, **params):
        mineral.__init__(self, posx, posy, world, **params)
        print("Creation vegetal")

        self.birth = []
        if "birth" in params:
            for rules in params["birth"]:
                if len(rules)==1:
                    self.birth.append([rules[0],"True"])                  
                else:
                    if rules[2]=="=": rules[2]+="="
                    self.birth.append([rules[0],"self.vars[\"%s\"].value"%rules[1] + rules[2] + rules[3]])

    def maximiseFields(self):
        b = self.belt()
        array = numpy.array([0 for i in range(len(b))])
        for name, sensor in self.sensors.items():
            for i in range(len(b)):
                array[i]+= self.world.fieldMap[sensor.FieldName]["now"][b[i][1],b[i][0]]*sensor.SensitivityValue
        if b != []:
            maxi = b[numpy.argmax(array)]
            return maxi
        return None

    def belt(self):
        """retourne un tableau des coordonnées:(x,y) à distance 1 de l'agent"""
        x,y = self.posx, self.posy
        minx,maxx,miny,maxy = x-1,x+1,y-1,y+1
        if minx<0:minx = x
        if miny<0:miny=y
        if maxx>=self.world.nbCol: maxx = x
        if maxy>=self.world.nbRow:maxy= y
        belt =[]
        for i in range(minx,maxx+1):
            for j in range (miny,maxy+1):
                if not(i==x and j==y) and not self.world.occupied[j][i]:
                    belt.append((i,j))
        return belt
    
    def update(self):
        for nomvar, var in self.vars.items():
            if nomvar in self.sensors :
                  var.value += float(self.sensors[nomvar].SensitivityValue*self.world.fieldMap[self.sensors[nomvar].FieldName]["now"][self.posy,self.posx]- self.fieldValueInPlace(self.sensors[nomvar].FieldName, self.posx,self.posy))   
            var.update()
        if self.birth != []:
            child = None
            for cas in self.birth:
                if eval(cas[1]):
                    child = cas[0]
            if child :  
                coords = self.maximiseFields()
                if coords :
                    self.world.agents.append(self.world.createAgent(child, coords[0], coords[1]))
        temp = self.evoluate()
        for nomvar, var in temp.vars.items():
            if nomvar in temp.world.fieldMap : temp.world.fieldMap[nomvar]["futur"]+= temp.fieldMap(nomvar)
        return temp
    
class animal(vegetal):
    def __init__(self, posx, posy, world, **params):
        vegetal.__init__(self, posx, posy, world, **params)
        print("Creation animal")    
# ------------------------------------------------------------------------------------------------------------------------        
class Sensor(object):
    """------------------------------------SENSOR--------------------------------------------"""
    def __init__(self, var, FieldName, SensitivityValue=0):
        assert isinstance(FieldName, str), "Le nom du field associé doit être de type string"
        assert isinstance(var, Var), "La variable associée dans être de type Var"
        assert type(SensitivityValue)==float, "SensitivityValue doit être un float"
        self.__var = var
        self.__name = self.__var.name
        self.__FieldName = FieldName
        self.__SensitivityValue = SensitivityValue
    def __str__(self):
        return "Var: %s, Field:%s, SensitivityValue: %s"%(self.__name, self.__FieldName, self.__SensitivityValue)
        
    @property
    def name(self):
        return self.__name

    @property
    def SensitivityValue(self):
        return self.__SensitivityValue

    @property
    def FieldName(self):
        return self.__FieldName
# ------------------------------------------------------------------------------------------------------------------------   
class Field(object):
    """---------------------------------------FIELD--------------------------------------------"""  
    def __init__(self, var, DistanceStepValue=0):
        assert isinstance(var, Var), "var doit être de type Var"
        assert type(DistanceStepValue)==float, "DistanceStepValue doit être un float"
        self.__var = var
        self.__name = self.__var.name
        self.__DistanceStepValue = DistanceStepValue
        self.__value = self.__var.value
    def __str__(self):
        return "Nom: %s, Valeur: %s, DistanceStepValue: %s"%(self.__name,self.__value, self.__DistanceStepValue)
    @property
    def name(self):
        return self.__var.name

    @property
    def DistanceStepValue(self):
        return self.__DistanceStepValue

    @property
    def value(self):
        return self.__var.value
        
# ------------------------------------------------------------------------------------------------------------------------ 
class Var(object):
    """---------------------------------------VAR--------------------------------------------"""
    def __init__(self, name, **params):
        self.__name = name
        self.__initvalue = params["InitValue"]
        self.__value = params["InitValue"]
        self.__TimeStepValue = params["TimeStepValue"]
        self.__tplus1value = 0.0
    def __str__(self):
        return "Nom: %s, Valeur: %s, TimeStep: %s"%(self.__name,self.__value, self.__TimeStepValue)

    @property
    def name(self):
        return self.__name

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, n):
        assert type(n)==float, "La valeur doit être exprimée en float"
        self.__value = n
        
    @property
    def TimeStepValue(self):
        return self.__TimeStepValue

    def reset(self):
        self.value = self.__initvalue
        
    def update(self):
        """incrémente la valeur de la variable de TimeStepValue"""
        self.value += self.__TimeStepValue
# =========================================================================================================================
if __name__ == "__main__" :
    filename = "oscar4"
    dico =getConfigFromFile("initfiles/"+filename+".txt")
    #bigbang
    World(dico)
