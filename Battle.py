import Creature
import TextBox
import Map
import random
import pygame
import Attributes
from pygame.locals import *
import pygame.time
import GlobalData
import PlayerData
import TeamData

textureManager = GlobalData.textureManager
display = GlobalData.display


def loadBattleTextures():
    textureManager.loadTexture("battle","images/battle/BattleCursor.png", -1)
    for y in range(4):
        for x in range(2):
           textureManager.spriteRects["battle"].append(pygame.rect.Rect(x*24,y*24,24,24))


class Battle:
    def __init__(self, currMap, team):
        self.textureManager = textureManager
        self.display = display
        self.map = currMap
        self.numMonsters = random.randint(1,self.map.numMonsters)
        self.monsterNames = []
        self.team = team
        self.font = pygame.font.Font(None, 24)
        self.monArray = [[None for i in range(3)] for j in range(3)]
        self.monArrayNum = 0            
        self.battleMenu = BattleMenu(360, 312, ["Attack", "WTC", "HTC", "Item", "Run"])
        self.battleBox = BattleBox()
        self.selectedMonster = (0,0)
        self.selection = 0
        self.battleBool = True
        self.teamNum = 0
        self.selectedMember = self.team.team[0]
        self.selectedMemNum = 13
        self.actions = []
        self.executeMoves = False
        self.arrayPrinted = False
        
        
    def flipScreenBuffer(self):
        pygame.display.flip()
        
    def printMonArray(self):
        if self.arrayPrinted is False:
            for y in range(3):
                print "[",
                for x in range(3):
                    if self.monArray[x][y] is None:
                        print "None,",
                    else:
                        print self.monArray[x][y].name + ":" + str(self.monArray[x][y].HP) + ",",
                print "]"
            print "\n"    
            self.arrayPrinted = True    

    def battleMain(self):
        self.display.getScreen().blit(self.textureManager.textures["bg"][0], (0,0))
        self.height = 0
        for v in self.team.team:
            self.display.getScreen().blit(self.textureManager.textures[v.currentSkin][0], (504,96+self.height*32), self.textureManager.spriteRects[v.currentSkin][13])
            self.height+=1
        for x in range(self.numMonsters):
            self.monster = random.randint(0, len(self.map.monsters)-1)
            self.monsterNames.append(self.map.monsters[self.monster])
        for x in range(self.numMonsters):
            self.monArray[x%3][x/3] = Creature.Creature(self.monsterNames[x])
        
        while(self.battleBool):
            if self.executeMoves:
                self.ret = self.performActions()
                self.arrayPrinted = False
                if self.ret is not None:
                    return self.ret
                self.executeMoves = False                                   
            self.display.getScreen().blit(self.textureManager.textures["bg"][0], (0,0))
            if self.selectedMemNum != 17: 
                self.display.getScreen().blit(self.textureManager.textures[self.selectedMember.currentSkin][0], (504 - self.selectedMemNum%13*6,96), self.textureManager.spriteRects[self.selectedMember.currentSkin][self.selectedMemNum])
            else:
                self.display.getScreen().blit(self.textureManager.textures[self.selectedMember.currentSkin][0], (504 - 4*6,96), self.textureManager.spriteRects[self.selectedMember.currentSkin][13])    
            self.drawStats()     #for testing  
            self.displayMonsters()
            self.battleBox.show()
            self.battleMenu.show()
            if self.selection == 0:
                self.display.getScreen().blit(self.textureManager.textures["battle"][0], (442, 316), self.textureManager.spriteRects["battle"][1])
            elif self.selection == 1:
                self.display.getScreen().blit(self.textureManager.textures["battle"][0], (442, 316+24), self.textureManager.spriteRects["battle"][1])
            elif self.selection == 2:
                self.display.getScreen().blit(self.textureManager.textures["battle"][0], (442, 316+48), self.textureManager.spriteRects["battle"][1])
            elif self.selection == 3:
                self.display.getScreen().blit(self.textureManager.textures["battle"][0], (442, 316+72), self.textureManager.spriteRects["battle"][1])
            elif self.selection == 4:
                self.display.getScreen().blit(self.textureManager.textures["battle"][0], (442, 316+96), self.textureManager.spriteRects["battle"][1])
            self.flipScreenBuffer()
            pygame.time.delay(75)
            if self.selectedMemNum < 16:
                self.selectedMemNum += 1
            else:
                self.selectedMemNum = 17    
            for e in pygame.event.get():
                if self.selectedMemNum != 17:
                    break
                if e.type == QUIT:
                    GlobalData.quitFlag = 1
                    return
                elif e.type == KEYDOWN:
                    if e.key == K_UP:
                        if self.selection == 0:
                            self.selection = 4
                        elif self.selection == 1:
                            self.selection = 0
                        elif self.selection == 2:
                            self.selection = 1
                        elif self.selection == 3:
                            self.selection = 2
                        elif self.selection == 4:
                            self.selection = 3    
                    elif e.key == K_DOWN:
                        if self.selection == 0:
                            self.selection = 1
                        elif self.selection == 1:
                            self.selection = 2
                        elif self.selection == 2:
                            self.selection = 3
                        elif self.selection == 3:
                            self.selection = 4
                        elif self.selection == 4:
                            self.selection = 0                        
                    elif e.key == K_END:
                        return
                    elif e.key == K_RETURN:
                        if self.selection == 0:
                            self.selectMonster("ATTACK")
                            break
                        elif self.selection == 1:
                            self.useShit("WTC")
                            break 
                        elif self.selection == 2:
                            self.useShit("HTC")
                            break
                        elif self.selection == 3:
                            self.useShit("ITEM")
                            break
                        elif self.selection == 4:
                            tmp = [self.selectedMember, "RUN"]
                            self.actions.append(tmp)
                            self.teamNum += 1
                            if self.teamNum == len(self.team.team):
                                self.enemyActions()                                
                                self.teamNum = 0
                                self.executeMoves = True
                            for x in range(4):    
                                self.display.getScreen().blit(self.textureManager.textures["bg"][0], (0,0))
                                self.display.getScreen().blit(self.textureManager.textures[self.selectedMember.currentSkin][0], (504 - (3-x)*6,96), self.textureManager.spriteRects[self.selectedMember.currentSkin][16-x])    
                                self.drawStats()   
                                self.displayMonsters()
                                self.battleBox.show()
                                self.battleMenu.show()
                                pygame.time.delay(75)
                                self.flipScreenBuffer()
                            self.selectedMemNum = 13
                       
                                                                                              
              




    def performActions(self):
        while(len(self.actions)>0):
            print len(self.actions)
            self.highestSPD = 0
            self.highestAction = None
            for x in self.actions:
                if x[0].attributes.stats[7] > self.highestSPD:
                    self.highestSPD = x[0].attributes.stats[7]
                    self.highestAction = x   
            if self.highestAction[1] == "ATTACK":
                self.attackTarget(self.highestAction[0], self.highestAction[2])
            if self.highestAction[1] == "WTC":
                self.WTCTarget(self.highestAction[0], self.highestAction[2], self.highestAction[3])
            if self.highestAction[1] == "HTC":
                self.HTCTarget(self.highestAction[0], self.highestAction[2], self.highestAction[3])
            if self.highestAction[1] == "ITEM":
                self.itemTarget(self.highestAction[0], self.highestAction[2], self.highestAction[3])
            if self.highestAction[1] == "RUN":
                self.run(self.highestAction[0])
            if self.battleBool == False:
                break        
            self.actions.remove(self.highestAction)
            self.display.getScreen().blit(self.textureManager.textures["bg"][0], (0,0))
            for x in self.team.team:
                if float(x.attributes.stats[0])*.8 <= x.HP:
                    if x.currentSkin.count('-') == 0:
                        x.currentSkin = x.currentSkin
                    else:
                        x.currentSkin = x.currentSkin[:-2]
                elif float(x.attributes.stats[0])*.6 <= x.HP:
                    if x.currentSkin.count('-') == 0:
                        x.currentSkin = x.currentSkin + "-80"
                    else:
                        x.currentSkin = x.currentSkin[:-2] + "80"
                elif float(x.attributes.stats[0])*.4 <= x.HP:
                    if x.currentSkin.count('-') == 0:
                        x.currentSkin = x.currentSkin + "-60"
                    else:
                        x.currentSkin = x.currentSkin[:-2] + "60" 
                elif float(x.attributes.stats[0])*.2 <= x.HP:
                    if x.currentSkin.count('-') == 0:
                        x.currentSkin = x.currentSkin + "-40"
                    else:
                        x.currentSkin = x.currentSkin[:-2] + "40"
                elif 0 <= x.HP:
                    if x.currentSkin.count('-') == 0:
                        x.currentSkin = x.currentSkin + "-20"
                    else:
                        x.currentSkin = x.currentSkin[:-2] + "20"                                     
            self.height = 0                    
            for x in self.team.team:
                self.display.getScreen().blit(self.textureManager.textures[x.currentSkin][0], (504,96+self.height*32), self.textureManager.spriteRects[x.currentSkin][13])
                self.height += 1    
            self.drawStats()
            self.printMonArray()
            for y in range(len(self.monArray)):
                for x in range(len(self.monArray[y])):
                    if self.monArray[y][x] is not None:                   
                        if self.monArray[y][x].HP <= 0:
                            self.battleBox.addText(self.monArray[y][x].name + " was defeated.")
                            self.monArray[y][x] = None
                            self.arrayPrinted = False     
             
            self.found = False               
            for y in self.monArray:
                for x in y:
                    if x is not None:
                        self.found = True                                
                        break
                if self.found:  
                    break
            if not self.found:
                self.printMonArray()
                self.battleBox.addText("Battle won!")
                self.open = True
                while self.open:      
                    for e in pygame.event.get():
                        if e.type == QUIT:
                            GlobalData.quitFlag = 1
                            return 
                        elif e.type == KEYDOWN:
                            if e.key == K_RETURN:
                                self.open = False
                #Won battle
                self.ret = []
                for x in self.team.team:
                    self.ret.append(x.currentSkin)                    
                return self.ret

            for x in self.team.team:
                if x.HP <= 0:
                    x.alive = False
            for x in range(len(self.team.team)):
                if self.team.team[x].alive:
                    break
                elif x is len(self.team.team)-1:
                    self.displayMonsters()
                    self.battleBox.addText("Game Over...")
                    GlobalData.quitFlag = 1
                    self.open = True
                    while self.open:      
                        for e in pygame.event.get():
                            if e.type == QUIT:
                                GlobalData.quitFlag = 1
                                return
                            elif e.type == KEYDOWN:
                                if e.key == K_RETURN:
                                    self.open = False
                                    return    
            self.displayMonsters()
            self.battleBox.show()
            self.battleMenu.show()
            self.flipScreenBuffer()
            self.open = True
            while self.open:      
                for e in pygame.event.get():
                    if e.type == QUIT:
                        GlobalData.quitFlag = 1
                        return
                    elif e.type == KEYDOWN:
                        if e.key == K_RETURN:
                            self.open = False
                            break
                pygame.time.delay(300)
                self.open = False
        for y in range(len(self.monArray)):
            for x in range(len(self.monArray[y])):
                if self.monArray[y][x] is not None:                   
                    if self.monArray[y][x].HP <= 0:
                        self.battleBox.addText(self.monArray[y][x].name + " was defeated.")
                        self.monArray[y][x] = None
                        self.arrayPrinted = False     
         
        self.found = False               
        for y in self.monArray:
            for x in y:
                if x is not None:
                    self.found = True                                
                    break
            if self.found:  
                break
        if not self.found:
            self.printMonArray()
            self.battleBox.addText("Battle won!")
            self.open = True
            while self.open:      
                for e in pygame.event.get():
                    if e.type == QUIT:
                        GlobalData.quitFlag = 1
                        return 
                    elif e.type == KEYDOWN:
                        if e.key == K_RETURN:
                            self.open = False
            #Won battle
            self.ret = []
            for x in self.team.team:
                self.ret.append(x.currentSkin)                    
            return self.ret

        for x in self.team.team:
            if x.HP <= 0:
                x.alive = False
        for x in range(len(self.team.team)):
            if self.team.team[x].alive:
                break
            elif x is len(self.team.team)-1:
                self.displayMonsters()
                self.battleBox.addText("Game Over...")
                GlobalData.quitFlag = 1
                self.open = True
                while self.open:      
                    for e in pygame.event.get():
                        if e.type == QUIT:
                            GlobalData.quitFlag = 1
                            return
                        elif e.type == KEYDOWN:
                            if e.key == K_RETURN:
                                self.open = False
                                return    
                             


    def drawStats(self):
        pygame.font.init()
        self.font = pygame.font.Font(None, 24)
        self.display.getScreen().blit(self.font.render(str(Attributes.attributeNames), 0, (255,255,255)), (24,24))
        self.display.getScreen().blit(self.font.render(str(self.team.team[0].attributes.stats), 0, (255,255,255)), (24,48))
        self.display.getScreen().blit(self.font.render("HP:" + str(self.team.team[0].HP), 0, (255,255,255)), (24,72))    

    def enemyActions(self):
        #print "Enemy monsters"
        for y in self.monArray:
            for x in y:
                if x is not None:
                    #print x.name
                    self.WTCList = []
                    self.HTCList = []
                    self.itemList = []
                    self.num = 0
                    self.itemTrue = False
                    self.WTCTrue = False  
                    for z in x.shit:
                        for y in z.types:
                            if y.strip() == "WTC":
                                self.WTCList.append(z.name)
                        for y in z.types:
                            if y.strip() == "HTC":
                                self.HTCList.append(z.name)
                        for y in z.types:
                            if y.strip() == "ITEM":
                                self.itemList.append(z.name)
                    if x.HP <= float(GlobalData.statsData[x.name][0])*.3:
                        if len(self.HTCList) > 0:
                            self.rand = random.randint(0, len(self.HTCList)-1)
                            tmp = [x, "HTC", self.HTCList[rand], x] 
                            self.actions.append(tmp)
                            continue            
                    if len(self.WTCList) > 0:
                        self.randWTC = random.randin(0,len(self.WTCList)-1)
                        self.num += 1
                        self.WTCTrue = True
                    if len(self.itemList) > 0:
                        self.randItem = random.randint(0,len(self.itemList)-1)
                        self.num += 1
                        self.itemTrue = True
                    self.act = random.randint(0,self.num)
                    self.actedOn = random.choice(self.team.team)
                    
                    if self.act == 0:
                        tmp = [x, "ATTACK", self.actedOn]
                        self.actions.append(tmp)
                    elif self.act == 1 and self.WTCTrue:
                        tmp = [x, "WTC", self.randWTC, self.actedOn]
                        self.actions.append(tmp)
                    elif self.act == 1 and self.itemTrue:
                        tmp = [x, "ITEM", self.randItem, x]
                        self.actions.append(tmp)    
                    elif self.act == 2:
                        tmp = [x, "ITEM", self.randItem, x]
                        self.actions.append(tmp)                                                 

    def run(self, actor):
        self.topMonSpeed = 0
        for y in self.monArray:
            for x in y:
                if x is not None:
                    if x.attributes.stats[7] > self.topMonSpeed:
                        self.topMonSpeed = x.attributes.stats[7]

        self.runMod = int(actor.attributes.stats[7]) - int(self.topMonSpeed)
        #print self.runMod                    
        if self.runMod <= 0:
            #cant run
            self.battleBox.addText("Can't run away!")
            #self.battleBox.draw()
            #print "Can't run away!"
        else:
            self.draw  = random.randint(1,25)
            if self.draw <= self.runMod:
                #success
                self.battleBox.addText("Got away!")
                #self.battleBox.draw()
                #print "Ran Away"
                self.battleBool = False
                self.open = True
                while self.open:      
                    for e in pygame.event.get():
                        if e.type == QUIT:
                            GlobalData.quitFlag = 1
                            return
                        elif e.type == KEYDOWN:
                            if e.key == K_RETURN:
                                self.open = False
                self.ret = []
                for x in self.team.team:
                    self.ret.append(x.currentSkin)                    
                return self.ret
            else:
                #couldnt run
                self.battleBox.addText("Couldn't get away!")
                #self.battleBox.draw()
                #print "Could not run"        

                        
                  
    def itemTarget(self, actor, item, actee):
        
        #if self.arrayNum > len(self.monArray) - 1:
        #    self.battleBox.addText("No Target!")
        #    self.battleBox.draw()
        #    self.noChange = True
        #    return                                
        self.accMod = int(actor.attributes.stats[4]) + int(GlobalData.itemData[item][6]) - int(actee.attributes.stats[6])
        #print self.accMod
        if self.team.shit[item].USE != "NA":
            self.team.shit[item].USE -= 1
            if self.team.shit[item].USE == 0:
                self.team.removeShit(item)
        self.draw = random.randint(0, 100)
        if self.draw > self.accMod:
            self.battleBox.addText(actor.name + " missed " + actee.name + "!")    
            return
        else:
            self.itemMod = int(actor.attributes.stats[2]) + int(GlobalData.itemData[item][4])
            if self.itemMod > 0: 
                actee.HP -= self.itemMod
                self.battleBox.addText(actor.name + " used " + item + " on " + actee.name + "!")
                return
            else:
                self.battleBox.addText(actor.name + "'s " + item + " has no effect on " + actee.name + "!") 
                return
                
                
                
    def selectMonster(self, action, item = None):                     
        self.selectionBool = True
        self.next = 0
        while self.monArray[self.selectedMonster[0]][self.selectedMonster[1]] is None:
            self.selectedMonster = (self.next%3, self.next/3)
            self.next += 1
        while self.selectionBool:
            #self.selectedMonster = (self.selectedMonster[0]%3, self.selectedMonster[1]%3)
            self.display.getScreen().blit(self.textureManager.textures["bg"][0], (0,0))
            self.drawStats()
            self.displayMonsters()  
            self.display.getScreen().blit(self.textureManager.textures[self.selectedMember.currentSkin][0], (504 - 4*6,96), self.textureManager.spriteRects[self.selectedMember.currentSkin][13])    
            self.battleMenu.show()
            self.battleBox.show()
            if self.selectedMonster == (0,0):
                self.display.getScreen().blit(self.textureManager.textures["battle"][0], (128, 96), self.textureManager.spriteRects["battle"][1])                 
            elif self.selectedMonster == (0,1):
                self.display.getScreen().blit(self.textureManager.textures["battle"][0], (128, 144 + 24), self.textureManager.spriteRects["battle"][1])              
            elif self.selectedMonster == (0,2):
                self.display.getScreen().blit(self.textureManager.textures["battle"][0], (128, 196 + 48), self.textureManager.spriteRects["battle"][1])                 
            elif self.selectedMonster == (1,0):
                self.display.getScreen().blit(self.textureManager.textures["battle"][0], (214, 96), self.textureManager.spriteRects["battle"][1])              
            elif self.selectedMonster == (1,1):
                self.display.getScreen().blit(self.textureManager.textures["battle"][0], (214, 144 + 24), self.textureManager.spriteRects["battle"][1])
            elif self.selectedMonster == (1,2):
                self.display.getScreen().blit(self.textureManager.textures["battle"][0], (214, 196 + 48), self.textureManager.spriteRects["battle"][1])
            elif self.selectedMonster == (2,0):
                self.display.getScreen().blit(self.textureManager.textures["battle"][0], (316, 96), self.textureManager.spriteRects["battle"][1])
            elif self.selectedMonster == (2,1):
                self.display.getScreen().blit(self.textureManager.textures["battle"][0], (316, 144 + 24), self.textureManager.spriteRects["battle"][1])
            elif self.selectedMonster == (2,2):
                self.display.getScreen().blit(self.textureManager.textures["battle"][0], (316, 196 + 48), self.textureManager.spriteRects["battle"][1])                 
            self.flipScreenBuffer()                  
            for e in pygame.event.get():
                #self.noChange = False        #this appears useless...
                if e.type == QUIT:
                    GlobalData.quitFlag = 1
                    return    
                elif e.type == KEYDOWN:
                    if e.key == K_UP:
                        if self.monArray[(self.selectedMonster[0])%3][(self.selectedMonster[1] - 1)%3] is not None:
                            self.selectedMonster = ((self.selectedMonster[0])%3, (self.selectedMonster[1] - 1)%3)
                        elif self.monArray[(self.selectedMonster[0])%3][(self.selectedMonster[1] - 2)%3] is not None:
                            self.selectedMonster = ((self.selectedMonster[0])%3, (self.selectedMonster[1] - 2)%3)
                        elif self.monArray[(self.selectedMonster[0] + 1)%3][(self.selectedMonster[1] - 1)%3] is not None:
                            self.selectedMonster = ((self.selectedMonster[0] + 1)%3, (self.selectedMonster[1] - 1)%3)
                        elif self.monArray[(self.selectedMonster[0] + 2)%3][(self.selectedMonster[1] - 2)%3] is not None:
                            self.selectedMonster = ((self.selectedMonster[0] + 2)%3, (self.selectedMonster[1] - 2)%3)
                        elif self.monArray[(self.selectedMonster[0] - 1)%3][(self.selectedMonster[1] - 1)%3] is not None:
                            self.selectedMonster = ((self.selectedMonster[0] - 1)%3, (self.selectedMonster[1] - 1)%3)
                        elif self.monArray[(self.selectedMonster[0] - 1)%3][(self.selectedMonster[1] - 2)%3] is not None:
                            self.selectedMonster = ((self.selectedMonster[0] - 1)%3, (self.selectedMonster[1] - 2)%3)
                        elif self.monArray[(self.selectedMonster[0] - 2)%3][(self.selectedMonster[1] - 1)%3] is not None:
                            self.selectedMonster = ((self.selectedMonster[0] - 2)%3, (self.selectedMonster[1] - 1)%3) 
                        elif self.monArray[(self.selectedMonster[0] - 2)%3][(self.selectedMonster[1] - 2)%3] is not None:
                            self.selectedMonster = ((self.selectedMonster[0] - 2)%3, (self.selectedMonster[1] - 2)%3) 
                               
                            
                    elif e.key == K_DOWN:
                        if self.monArray[(self.selectedMonster[0])%3][(self.selectedMonster[1] + 1)%3] is not None:
                            self.selectedMonster = ((self.selectedMonster[0])%3, (self.selectedMonster[1] + 1)%3)
                        elif self.monArray[(self.selectedMonster[0])%3][(self.selectedMonster[1] + 2)%3] is not None:
                            self.selectedMonster = ((self.selectedMonster[0])%3, (self.selectedMonster[1] + 2)%3)
                        elif self.monArray[(self.selectedMonster[0] + 1)%3][(self.selectedMonster[1] + 1)%3] is not None:
                            self.selectedMonster = ((self.selectedMonster[0] + 1)%3, (self.selectedMonster[1] + 1)%3)
                        elif self.monArray[(self.selectedMonster[0] + 2)%3][(self.selectedMonster[1] + 2)%3] is not None:
                            self.selectedMonster = ((self.selectedMonster[0] + 2)%3, (self.selectedMonster[1] + 2)%3)
                        elif self.monArray[(self.selectedMonster[0] - 1)%3][(self.selectedMonster[1] + 1)%3] is not None:
                            self.selectedMonster = ((self.selectedMonster[0] - 1)%3, (self.selectedMonster[1] + 1)%3)
                        elif self.monArray[(self.selectedMonster[0] - 1)%3][(self.selectedMonster[1] + 2)%3] is not None:
                            self.selectedMonster = ((self.selectedMonster[0] - 1)%3, (self.selectedMonster[1] + 2)%3)
                        elif self.monArray[(self.selectedMonster[0] - 2)%3][(self.selectedMonster[1] + 1)%3] is not None:
                            self.selectedMonster = ((self.selectedMonster[0] - 2)%3, (self.selectedMonster[1] + 1)%3)
                        elif self.monArray[(self.selectedMonster[0] - 2)%3][(self.selectedMonster[1] + 2)%3] is not None:
                            self.selectedMonster = ((self.selectedMonster[0] - 2)%3, (self.selectedMonster[1] + 2)%3)
                               
                            
                    elif e.key == K_RIGHT:
                        if self.monArray[(self.selectedMonster[0] + 1)%3][(self.selectedMonster[1])%3] is not None:
                            self.selectedMonster = ((self.selectedMonster[0] + 1)%3, (self.selectedMonster[1])%3)
                        elif self.monArray[(self.selectedMonster[0] + 2)%3][(self.selectedMonster[1])%3] is not None:
                            self.selectedMonster = ((self.selectedMonster[0] + 2)%3, (self.selectedMonster[1])%3)
                        elif self.monArray[(self.selectedMonster[0] + 1)%3][(self.selectedMonster[1] - 1)%3] is not None:
                            self.selectedMonster = ((self.selectedMonster[0] + 1)%3, (self.selectedMonster[1] - 1)%3)
                        elif self.monArray[(self.selectedMonster[0] + 2)%3][(self.selectedMonster[1] - 2)%3] is not None:
                            self.selectedMonster = ((self.selectedMonster[0] + 2)%3, (self.selectedMonster[1] - 2)%3)
                        elif self.monArray[(self.selectedMonster[0] + 1)%3][(self.selectedMonster[1] + 1)%3] is not None:
                            self.selectedMonster = ((self.selectedMonster[0] + 1)%3, (self.selectedMonster[1] + 1)%3)
                        elif self.monArray[(self.selectedMonster[0] + 1)%3][(self.selectedMonster[1] + 2)%3] is not None:
                            self.selectedMonster = ((self.selectedMonster[0] + 1)%3, (self.selectedMonster[1] + 2)%3)
                        elif self.monArray[(self.selectedMonster[0] + 2)%3][(self.selectedMonster[1] + 1)%3] is not None:
                            self.selectedMonster = ((self.selectedMonster[0] + 2)%3, (self.selectedMonster[1] + 1)%3)
                        elif self.monArray[(self.selectedMonster[0] + 2)%3][(self.selectedMonster[1] + 2)%3] is not None:
                            self.selectedMonster = ((self.selectedMonster[0] + 2)%3, (self.selectedMonster[1] + 2)%3) 
                                 
                            
                    elif e.key == K_LEFT:
                        if self.monArray[(self.selectedMonster[0] - 1)%3][(self.selectedMonster[1])%3] is not None:
                            self.selectedMonster = ((self.selectedMonster[0] - 1)%3, (self.selectedMonster[1])%3) 
                        elif self.monArray[(self.selectedMonster[0] - 2)%3][(self.selectedMonster[1])%3] is not None:
                            self.selectedMonster = ((self.selectedMonster[0] - 2)%3, (self.selectedMonster[1])%3) 
                        elif self.monArray[(self.selectedMonster[0] - 1)%3][(self.selectedMonster[1] - 1)%3] is not None:
                            self.selectedMonster = ((self.selectedMonster[0] - 1)%3, (self.selectedMonster[1] - 1)%3) 
                        elif self.monArray[(self.selectedMonster[0] - 2)%3][(self.selectedMonster[1] - 2)%3] is not None:
                            self.selectedMonster = ((self.selectedMonster[0] - 2)%3, (self.selectedMonster[1] - 2)%3) 
                        elif self.monArray[(self.selectedMonster[0] - 1)%3][(self.selectedMonster[1] + 1)%3] is not None:
                            self.selectedMonster = ((self.selectedMonster[0] - 1)%3, (self.selectedMonster[1] + 1)%3) 
                        elif self.monArray[(self.selectedMonster[0] - 1)%3][(self.selectedMonster[1] + 2)%3] is not None:
                            self.selectedMonster = ((self.selectedMonster[0] - 1)%3, (self.selectedMonster[1] + 2)%3) 
                        elif self.monArray[(self.selectedMonster[0] - 2)%3][(self.selectedMonster[1] + 1)%3] is not None:
                            self.selectedMonster = ((self.selectedMonster[0] - 2)%3, (self.selectedMonster[1] + 1)%3)
                        elif self.monArray[(self.selectedMonster[0] - 2)%3][(self.selectedMonster[1] + 2)%3] is not None:
                            self.selectedMonster = ((self.selectedMonster[0] - 2)%3, (self.selectedMonster[1] + 2)%3)
                                      
                            
                    elif e.key == K_END:
                        self.selectionBool = False
                        break

                    elif e.key == K_RETURN:    
                        #if self.noChange == True:  #this appears useless...
                        #    continue
                        if item is None:
                            tmp = [self.selectedMember, action, self.monArray[self.selectedMonster[0]][self.selectedMonster[1]]]    #for attack only
                        else:
                            tmp = [self.selectedMember, action, item, self.monArray[self.selectedMonster[0]][self.selectedMonster[1]]]
                            self.bool = False    
                        
                        self.actions.append(tmp)
                        self.teamNum += 1
                        if self.teamNum == len(self.team.team):
                            self.enemyActions()                                
                            self.teamNum = 0
                            self.executeMoves = True
                            
                            
                        for x in range(4):    
                            self.display.getScreen().blit(self.textureManager.textures["bg"][0], (0,0))
                            self.display.getScreen().blit(self.textureManager.textures[self.selectedMember.currentSkin][0], (504 - (3-x)*6,96), self.textureManager.spriteRects[self.selectedMember.currentSkin][16-x])    
                            self.drawStats()   
                            self.displayMonsters()
                            self.battleBox.show()
                            self.battleMenu.show()
                            pygame.time.delay(75)
                            self.flipScreenBuffer()
                            
                        self.selectedMemNum = 13                        
                        self.selectionBool = False
                        break

                    
                    
              

    def useShit(self, shitType):
        self.bool = True
        self.shitMenu = None
        self.list = None
        if shitType is "WTC":
            if len(self.team.WTCList) == 0:
                TextBox.QuickBox(192, 312, "No WTC!              ")
                return
            self.list = self.team.WTCList
                
        elif shitType is "HTC":
            if len(self.team.HTCList) == 0:
                TextBox.QuickBox(192, 312, "No HTC!              ")
                return
            self.list = self.team.HTCList    

        elif shitType is "ITEM":
            if len(self.team.itemList) == 0:
                TextBox.QuickBox(192, 312, "No Items!            ")
                return
            self.list = self.team.itemList          
        
        self.shitMenu = BattleMenu(192, 312, self.list)              
       
        self.selection = 0
        while self.bool:
            self.display.getScreen().blit(self.textureManager.textures["bg"][0], (0,0))
            self.drawStats()
            self.displayMonsters()    
            self.display.getScreen().blit(self.textureManager.textures[self.selectedMember.currentSkin][0], (504 - 4*6,96), self.textureManager.spriteRects[self.selectedMember.currentSkin][13])    
            self.battleMenu.show()
            self.battleBox.show()
            self.shitMenu.show()
            if self.selection == 0:
                self.display.getScreen().blit(self.textureManager.textures["battle"][0], (334, 316), self.textureManager.spriteRects["battle"][1])
            elif self.selection == 1:
                self.display.getScreen().blit(self.textureManager.textures["battle"][0], (334, 316+24), self.textureManager.spriteRects["battle"][1])
            elif self.selection == 2:
                self.display.getScreen().blit(self.textureManager.textures["battle"][0], (334, 316+48), self.textureManager.spriteRects["battle"][1])
            elif self.selection == 3:
                self.display.getScreen().blit(self.textureManager.textures["battle"][0], (334, 316+72), self.textureManager.spriteRects["battle"][1])
            elif self.selection == 4:
                self.display.getScreen().blit(self.textureManager.textures["battle"][0], (334, 316+96), self.textureManager.spriteRects["battle"][1])
            self.flipScreenBuffer()
            for e in pygame.event.get():
                if e.type == QUIT:
                    GlobalData.quitFlag = 1
                    return
                elif e.type == KEYDOWN:
                    if e.key == K_UP:
                        self.selection -=1
                        if self.selection < 0:
                            if len(self.list) <= 5:
                                self.selection = len(self.list) - 1
                            else:
                                self.selection = 0
                                if self.shitMenu.lineOffset > 0:
                                    self.shitMenu.lineOffset -= 1        
                    elif e.key == K_DOWN:
                        self.selection += 1
                        if self.selection > 4:
                             if len(self.list) <= 5:
                                self.selection = 0
                             else:
                                self.selection = 4
                                if self.shitMenu.lineOffset + 5 < len(self.list):
                                    self.shitMenu.lineOffset += 1                    
                    elif e.key == K_END:
                        return
                    elif e.key == K_RETURN:
                        if self.selection == 0:
                            if shitType is not "HTC":
                                self.selectMonster(shitType, self.shitMenu.lines[0])
                                break
                            else:
                                self.selectTeam(self.shitMenu.lines[0])    
                        elif self.selection == 1:
                            if shitType is not "HTC":
                                self.selectMonster(shitType, self.shitMenu.lines[1])
                                break
                            else:
                                self.selectTeam(self.shitMenu.lines[1])        
                        elif self.selection == 2:
                            if shitType is not "HTC":
                                self.selectMonster(shitType, self.shitMenu.lines[2])
                                break
                            else:
                                self.selectTeam(self.shitMenu.lines[2])        
                        elif self.selection == 3:
                            if shitType is not "HTC":
                                self.selectMonster(shitType, self.shitMenu.lines[3])
                                break
                            else:
                                self.selectTeam(self.shitMenu.lines[3])        
                        elif self.selection == 4:
                            if shitType is not "HTC":
                                self.selectMonster(shitType, self.shitMenu.lines[4])
                                break
                            else:
                                self.selectTeam(self.shitMenu.lines[4])                                                                               
                pygame.event.pump()

    def WTCTarget(self, actor, WTC, actee):
        #if self.arrayNum > len(self.monArray) - 1:
        #    self.battleBox.addText("No Target!")
        #    self.battleBox.draw()
        #    self.noChange = True
        #    return                                
        self.accMod = int(actor.attributes.stats[4]) + int(GlobalData.itemData[WTC][6]) - int(actee.attributes.stats[6])
        #print self.accMod
        for x in actor.shit:
            if x.name == WTC:
                actor.shit[actor.shit.index(x)].USE -= 1
                if actor.shit[actor.shit.index(x)].USE == 0:
                    actor.shit.remove(x)    
                break
        self.draw = random.randint(0, 100)
        if self.draw > self.accMod:
            self.battleBox.addText(actor.name + " missed " + actee.name + "!")    
            return
        else:
            self.WTCMod = int(actor.attributes.stats[2]) + int(GlobalData.itemData[WTC][4]) - int(actee.attributes.stats[5])
            if self.WTCMod > 0: 
                actee.HP -= self.WTCMod
                self.battleBox.addText(actor.name + " used " + WTC + " on " + actee.name + "!")
                return
            else:
                self.battleBox.addText(actor.name + "'s " + WTC + " has no effect on " + actee.name + "!") 
                return

    
                  
    def HTCTarget(self, actor, HTC, actee):                             
        self.accMod = int(actor.attributes.stats[4]) + int(GlobalData.itemData[HTC][6])
        #print self.accMod
        for x in actor.shit:
            if x.name == self.HTCChoice:
                actor.shit.remove(x)
                break
        self.draw = random.randint(0, 100)
        if self.draw > self.accMod:
            self.battleBox.addText(actor.name + " missed " + actee.name + "!")    
            return
        else:
            self.HTCMod = int(actor.attributes.stats[1]) + int(GlobalData.itemData[HTC][5])
            if self.HTCMod > 0: 
                actee.HP += self.HTCMod
                if actee.HP > actee.attributes.stats[0]:
                    actee.HP = actee.attributes.stats[0]
                self.battleBox.addText(actor.name + " used " + HTC + " on " + actee.name + "!")
                return
            else:
                self.battleBox.addText(actor.name + "'s " + HTC + " has no effect on " + actee.name + "!") 
                return

    
    def attackTarget(self, actor, actee):
        #if self.arrayNum > len(self.monArray) - 1:
        #    self.battleBox.addText("No Target!")
        #    self.battleBox.draw()
        #    self.noChange = True
        #    return
        #print self.monArray[self.selectionAttack[0]][self.selectionAttack[1]]
        #print actee                                
        self.accMod = int(actor.attributes.stats[4]) - int(actee.attributes.stats[6])
        #print self.accMod
        self.draw = random.randint(0, 100)
        if self.draw > self.accMod:            
            self.battleBox.addText(actor.name + " missed " + actee.name + "!")    
            return
        else:
            self.strMod = int(actor.attributes.stats[3]) - int(actee.attributes.stats[5])
            if self.strMod > 0: 
                actee.HP -= self.strMod
                self.battleBox.addText(actor.name + " hit " + actee.name + "!")
                return
            else:
                self.battleBox.addText(actor.name + "'s attack has no effect on " + actee.name + "!") 
                return


    def displayMonsters(self):
        self.xOff = 0       
        self.yOff = 0
        for y in range(3):
            for x in range(3):
                if self.monArray[x][y] is not None:
                    self.monArray[x][y].display(80 + self.xOff, 96 + self.yOff)
                if self.xOff is not 184:
                    self.xOff += 92                     
                else:
                    self.xOff = 0
                    self.yOff += 72
            

class BattleMenu:
    def __init__(self, x, y, lines):
        self.display = GlobalData.display
        self.textureManager = GlobalData.textureManager
        self.font = pygame.font.Font(None, 24)
        self.x = x
        self.y = y
        self.maxWidth = self.display.getScreenWidth() - 96        
        self.maxLength = self.display.getScreenHeight() - 96
        self.width = 148
        self.height = 48         
        self.lines = lines
        self.lineNum = len(self.lines)-1
        self.lineOffset = 0

    def show(self):
        final_lines = []
        if self.lineNum < 5:
            final_lines = self.lines
        else:
            for x in range(5):
                print x
                final_lines.append(self.lines[x+self.lineOffset])
     
        self.xCount = self.width/24
        if self.width%24 != 0:
            self.xCount += 1
        if len(final_lines) <= 5:    
            self.yCount = len(final_lines)
            if len(final_lines) == 1:
                self.yCount +=1
        else:
            self.yCount = 5        
        for x in range(self.xCount):
            for y in range(self.yCount):
                if x == 0:
                    if y == 0:
                        #print "topleft"
                        self.display.getScreen().blit(self.textureManager.textures["text"][0], (self.x + x*24, self.y + y*24), self.textureManager.spriteRects["text"][1])              
                    elif y == self.yCount-1:
                        #print "botleft"
                        self.display.getScreen().blit(self.textureManager.textures["text"][0], (self.x + x*24, self.y + y*24), self.textureManager.spriteRects["text"][7])
                    else:
                        #print "midleft"
                        self.display.getScreen().blit(self.textureManager.textures["text"][0], (self.x + x*24, self.y + y*24), self.textureManager.spriteRects["text"][4])
                elif x == self.xCount - 1 :
                    if y == 0:
                        #print "topright"
                        self.display.getScreen().blit(self.textureManager.textures["text"][0], (self.x + x*24, self.y + y*24), self.textureManager.spriteRects["text"][3])              
                    elif y == self.yCount-1:
                        #print "botright"
                        self.display.getScreen().blit(self.textureManager.textures["text"][0], (self.x + x*24, self.y + y*24), self.textureManager.spriteRects["text"][9])
                    else:
                        #print "midright"
                        self.display.getScreen().blit(self.textureManager.textures["text"][0], (self.x + x*24, self.y + y*24), self.textureManager.spriteRects["text"][6])
                else:
                    if y == 0:
                        #print "topmid"
                        self.display.getScreen().blit(self.textureManager.textures["text"][0], (self.x + x*24, self.y + y*24), self.textureManager.spriteRects["text"][2])              
                    elif y == self.yCount-1:
                        #print "botmid"
                        self.display.getScreen().blit(self.textureManager.textures["text"][0], (self.x + x*24, self.y + y*24), self.textureManager.spriteRects["text"][8])
                    else:
                        #print "center"
                        self.display.getScreen().blit(self.textureManager.textures["text"][0], (self.x + x*24, self.y + y*24), self.textureManager.spriteRects["text"][5])
                      
        self.yPlus = 0
        for x in final_lines:            
            self.display.getScreen().blit(self.font.render(x, 0, (255,255,255)), (self.x + 6, self.y + self.yPlus + 4))
            self.yPlus += 24     
    



class BattleBox:
    def __init__(self, text = ""):
        self.display = GlobalData.display
        self.textureManager = GlobalData.textureManager
        self.font = pygame.font.Font(None, 24)
        self.x = 24
        self.y = 312
        self.maxWidth = 312 - 96        
        self.maxLength = 312 - 96
        self.width = 312
        self.height = 312-96      
        self.text = text
        self.lines = []
        self.lineNum = 0
        
    def draw(self):
        final_lines = []
        requested_lines = self.text
        if self.font.size(requested_lines)> self.width - 24:
            words = requested_lines.split(' ')
            accumulated_line = ""
            for word in words:
                test_line = accumulated_line + word + " "
                # Build the line while the words fit.    
                if self.font.size(test_line)[0] < self.width - 24:
                    accumulated_line = test_line 
                else: 
                    final_lines.append(accumulated_line) 
                    accumulated_line = word + " "
            final_lines.append(accumulated_line)
            self.linesLength = len(final_lines)
            for x in final_lines:
                if self.lineNum < 5:
                    self.lines.append(x)
                    self.lineNum += 1
                else:
                    for y in range(len(self.lines)-1):
                        self.lines[y] = self.lines[y+1]
                    self.lines[4] = x
        else: 
            if self.lineNum < 5:
                self.lines.append(requested_lines)
                self.lineNum += 1
            else:
                for x in range(len(self.lines)-1):
                    self.lines[x] = self.lines[x+1]
                self.lines[4] = requested_lines  

    def show(self):
        self.xCount = 14
        self.yCount = 5
        for x in range(self.xCount):
            for y in range(self.yCount):
                if x == 0:
                    if y == 0:
                        self.display.getScreen().blit(self.textureManager.textures["text"][0], (self.x + x*24, self.y + y*24), self.textureManager.spriteRects["text"][1])              
                    elif y == self.yCount-1:
                        self.display.getScreen().blit(self.textureManager.textures["text"][0], (self.x + x*24, self.y + y*24), self.textureManager.spriteRects["text"][7])
                    else:
                        self.display.getScreen().blit(self.textureManager.textures["text"][0], (self.x + x*24, self.y + y*24), self.textureManager.spriteRects["text"][4])
                elif x == self.xCount - 1 :
                    if y == 0:
                        self.display.getScreen().blit(self.textureManager.textures["text"][0], (self.x + x*24, self.y + y*24), self.textureManager.spriteRects["text"][3])              
                    elif y == self.yCount-1:
                        self.display.getScreen().blit(self.textureManager.textures["text"][0], (self.x + x*24, self.y + y*24), self.textureManager.spriteRects["text"][9])
                    else:
                        self.display.getScreen().blit(self.textureManager.textures["text"][0], (self.x + x*24, self.y + y*24), self.textureManager.spriteRects["text"][6])
                else:
                    if y == 0:
                        self.display.getScreen().blit(self.textureManager.textures["text"][0], (self.x + x*24, self.y + y*24), self.textureManager.spriteRects["text"][2])              
                    elif y == self.yCount-1:
                        self.display.getScreen().blit(self.textureManager.textures["text"][0], (self.x + x*24, self.y + y*24), self.textureManager.spriteRects["text"][8])
                    else:
                        self.display.getScreen().blit(self.textureManager.textures["text"][0], (self.x + x*24, self.y + y*24), self.textureManager.spriteRects["text"][5])                  
        self.yPlus = 0
        for x in self.lines:            
            self.display.getScreen().blit(self.font.render(x, 0, (255,255,255)), (self.x + 6, self.y + self.yPlus + 4))
            self.yPlus += 24        
        #pygame.display.flip()
    
        
    def addText(self, text):       
        self.text = text
        self.open = True
        self.draw()
        self.show()
        pygame.display.flip()

