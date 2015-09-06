#run batch file or
#in python interpreter, run
#   execfile('W:/Education/2015 Interns/RHMS/simulation.py')

from operator import add, mul, div
from collections import defaultdict
from copy import copy, deepcopy
from timeit import default_timer
from random import randrange, sample
from csv import reader, writer

class Player:
    def __init__(self, row):
        self.name = row[0]
        self.pos = row[2].split('/')
        self.g = float(row[3])
        self.stats = map(float, row[4:9])
        self.valuation = 20
        self.appearances = 1

    def updateValuation(self, rank):
        self.valuation += rank
        self.valuation = self.valuation if self.valuation > 0 else 1
        self.appearances += 1
    
    def __str__(self):
        return self.name + " " + str(self.pos) + " " + str(self.valuation)

class Team:
    def __init__(self):
        self.players = []
        self.stats = [0, 0, 0, 0, 0]
        self.ranks = [0, 0, 0, 0, 0]
        self.salary = 0
        self.salaryCap = 180

    def addPlayer(self, player):
        self.players.append(player)

    def compileStats(self):
        for player in self.players:
            self.stats = map(add, self.stats, player.stats)
        self.stats[4] = self.stats[4]/len(self.players)

    def updateValuations(self):
        playerDiff = (sum(self.ranks)-27.5)/12.5*(self.salaryCap-self.salary)/9
        map(lambda x: x.updateValuation(playerDiff), self.players)

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
            
            for pos in sample(universe.selectPos, len(universe.selectPos)):
                indices = copy(posIndex[pos])
                if posIndex[pos]:
                    while True:
                        i = randrange(len(indices))
                        index = indices[i]
                        player = universe.players[index]
                        if player.valuation <= (team.salaryCap - team.salary - (9- len(team.players) - 1)):
                            for p in (player.pos + ['All']):
                                posIndex[p].remove(index)
                            team.addPlayer(player)
                        else:
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

class Simulation:
    def __init__(self, numLeagues, leagueSize):
        self.numLeagues = numLeagues
        self.leagueSize = leagueSize
        
        self.universe = PlayerUniverse()
        self.universe.populateUniverse()
        self.universe.constructUniverse()
        
        self.results = []
        
    def run(self):
        leaguesFormed = 0
        while leaguesFormed < self.numLeagues:
            league = League(self.leagueSize)
            if league.generateTeams(self.universe) is -1:
                continue
            leaguesFormed = leaguesFormed + 1
            league.rankTeams()
            #if leaguesFormed % 100 is 0:
            #    print leaguesFormed
        
        for p in self.universe.players:
            print p.valuation

         
        #self.getResults()
    
    '''def getResults(self):
        validVals = [self.universe.players[i].valuation for i in self.universe.posIndex['All']]
        minVal = min(validVals)
        sumVal = sum(validVals)

        factor = (1800-len(validVals))/(sumVal-minVal*len(validVals))
        
        for p in self.universe.players:
            p.valuation = (p.valuation-minVal)*factor + 1
            print p.valuation
        
        self.results.append([p.valuation for p in self.universe.players])'''
    
    def writeResults(self):
        with open('W:/Education/2015 Interns/RHMS/simResults.csv', 'wb') as csvfile:
            w = writer(csvfile)
            
            for p in self.universe.players:
                w.writerow([p.valuation])
            
def main():
    print "Remember to change DH/OF to OF!\n"
    start = default_timer()

    sim = Simulation(1000, 10)
    sim.run()
    #sim.writeResults()

    stop = default_timer()
    print "\nTime Elapsed: " + str(stop - start) + " seconds"
    
main()