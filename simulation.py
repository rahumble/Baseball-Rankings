#run batch file or
#in python interpreter, run
#   execfile('W:/Education/2015 Interns/RHKQ/simulation.py')

from operator import add, mul, div
from collections import defaultdict
from copy import deepcopy, copy
from timeit import default_timer
from random import randrange
from csv import reader, writer
from numpy.random import binomial

class Player:
    def __init__(self, row):
        self.name = row[0]
        self.pos = row[2].split('/')
        
        self.g = float(row[3])
        self.stats = map(float, row[4:9])
        self.pa = float(row[9])
        self.ob = self.stats[4]*self.pa
        
        self.randStats = copy(self.stats)
        self.valuation = 0
        self.appearances = 0

    def updateValuation(self, rank):
        self.valuation += rank
        self.appearances += 1
    
    def randStats(self):
        randOB = binomial(self.pa, self.stats[4])
        self.randStats[4] = randOB/self.pa #get rand OBP
        self.randStats[0] = randOB/self.ob * self.stats[0] # get rand R
        self.randStats[1] = randOB/self.ob * self.stats[1] # get rand HR
        self.randStats[2] = randOB/self.ob * self.stats[2] # get rand RBI
        self.randStats[3] = randOB/self.ob * self.stats[3] # get rand SB

    def finalizeValuation(self):
        self.valuation = self.valuation/self.appearances if self.appearances > 0 else 0
    
    def __str__(self):
        return self.name + " " + str(self.pos) + " " + str(self.valuation)

class Team:
    def __init__(self):
        self.players = []
        self.stats = [0, 0, 0, 0, 0]
        self.ranks = [0, 0, 0, 0, 0]

    def addPlayer(self, player):
        self.players.append(player)

    def compileStats(self):
        for player in self.players:
            self.stats = map(add, self.stats, player.stats)
        self.stats[4] = self.stats[4]/len(self.players)

    def updateValuations(self):
        map(lambda x: x.updateValuation(sum(map(mul, map(div, x.stats, self.stats), self.ranks))), self.players)

    def printTeam(self):
        for player in self.players:
                print "\tPlayer: " + player.name + "," + str(player.pos) + "," + str(player.stats)

class League:
    def __init__(self, numTeams):
        self.teams = []
        self.numTeams = numTeams

    def generateTeams(self, universe):
        posIndex = deepcopy(universe.posIndex)
    
        for teamNum in range(self.numTeams):
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
        with open('W:/Education/2015 Interns/RHMS/Raw Data.csv', 'rb') as csvfile:
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
        tmp = [p.valuation for p in self.players]
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
                
                for p in self.players:
                    p.valuation = 0
                    p.appearances = 0
                    
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
                #if leaguesFormed % 100 is 0:
                #    print leaguesFormed
                    
            map(Player.finalizeValuation, self.universe.players)
            self.getResults()
            if iterate:
                if self.universe.removeWorst() is False:
                    break
            else:
                break
    
    def getResults(self):
        validVals = [self.universe.players[i].valuation for i in self.universe.posIndex['All']]
        minVal = min(validVals)
        sumVal = sum(validVals)

        factor = (20*len(self.universe.posIndex['All'])-len(validVals))/(sumVal-minVal*len(validVals))
        
        for p in self.universe.players:
            p.valuation = (p.valuation-minVal)*factor + 1
            p.valuation = p.valuation if p.valuation > 0 else ""
        
        self.results.append([p.valuation for p in self.universe.players])
    
    def writeResults(self):
        with open('W:/Education/2015 Interns/RHMS/simResults.csv', 'wb') as csvfile:
            w = writer(csvfile)
            
            #for i in range(len(self.results[0])):
            #    w.writerow([x[i] for x in self.results])
            for p in self.universe.players:
                w.writerow([p.valuation])
            
def main():
    start = default_timer()

    sim = Simulation(500, 10)
    sim.run(True)
    sim.writeResults()

    stop = default_timer()
    print "\nTime Elapsed: " + str(stop - start) + " seconds"
    
main()