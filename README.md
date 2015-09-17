# Baseball Valuations

This code forms the basis for player valuations for a one-week roto-style fantasy baseball draft given a set of projected stats.

The excel sheets house data about player predictions (assumed true and given), try to value players, and track the draft as it happens. The most recent file is "Week 3 Projections.xlsx"; the file is not that easy to understand without an understanding of fantasy baseball valuation.

The python code tries to determine the values of the players iteratively by simulating thousands of games. The newest version is simulation_v2.py.

The input is "Raw Data.csv", which has the projected stats for each player.

The output is simResults.csv. Each column is the value of each player at that iteration. As the program iterates players are removed from the player "universe" and values are recalculated.
