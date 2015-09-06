#run batch file or
#in python interpreter, run
#   execfile('W:/Education/2015 Interns/RHKQ/simulation.py')

from operator import add, mul, div
from collections import defaultdict
from copy import deepcopy, copy
from timeit import default_timer
from random import randrange, sample
from csv import reader, writer
from numpy.random import binomial
from os import path

path = path.dirname(path.abspath(__file__))

class Player:
    def __init__(self, row):
        self.name = row[0]
        self.pos = row[2].split('/')
        
        self.g = float(row[3])
        self.stats = map(float, row[4:9])
        self.pa = float(row[9])
        self.ob = self.stats[4]*self.pa
        self.randOB = 0
        
        self.randStats = copy(self.stats)
        self.valuation = 0
        self.appearances = 0
        self.value = 20

    def updateValuation(self, rank):
        self.valuation += rank
        self.appearances += 1
    
    def randomizeStats(self):
        self.randOB = binomial(self.pa, self.stats[4])
        self.randStats[4] = self.randOB/self.pa #get rand OBP
        self.randStats[0] = self.randOB/self.ob * self.stats[0] # get rand R
        self.randStats[1] = self.randOB/self.ob * self.stats[1] # get rand HR
        self.randStats[2] = self.randOB/self.ob * self.stats[2] # get rand RBI
        self.randStats[3] = self.randOB/self.ob * self.stats[3] # get rand SB

    def finalizeValuation(self):
        if self.appearances > 0:
            self.value = self.valuation/self.appearances
        else:
            self.value = self.value*0.8
        self.valuation = 0
        self.appearances = 0
    
    def __str__(self):
        return self.name + " " + str(self.pos) + " " + str(self.value)

class Team:
    def __init__(self):
        self.players = []
        self.stats = [0, 0, 0, 0, 0]
        self.ob = 0
        self.pa = 0
        self.ranks = [0, 0, 0, 0, 0]
        self.salary = 0
        self.salaryCap = 180

    def addPlayer(self, player):
        self.players.append(player)

    def compileStats(self):
        for player in self.players:
            player.randomizeStats()
            self.stats = map(add, self.stats, player.randStats)
            self.ob += player.randOB
            self.pa += player.pa
        self.stats[4] = self.ob/self.pa

    def updateValuations(self):
        obpContr = self.pa/self.ob * sum([p.randOB/p.pa for p in self.players])
        for player in self.players:
            rank = sum(map(mul, map(div, player.randStats, self.stats), self.ranks))
            rank -= player.randStats[4]/self.stats[4]*self.ranks[4] #subtract out incorrect obp calc
            rank += ((player.randOB/self.ob)/(player.pa/self.pa))/obpContr #add correct obp calc
            player.updateValuation(rank)

    def printTeam(self):
        for player in self.players:
                print "\tPlayer: " + player.name + "," + str(player.pos) + "," + str(player.stats)

class League:
    def __init__(self, numTeams):
        self.teams = []
        self.numTeams = numTeams

    def generateTeams(self, universe):
        posIndex = deepcopy(universe.posIndex)
    
        '''for teamNum in range(self.numTeams):
            team = Team()          
            
            for pos in universe.selectPos:
                if posIndex[pos]:
                    i = randrange(len(posIndex[pos]))
                    index = posIndex[pos][i]
                    player = universe.players[index]
                    for p in (player.pos + ['All']):
                        posIndex[p].remove(index)
                    team.addPlayer(player)
                else:
                    return -1

            self.teams.append(team)
            '''

        for teamNum in range(self.numTeams):
            team = Team()          

            for pos in sample(universe.selectPos, len(universe.selectPos)):
                indices = deepcopy(posIndex[pos])
                if posIndex[pos]:
                    while True:
                        i = randrange(len(indices))
                        index = indices[i]
                        player = universe.players[index]
                        if player.value <= (team.salaryCap - team.salary - (9- len(team.players) - 1)):
                            for p in (player.pos + ['All']):
                                '''print str(index) + " " + p + " " + pos + " " + str(i)
                                print player
                                print indices
                                print posIndex'''
                                posIndex[p].remove(index)
                            team.addPlayer(player)
                            break
                        else:
                            '''print index
                            print posIndex[pos]'''
                            indices.remove(index)
                        
                        if len(indices) == 0:
                            return -1
                else:
                    return -1

            self.teams.append(team)
            
    def rankTeams(self):
        for team in self.teams:
            team.compileStats()
            
        for stat in range(5):
            tmp = [team.stats[stat] for team in self.teams]
            indices = list(range(len(tmp)))
            indices.sort(key=lambda x: tmp[x])
            for i, x in enumerate(indices):
                self.teams[x].ranks[stat] = i+1
                
        map(lambda x: x.updateValuations(), self.teams)

class PlayerUniverse:
    def __init__(self):
        self.players = []
        
        self.positions = ['1B','2B','SS','3B','OF','C','All']
        self.minNum = dict(zip(self.positions, [11, 11, 11, 11, 22, 11, 100]))        
        self.selectPos = ['C','SS','2B','3B','1B','OF','OF','All','All']
        
        self.posIndex = defaultdict(list)
    
    def populateUniverse(self):
        with open(path + '/Raw Data.csv', 'rb') as csvfile:
            r = reader(csvfile)
            r.next()
            
            for row in r:
                player = Player(row)
                self.players.append(player)
    
    def constructUniverse(self):
        for pos in self.positions:
            for i, j in enumerate(self.players):
                if pos in j.pos or pos is 'All':
                    self.posIndex[pos].append(i)
    
    def removeWorst(self):
        tmp = [p.value for p in self.players]
        indices = self.posIndex['All']
        indices.sort(key=lambda x: tmp[x])
        
        for index in indices:
            player = self.players[index]
            valid = True
            
            for pos in (player.pos + ['All']):
                if len(self.posIndex[pos]) <= self.minNum[pos]:
                    valid = False
                    break
                    
            if valid:
                for pos in (player.pos + ['All']):
                    self.posIndex[pos].remove(index)
                
                #print index
                print "Removing: " + str(self.players[index])
                print str(len(self.posIndex['All'])) + " players remaining.\n"
                
                player.value = 0

                return True
                
        return False            

class Simulation:
    def __init__(self, numLeagues, leagueSize):
        self.numLeagues = numLeagues
        self.leagueSize = leagueSize
        
        self.universe = PlayerUniverse()
        self.universe.populateUniverse()
        self.universe.constructUniverse()
        
        self.results = []
        
    def run(self, iterate):
        while True:
            leaguesFormed = 0
            while leaguesFormed < self.numLeagues:
                league = League(self.leagueSize)
                if league.generateTeams(self.universe) is -1:
                    #print "Continue"
                    continue
                leaguesFormed = leaguesFormed + 1
                league.rankTeams()
                #print [p.valuation for p in self.universe.players]
                if leaguesFormed % 10 is 0:
                    print leaguesFormed
                    
            map(Player.finalizeValuation, self.universe.players)
            self.getResults()
            if iterate:
                if self.universe.removeWorst() is False:
                    break
            else:
                break
    
    def getResults(self):
        validVals = [self.universe.players[i].value for i in self.universe.posIndex['All']]
        minVal = min(validVals)
        sumVal = sum(validVals)

        factor = (20*len(self.universe.posIndex['All'])-len(validVals))/(sumVal-minVal*len(validVals))
        
        for p in self.universe.players:
            p.value = (p.value-minVal)*factor + 1
            p.value = p.value if p.value > 0 else 0
        
        self.results.append([p.value for p in self.universe.players])
    
    def writeResults(self):
        with open(path + '/simResults.csv', 'wb') as csvfile:
            w = writer(csvfile)
            
            for i in range(len(self.results[0])):
                w.writerow([x[i] for x in self.results])
            #for p in self.universe.players:
            #    w.writerow([p.value])
            
def main():
    start = default_timer()

    sim = Simulation(200, 10)
    sim.run(True)
    sim.writeResults()

    stop = default_timer()
    print "\nTime Elapsed: " + str(stop - start) + " seconds"
    
main()