#run batch file or
#in python interpreter, run
#   execfile('W:/Education/2015 Interns/RHKQ/simulation.py')

from operator import add, mul, div
from collections import defaultdict
import csv, random, timeit, numpy

class Player:
    def __init__(self, row):
        self.name = row[0]
        self.pos = row[2].split('/')
        self.g = float(row[3])
        self.stats = map(float, row[4:9])
        self.valuation = 0
        self.appearances = 0

    def updateValuation(self, rank):
        self.valuation += rank
        self.appearances += 1

    def finalizeValuation(self):
        self.valuation = self.valuation/self.appearances if self.appearances > 0 else 0

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
        for _ in range(self.numTeams):
            team = Team()
            for pos in universe.positions[:-1]:
                index = random.choice(universe.posIndex[pos])
                team.addPlayer(universe.players[index])
            for _ in range(3):        
                team.addPlayer(random.choice(universe.players))
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
        self.positions = ['1B','2B','SS','3B','OF','C','DH']
        self.posIndex = defaultdict(list)
    
    def populateUniverse(self):
        with open('W:/Education/2015 Interns/RHKQ/Raw Data.csv', 'rb') as csvfile:
            reader = csv.reader(csvfile)
            reader.next()
            for row in reader:
                player = Player(row)
                self.players.append(player)
    
    def constructUniverse(self):
        for pos in self.positions:
            for i, j in enumerate(self.players):
                if pos in j.pos:
                    self.posIndex[pos].append(i)

class Simulation:
    def __init__(self, numLeagues, leagueSize):
        self.numLeagues = numLeagues
        self.leagueSize = leagueSize
        self.universe = PlayerUniverse()

    def run(self):
        self.universe.populateUniverse()
        self.universe.constructUniverse()
        
        for i in range(self.numLeagues):
            league = League(self.leagueSize)
            league.generateTeams(self.universe)
            league.rankTeams()
    
    def getResults(self):
        map(Player.finalizeValuation, self.universe.players)
        minVal = min([p.valuation for p in self.universe.players])
        sumVal = sum([p.valuation for p in self.universe.players])
        factor = (1800-len(self.universe.players))/(sumVal-minVal*len(self.universe.players))
        for p in self.universe.players:
            p.valuation = (p.valuation-minVal)*factor + 1
            print p.valuation
        print "New Sum: " + str(sum([p.valuation for p in self.universe.players]))
            

start = timeit.default_timer()
sim = Simulation(10000, 10)
sim.run()
sim.getResults()

stop = timeit.default_timer()
print "\nTime Elapsed: " + str(stop - start) + " seconds"