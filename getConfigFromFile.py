def getConfigFromFile(file):
    """ Takes a text file in parameters and returns an exploitable dict"""
    tobeclosed = open(file, 'r')
    tabParam = tobeclosed.read().split("\n\n")
    nbAgents = 0
    typeOfAgents = ["mineral", "vegetal", "animal"]
    world = {}
    agents = {}
    instances = {}
    agentname = []
    for paragraphe in tabParam : # pour chaque paragraphe
        words = paragraphe.split(" ")
        if words[0] == "world":    #info sur world
            world["nbCol"] = int(words[1])
            world["nbRow"] = int(words[2])
            world["color"] = words[3]
            
        elif words[0] in typeOfAgents : #paragraphe d'agent
            if words[0] not in agents: agents[words[0]]={} # un dictionnaire par type d'agent mineral-vegetal-animal

            lignes = paragraphe.split("\n") #contient chaque ligne du paragraphe               
            firstlineItems = lignes[0].split(" ")
            agentParams = {"colorIcone": firstlineItems[2]}
            for ligne in lignes[1:]: #pour chaque ligne du paragraphe agent
                mots = ligne.split(" ")
                tempmots = []
                i=0
                while i<len(mots) and mots[i] != "" and mots[i] != "#":
                    tempmots.append(mots[i])
                    i+=1
                mots = tempmots
                if mots != []:
                    if mots[0] not in agentParams : agentParams[mots[0]] = {}
                    
                    if mots[0] == "var":
                        agentParams[mots[0]][mots[1]] = {"InitValue" : 0.0, "TimeStepValue" : 0.0}
                        if len(mots)>2 : agentParams[mots[0]][mots[1]]["InitValue"] = float(mots[2])
                        if len(mots)>3 : agentParams[mots[0]][mots[1]]["TimeStepValue"] = float(mots[3])

                    elif mots[0] == "field":
                        agentParams[mots[0]][mots[1]] = {"DistanceStepValue" : 0.0}
                        if len(mots)>2 : agentParams[mots[0]][mots[1]]["DistanceStepValue"] = float(mots[2])                 
                        
                    elif mots[0] == "sensor":
                         agentParams[mots[0]][mots[1]] = {"FieldName" : mots[2], "SensitivityValue" : 0.0}
                         if len(mots)>3 : agentParams[mots[0]][mots[1]]["SensitivityValue"] = float(mots[3])                                 

                    elif mots[0] == "status" or mots[0] == "birth": #var #compare #to #newstatus
                        if agentParams[mots[0]] == {} : agentParams[mots[0]] = []
                        s = [mots[len(mots)-1]]
                        if len(mots)>2 : 
                            s+=mots[1:len(mots)-1]
                        agentParams[mots[0]].append(s)                           
            agents[words[0]][firstlineItems[1]] = agentParams
            agentname.append(firstlineItems[1])
        else:
            agentinstance = paragraphe.split("\n")
            for line in agentinstance:
                param = line.split(" ")
                if param[0]=="agent":
                    if param[1] in agentname:
                        if param[1] not in instances : instances[param[1]]=[]
                        for coords in param[2:]:
                            instances[param[1]].append(coords[1:len(coords)-1])
    tobeclosed.close()
    return {"world" : world, "agents":agents, "instances":instances}

if __name__ == "__main__" :
    import json
    file = "initfiles/oscar1.txt"
    dico = getConfigFromFile(file)
    print(json.dumps(dico, indent=4))
