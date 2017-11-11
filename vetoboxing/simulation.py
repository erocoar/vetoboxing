"""""""""
"" vetoboxing.py
"" This script is designed to run a simulation of veto player voting processes.
"""""""""
#----------------------------------------------------------------------------------------------------#
import os
import time
import logging
from pandas import DataFrame
import numpy as np
from itertools import combinations
from math import floor, ceil

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon
from matplotlib.collections import PatchCollection
import matplotlib.lines as mlines

from shapely.geometry import Point, LinearRing
from scipy.spatial import distance as dist
import copy
logging.basicConfig(filename = "vblog.log", level = logging.DEBUG)

class Simulation():
    def __init__(self, Variables, parent = None):
        self.parent = parent
#        self.parent.logWidget.log.append("log3")
        
        self.Variables = Variables
        
        self.Variables.customRoleArray = False #TODO implement this
        
        """Initialize Voter Arrays"""
        self.voterPositionArray = np.zeros((self.Variables.votercount, self.Variables.runs, self.Variables.dimensions))
        self.voterPositionArray[:, 0, :] = self.Variables.voterPositions
        
        self.voterRadiusArray = np.zeros((self.Variables.votercount, self.Variables.runs, 1))
        
        if self.Variables.customRoleArray:
            print("use CRA")
            self.voterRoleArray = np.array(self.Variables.customRoleArray)
        else:
            if self.Variables.randomVetoPlayer and not self.Variables.randomAgendaSetter:
                self.voterRoleArray = np.random.choice([0, 1], size = (self.Variables.runs, self.Variables.votercount))
                self.voterRoleArray[np.arange(self.voterRoleArray.shape[0]), self.Variables.voterRoles.index(2)] = 2
                
            elif self.Variables.randomAgendaSetter and not self.Variables.randomVetoPlayer:
                self.voterRoleArray = np.repeat(np.array([self.Variables.voterRoles]), self.Variables.runs, axis = 0)
                self.voterRoleArray[np.arange(self.voterRoleArray.shape[0]), 
                                              np.random.choice(np.arange(self.voterRoleArray.shape[1]), size = (self.voterRoleArray.shape[0],))] = 2

            elif self.Variables.randomVetoPlayer and self.Variables.randomAgendaSetter:                                                          
                self.voterRoleArray = np.random.choice([0, 1], size = (self.Variables.runs, self.Variables.votercount))
                """set agenda setter at random index per row, np.arange to index all rows"""
                self.voterRoleArray[np.arange(self.voterRoleArray.shape[0]), 
                                              np.random.choice(np.arange(self.voterRoleArray.shape[1]), size = (self.voterRoleArray.shape[0],))] = 2
                                              
            else:
                self.voterRoleArray = np.repeat(np.array([self.Variables.voterRoles]), self.Variables.runs, axis = 0)
                
        """Initialize SQ, Outcome, Dist Arrays"""
        self.statusQuo = np.zeros(((self.Variables.runs, self.Variables.dimensions)))
        self.statusQuo[0] = self.Variables.statusQuoPosition
        
        self.outcomes = np.zeros(((self.Variables.runs, self.Variables.dimensions)))
        self.dimensionDistance = np.zeros((self.Variables.runs, self.Variables.dimensions))
        
        self.totalPythDistance = np.zeros((self.Variables.runs, 1))
        self.totalManhDistance = np.zeros((self.Variables.runs, 1))
        
        self.breakDecimal = pow(10, str(self.Variables.breaks)[::-1].find("."))
        
        """if shapely, initialize shapely objects for each voter"""
        if self.Variables.method == "optimization":
            self.winsetPatches = []
#            from shapely.geometry import LineString, Point, LinearRing
            
#            self.voterPoints = [Point(position) for position in self.Variables.voterPositions[:, 0, :]]
#            self.voterCircles = [point.buffer(point.distance(self.statusQuo[0])) for point in self.voterPoints]

    def simulation(self):
        """expl"""
        for run in range(self.Variables.runs):
            print("run nr {0} running".format(str(run + 1)))
            
            """get indexes for all roles for specific run"""
            print(self.voterRoleArray)
            agendaSetterIndex = np.where(self.voterRoleArray[run, :] == 2)[0]
            vetoPlayerIndex = np.where(self.voterRoleArray[run, :] == 1)[0]
            normalPlayerIndex = np.where(self.voterRoleArray[run, :] == 0)[0]
            
            """calculate run radius for all voters and update radius array"""
            self.voterRadiusArray[agendaSetterIndex, run] = self.determineDistance(self.voterPositionArray[agendaSetterIndex, run],
                                 self.statusQuo[[run]], self.Variables.distanceType)

            if vetoPlayerIndex.any():
                self.voterRadiusArray[vetoPlayerIndex, run, 0] = self.determineDistance(self.statusQuo[[run]],
                                     self.voterPositionArray[vetoPlayerIndex, run], self.Variables.distanceType)
                
            if normalPlayerIndex.any():
                self.voterRadiusArray[normalPlayerIndex, run, 0] = self.determineDistance(self.statusQuo[[run]],
                                     self.voterPositionArray[normalPlayerIndex, run], self.Variables.distanceType)
                
            """check if agenda setter position == status quo position, in which case the outcome is predetermined"""
            if (self.voterPositionArray[agendaSetterIndex, run] == self.statusQuo[run]).all():
                self.outcomes[run] = self.statusQuo[run]
                self.totalPythDistance[run] = 0
                self.totalManhDistance[run] = 0
                self.dimensionDistance[run] = [0 for _ in range(self.Variables.dimensions)]
                if self.Variables.runs > 1 and run != self.Variables.runs - 1: 
                    self.alterStatusQuo()
                    self.alterPlayerPreferences()
                continue
            
            """determine possible coalitions given a selected majority rule -- coalitions necessarily include veto players and agenda setter"""
            possibleCoalitions = self.determineCoalitions(agendaSetterIndex, vetoPlayerIndex, normalPlayerIndex)
            #TODO from coalition grid search to function
            possibleOutcomes = []
            
            """grid search"""
            if self.Variables.method == "grid":
                """grid index to make grid a square around agenda setter radius"""
                gridIndex = [[self.voterPositionArray[agendaSetterIndex, run].item(dim) - self.voterRadiusArray[agendaSetterIndex, run].item(0) for
                              dim in range(self.Variables.dimensions)], [self.voterPositionArray[agendaSetterIndex, run].item(dim) + 
                    self.voterRadiusArray.item(0) for dim in range(self.Variables.dimensions)]]
                
                pointGrid = self.gridPaint(*gridIndex, self.Variables.breaks, self.breakDecimal)
                
                """exclude points that are outside of agenda setter and veto player winsets"""
                pointGrid = self.gridPointsInWinset(pointGrid, self.statusQuo[[run]], self.voterPositionArray[agendaSetterIndex, run])
                pointGrid = self.gridPointsInWinset(pointGrid, self.statusQuo[[run]], self.voterPositionArray[vetoPlayerIndex, run])
                
                if possibleCoalitions:
                    """select outcomes for all coalitions"""
                    for coalition in possibleCoalitions:
                        pointsInWinset = self.gridPointsInWinset(pointGrid, self.statusQuo[[run]], np.vstack([self.voterPositionArray[coalition, run]]))
                        possibleOutcome = self.gridClosestToAgendaSetter(pointsInWinset, agendaSetterIndex, run)
                        possibleOutcomes.append(possibleOutcome)   
                else:
                    possibleOutcomes.append(self.gridClosestToAgendaSetter(pointGrid, agendaSetterIndex, run))
                    
                if len(possibleOutcomes) > 1:
                    possibleOutcomes = np.vstack([item for item in possibleOutcomes])
                    """select outcome closest to agenda setter"""
                    outcome = self.gridClosestToAgendaSetter(possibleOutcomes, agendaSetterIndex, run)
                    self.outcomes[run] = outcome
                else:
                    self.outcomes[run] = possibleOutcomes[0]
                            
            else:
                statusQuoPoint = Point(self.statusQuo[run])
                voterPoints = [Point(position) for position in self.voterPositionArray[:, run, :]]
                voterCircles = [point.buffer(point.distance(statusQuoPoint)) for point in voterPoints]
                
                winsets = []
                if possibleCoalitions:
                    for coalition in possibleCoalitions:
                        intersection = voterCircles[agendaSetterIndex.item()]
#                        intersection = [voterCircles[index] for index in agendaSetterIndex][0]

                        for voter in coalition + vetoPlayerIndex.tolist():
#                            intersection = intersection.intersection(voterCircles[voter])
                            intersection = intersection.intersection([voterCircles[index] for index in [voter]][0])

                        winsets.append(intersection)
                        
                else:
                    intersection = voterCircles[agendaSetterIndex.item()]
                    
                    for voter in vetoPlayerIndex:
#                        intersection = intersection.intersection(voterCircles[voter])
                        intersection = intersection.intersection([voterCircles[index] for index in [voter]][0])
                        
                    winsets.append(intersection)
                        
                closestPoints = []
                
                for winset in winsets:
                    if winset.area != 0:
                        polExt = LinearRing(winset.exterior.coords)
    #                    d = polExt.project(voterPoints[agendaSetterIndex])
                        d = polExt.project([voterPoints[index] for index in agendaSetterIndex][0])
                        p = polExt.interpolate(d)
                        closestPoint = p.coords[0]
                        closestPoints.append(closestPoint)
                        
                    else:
                        closestPoints.append(self.statusQuo[run].tolist())
                    
                closestPointsDistances = [self.determineDistance(self.statusQuo[[run]], np.array([point])) for point in closestPoints]
                minIndex = np.argmin(closestPointsDistances)
                
                self.outcomes[run] = closestPoints[minIndex]
                
                if self.Variables.visualize:
                    if np.all(self.outcomes[run] != self.statusQuo[run]):
                        self.winsetPatches.append(PatchCollection([Polygon(winsets[minIndex].exterior)], facecolor = "red", linewidth = .5, alpha = .7))
                    else:
                        self.winsetPatches.append(None)
                    
            """determine distances travelled in run"""
            self.totalPythDistance[run] = self.determineDistance(self.outcomes[[run]], self.statusQuo[[run]], "euclidean")
            self.totalManhDistance[run] = self.determineDistance(self.outcomes[[run]], self.statusQuo[[run]], "cityblock")
            
            self.dimensionDistance[run] = np.column_stack([self.determineDistance(self.statusQuo[[run]][None, :, dim],
                                                          self.outcomes[[run]][None, :, dim],
                                                          self.Variables.distanceType) for dim in range(self.Variables.dimensions)])
                                   
                    
            """alter status quo and preferences"""
            if self.Variables.runs > 1 and run != self.Variables.runs - 1:
                print("call alter poss")
                print(run)
                self.alterStatusQuo(run)
                #original passed on "self.outcomes[[run]])"
                self.alterPlayerPreferences(run)
                
#        if self.Variables.visualize:
#            self.visualizeResults()
            
        if self.Variables.save:
            self.saveResults()
            
        if any([self.Variables.randomVetoPlayer, self.Variables.randomAgendaSetter]):
            self.saveRoleArray()
                
       
    def determineCoalitions(self, agendaSetter, vetoPlayers, normalVoters):
        """
        Determines which possible coalitions can form a majority. It checks how many more
        (if any) voters are needed besides the veto players and the agenda setter 
        (which are always required to vote for a proposal) and creates all possible combinations thereof
        """
        requiredVoters = agendaSetter + vetoPlayers
        # check if veto players and the agenda setter are a majority by themselves
        if len(requiredVoters) <= 0.5 * self.Variables.votercount:
            #determine how many more voters are needed
            more_voters = ceil(0.5 * self.Variables.votercount + 1) - self.Variables.votercount % 2 - len(requiredVoters)
        
            possible_coalitions = [list(coalition) for coalition in combinations(normalVoters, more_voters)]           
        # if VPs and agenda setter are already a majority, they are the only coalition
        else:
            possible_coalitions = []
    
        return possible_coalitions
    
    
    def determineDistance(self, point1, point2, distanceType = "euclidean"):  
        """
        Determine the distance between two points in any number of dimensions.
        As such, it can also be used to determine the radius of a preference circle (by inputting
        a point and the status quo).
        """
        if point1.ndim == 1:
            point1 = point1[None, :]
            
        if point2.ndim == 1:
            point2 = point2[None, :]
          
        return dist.cdist(point1, point2, metric = distanceType)
    
        
    def gridPaint(self, start, stop, breaks, break_decimal):
        """
        Points are added at set intervals to a grid of a given size.
        """
        try:
            start_r = [floor(strt * break_decimal) / break_decimal for strt in start]
            stop_r  = [ceil(stp * break_decimal) / break_decimal for stp in stop]
            bins = np.array([(stp - strt) / breaks for stp, strt in zip(stop_r, start_r)])
            bounds = np.array([[begin, end ] for begin, end in zip(start_r, stop_r)])
            position = np.mgrid[[slice(row[0], row[1], n*1j) for row, n in zip(bounds, bins)]]
            position = position.reshape(self.Variables.dimensions, -1).T
            return position  

        except MemoryError:
            logging.error("Memory Error. Could not create grids // Try setting larger breaks")
            raise


    def gridPointsInWinset(self, random_points, status_quo, player):
        """
        Function to determine which points fall inside preference circles of specified players.
        This function is first used to determine the optimum within each coalition, and then
        to determine the final outcome: the optimal point across all coalitions.
        """        
        radius = self.determineDistance(player, status_quo, self.Variables.distanceType).T
        distance = self.determineDistance(random_points, player, self.Variables.distanceType)
        index = np.where(np.all(np.greater_equal(radius, distance), axis = 1))[0]
        return random_points[index]
    
    
    def gridClosestToAgendaSetter(self, points_in_selection, as_index, run):
        """
        This function determines which point from a given array is closest to the agenda setter. It takes all
        points that a have a theoretical majority; now the point is to determine which the AS likes most. This
        will be the most-preferred point and the outcome of the veto-player game. If there is no point that
        lies in the preference circles of all veto players and the agenda setter, this function returns the
        status quo.
        """
        #if there are no points inside all preference circles, the outcome will be the status quo
        if points_in_selection.size == 0:
            preferred_point = self.statusQuo[run].tolist()
        else:
            # determine the distance of each eligible point to the agenda setter
            #TODO: This dist calc is double, store values from pointsInWinset and reuse?
            distance = self.determineDistance(points_in_selection, self.voterPositionArray[as_index, run], 
                                              self.Variables.distanceType)
            # retrieve the index of minimum distance and get the actual point value
            index = np.where(distance == distance.min())
            # currently, only the first value is used. for games with 0 agenda setter better system needed
            preferred_point = points_in_selection[index[0][0]]
            
        return preferred_point
            
              
    def alterStatusQuo(self, run):
        """
        Set the status quo for the new simulation based on alterStatusQuo and vibration distribution
        """       
        # if the status quo doesn"t change there is still vibration
        if self.Variables.alterStatusQuo == "no":
            self.statusQuo[run + 1] = self.statusQuo[run]
            
        elif self.Variables.alterStatusQuo == "randomDrift":
            self.statusQuo[run + 1] = self.statusQuo + self.setVibration(self.statusQuo[run].shape)
        
        # place a completely random status quo on the grid
        #TODO fix to only SQ in winset
        elif self.Variables.alterStatusQuo == "random":
            self.statusQuo[run + 1] = np.random.uniform(0, 100, (1, self.Variables.dimensions))
        
        # alter status quo based on outcome and vibration
        elif self.Variables.alterStatusQuo == "history":
            self.statusQuo[run + 1] = self.outcome[run]
            
        # alter status quo based on outcome of previous run, drift, and vibration
        elif self.Variables.alterStatusQuo == "history+drift":
            self.statusQuo[run + 1] = self.outcomes[run] + self.Variables.statusQuoDrift
        
            
    def alterPlayerPreferences(self, run):
        """
        Function to alter the preferences of the players for every run. Two options: preferences
        do not change (yet there is some vibration), or preferences have a drift in a certain
        direction.
        """  
        if self.Variables.alterPreferences == "randomDrift":
            self.voterPositionArray[:, run + 1, :] = self.voterPositionArray[:, run, :] + self.setVibration(size = self.voterPositionArray[:, run, :].shape)
        
        if self.Variables.alterPreferences == "drift":
            self.voterPositionArray[:, run + 1, :] = self.voterPositionArray[:, run, :] + self.Variables.voterDrift
            
             
    def visualizeInit(self, animate = True, save = False):
        """
        Initialize Figure + Axis
        """  
        """""""Initialize ax lim array"""""""
        print("called")
        if self.Variables.dimensions == 1:
            self.visLimits = np.zeros((2, 2))
        else:
            self.visLimits = np.zeros((self.Variables.dimensions, 2))
            
        if animate:
            filenames = []
            
        if self.Variables.dimensions == 1:
            """""""""
            1D Figure
            """""""""
            self.visLimits[0] = ((self.voterPositionArray - self.voterRadiusArray)[:, :, 0].min(),
                      (self.voterPositionArray + self.voterRadiusArray)[:, :, 0].max())
            self.visLimits[1] = (0, self.voterRadiusArray.max())
            
            if save is True:
                fig = plt.figure(figsize = (20, 5))
                ax = fig.add_subplot(111)
                for run in range(self.Variables.runs):
                    self.visualizeDrawOnAxis(1, ax, run, self.visLimits)
                    
                    filename = os.path.join(self.Variables.directory, "run" + str(run) + ".png")
                    fig.savefig(filename, bbox_inches = "tight")
                    
                    if animate:
                        filenames.append(filename)
                        
                plt.close(fig)
        
        elif self.Variables.dimensions == 2:
            """""""""
            2D Figure
            """""""""
            for dim in range(self.Variables.dimensions):
                self.visLimits[dim] = ((self.voterPositionArray - self.voterRadiusArray).min(),
                          (self.voterPositionArray + self.voterRadiusArray).max())
                
                
            if save is True:
                self.Variables.traceTotalChange = False
                if self.Variables.traceTotalChange is True:
                    fig, (ax, ax1) = plt.subplots(2, 1, gridspec_kw = {"height_ratios" : [4, 1]})
                    fig.set_size_inches(10, 10)
                    fig.set_dpi(80)
                    ax1.plot(range(self.Variables.runs), self.totalPythDistance, c = "#1f77b4")
                    ax1.scatter(run, self.totalPythDistance[run], c = "#d62728", s = 40, clip_on = False)
    
                else:
                    fig = plt.figure(figsize = (18.5, 10.5))
                    ax = fig.add_subplot(111, aspect = "equal")
                    
                for run in range(self.Variables.runs):
                    self.visualizeDrawOnAxis(2, ax, run, self.visLimits)
                    
                    filename = os.path.join(self.Variables.directory, "run" + str(run) + ".png")
                    fig.savefig(filename, bbox_inches = "tight")
                    
                    if animate:
                        filenames.append(filename)
                        
                plt.close(fig)
                
        elif self.Variables.dimensions == 3:
            """""""""
            3D Figure
            """""""""
            from mpl_toolkits.mplot3d import Axes3D
            def drawSphere(self, xCenter, yCenter, zCenter, r):
                #draw sphere
                u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
                x=np.cos(u)*np.sin(v)
                y=np.sin(u)*np.sin(v)
                z=np.cos(v)
                # shift and scale sphere
                x = r*x + xCenter
                y = r*y + yCenter
                z = r*z + zCenter
                return (x,y,z)
            
            for dim in range(self.Variables.number_dimensions):
                self.visLimits[dim] = ((self.voterPositionArray - self.voterRadiusArray)[:, :, dim].min(),
                          (self.voterPositionArray + self.voterRadiusArray)[:, :, dim].max())
                
                
    def visualizeDrawOnAxis(self, dim, ax, run, lims, fromUI = False):
        """
        Clear and then plot on given axis
        """
        print("plot fig" + str(run))
        ax.cla()
        
        if dim == 1:
            """
            1D
            """
            ax.set_xlim(lims[0, 0], lims[0, 1])
            ax.set_ylim(lims[1, 0], lims[1, 1])
    
                    #in role array, normal voter == 0, agenda setter == 1, veto player == 2
            if 0 in self.voterRoleArray[run]:
                index = np.where(np.squeeze(np.isin(self.voterRoleArray[run], 0)))[0]
    
                ax.scatter(self.voterPositionArray[index, run], [0 for i in index],
                           s = 70, c = "black", label = "Voters", clip_on = False)
    
                norm_patches = [Circle((xx, 0), rr) for xx, rr in zip(self.voterPositionArray[index, run], self.voterRadiusArray[index, run])]
                        
                norm_collection = PatchCollection(norm_patches, facecolors = "grey", edgecolors = "black", linewidths = 0.5, alpha = 0.2)
            
                ax.add_collection(norm_collection)
                norm_collection.set_clip_box(ax.bbox)
    
    
            if 2 in self.voterRoleArray[run]:
                index = np.where(np.squeeze(np.isin(self.voterRoleArray[run], 1)))[0]
                
                ax.scatter(self.voterPositionArray[index, run], [0 for i in index], s = 60, c = "red", label = "Veto Players", clip_on = False)
                
                veto_patches = [Circle((xx, 0), rr) for xx, rr in zip(self.voterPositionArray[index, run], self.voterRadiusArray[index, run])]
                        
                veto_collection = PatchCollection(veto_patches, facecolors = "red", edgecolors = "black", linewidths = 0.5, alpha = 0.2)
                        
                ax.add_collection(veto_collection)
                veto_collection.set_clip_box(ax.bbox)
                        
            index = np.where(np.squeeze(np.isin(self.voterRoleArray[run], 2)))[0]

            ax.scatter(self.voterPositionArray[index, run], 0, s = 60, c = "lightblue", label = "Agenda Setter", clip_on = False)
    
            as_patch = Circle((self.voterPositionArray[index, run], 0), self.voterRadiusArray[index, run],
                                       facecolor = "blue", edgecolor = "black", linewidth = 0.5, alpha = 0.2)                      
                        
            ax.add_artist(as_patch)
            as_patch.set_clip_box(ax.bbox)
                    
            ax.scatter(self.statusQuo[run], 0, s = 60, c = "orange", label = "Status Quo", clip_on = False)
                    
            ax.scatter(self.outcomes[run], 0, s = 50, c = "yellow", label = "Outcome", clip_on = False)
        
            box = ax.get_position()
                    
            ax.set_position([box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9])
                    
            ax.legend(scatterpoints = 1, loc = "upper center", shadow = "True", bbox_to_anchor = (0.5, -0.05), ncol = 3, fancybox = True)
                    
            ax.annotate("Run: " + str(run+1), xy = (1, 1), xycoords = "axes fraction")

        elif dim == 2:
            """
            2D
            """
            ax.set_xlim(lims[0, 0], lims[0, 1])
            ax.set_ylim(lims[1, 0], lims[1, 1])
                
            if 0 in self.voterRoleArray[run]:
                """
                plot normal voters
                """
                index = np.where(np.squeeze(self.voterRoleArray[run] == 0))[0]

                ax.scatter(self.voterPositionArray[index, run, 0], self.voterPositionArray[index, run, 1], s = 30, c = "#7f7f7f", label = "Voters")

                norm_patches = [Circle((xx, yy), rr) for xx, yy, rr in zip(self.voterPositionArray[index, run, 0],
                                self.voterPositionArray[index, run, 1],
                                self.voterRadiusArray[index, run])]
                                    
                norm_collection = PatchCollection(norm_patches, facecolors = "#7f7f7f", edgecolors = "black", linewidths = 0.5, alpha = 0.2)
                                    
                ax.add_collection(norm_collection)
                norm_collection.set_clip_box(ax.bbox)

            if 1 in self.voterRoleArray[run]:
                """
                plot veto players
                """ 
                index = np.where(np.squeeze(self.voterRoleArray[run] == 1))[0]
                
                ax.scatter(self.voterPositionArray[index, run, 0], self.voterPositionArray[index, run, 1],
                           s = 30, c = "#d62728", label = "Veto Players")
                
                veto_patches = [Circle((xx, yy), rr) for xx, yy, rr in zip(
                        self.voterPositionArray[index, run, 0], 
                        self.voterPositionArray[index, run, 1],
                        self.voterRadiusArray[index, run])]

                veto_collection = PatchCollection(veto_patches, facecolors = "#d62728", 
                                                  alpha = 0.2, linewidths = 0.5, edgecolors = "black")
                
                ax.add_collection(veto_collection)
                veto_collection.set_clip_box(ax.bbox)
                    
            """
            plot agenda setter
            """
            index = np.where(np.squeeze(self.voterRoleArray[run] == 2))[0]
            ax.scatter(self.voterPositionArray[index, run, 0], self.voterPositionArray[index, run, 1],
                    s = 30, c = "#1f77b4", label = "Agenda Setter")
            
            as_patch = Circle((
                    self.voterPositionArray[index, run, 0],
                    self.voterPositionArray[index, run, 1]),
                    self.voterRadiusArray[index, run],
                    facecolor = "#1f77b4", edgecolor = "black", linewidth = 0.5, alpha = 0.2)

            ax.add_artist(as_patch)
            as_patch.set_clip_box(ax.bbox)
                
            """
            plot status quo and outcome
            """
            ax.scatter(self.statusQuo[run, 0], self.statusQuo[run, 1], s = 35, c = "#8c564b", label = "Status Quo")
            ax.scatter(self.outcomes[run, 0], self.outcomes[run, 1], s = 30, c = "#ff7f0e", label = "Outcome")
            
            """add precise winset patch"""
            if self.Variables.method == "optimization" and self.winsetPatches[run] is not None:
                print("add winset patch")
                if not fromUI:
                    ax.add_collection(self.winsetPatches[run])
                else:
                    UI_winsetPatch = copy.copy(self.winsetPatches[run])
                    UI_winsetPatch.axes = None
                    UI_winsetPatch.figure = None
                    UI_winsetPatch.set_transform(ax.transData)
                    ax.add_collection(UI_winsetPatch)
            
            #trace status quo
            if self.Variables.trace is True:
                lines = [mlines.Line2D([self.statusQuo[run, 0], self.outcomes[run, 0]], 
                                       [self.statusQuo[run, 1], self.outcomes[run, 1]],
                                       linewidth = 2, color = "#2ca02c", alpha = 1)]
                    
                if run <= 4:
                    lines += [mlines.Line2D([self.statusQuo[run - i - 1, 0], self.statusQuo[run - i, 0]],
                                            [self.statusQuo[run - i - 1, 1], self.statusQuo[run - i, 1]],
                                            linewidth = 2, color = "#2ca02c", alpha = (0.8 - i * .2)) for i in range(run)]
                    
                else: 
                    lines += [mlines.Line2D([self.statusQuo[run - i - 1, 0], self.statusQuo[run - i, 0]], 
                                           [self.statusQuo[run - i - 1, 1], self.statusQuo[run - i, 1]],
                                           linewidth = 2, color = "#2ca02c", alpha = (0.8 - i * .2)) for i in range(5)]

                [ax.add_line(line) for line in lines]
            
            box = ax.get_position()
                            
            ax.legend(scatterpoints = 1, loc = "upper center", shadow = "True", bbox_to_anchor = (0.5, -0.05), ncol = 3, fancybox = True)
            
            ax.annotate("Run: " + str(run+1), xy = (1, 1), xycoords="axes fraction")
            
             
    def visualizeAnimate(self, filenames):
        pass

#    def visualizeResults(self, animate = True):
#        """
#        This function visualizes the results of the runs and saves them as png files in a specified folder
#        """           
#            for run in range(self.Variables.runs):
#                ax.set_xlim(vis_limits[0, 0], vis_limits[0, 1])
#                ax.set_ylim(vis_limits[1, 0], vis_limits[1, 1])
#
#                #in role array, normal voter == 0, agenda setter == 1, veto player == 2
#                if 0 in self.voterRoleArray[run]:
#                    
#                    index = np.where(np.squeeze(np.isin(self.voterRoleArray[run], 0)))[0]
#                    
#                    ax.scatter(self.voterPositionArray[index, run], [0 for i in index],
#                               s = 70, c = "black", label = "Voters", clip_on = False)
#
#                    norm_patches = [Circle((xx, 0), rr) for xx, rr in zip(
#                            self.voterPositionArray[index, run], 
#                            self.voterRadiusArray[index, run])]
#                    
#                    norm_collection = PatchCollection(norm_patches, facecolors = "grey", 
#                                                      edgecolors = "black", linewidths = 0.5, alpha = 0.2)
#                    
#                    ax.add_collection(norm_collection)
#                    norm_collection.set_clip_box(ax.bbox)
#
#
#                if 2 in self.voterRoleArray[run]:
#                    print("VRA")
#                    print(self.voterRoleArray[run])
#                    index = np.where(np.squeeze(np.isin(self.voterRoleArray[run], 2)))[0]
#
#                    ax.scatter(self.voterPositionArray[index, run], [0 for i in index],
#                               s = 60, c = "red", label = "Veto Players", clip_on = False)
#                    
#                    veto_patches = [Circle((xx, 0), rr) for xx, rr in zip(
#                            self.voterPositionArray[index, run], 
#                            self.voterRadiusArray[index, run])]
#                    
#                    veto_collection = PatchCollection(veto_patches, facecolors = "red", 
#                                                      edgecolors = "black", linewidths = 0.5, alpha = 0.2)
#                    
#                    ax.add_collection(veto_collection)
#                    veto_collection.set_clip_box(ax.bbox)
#                    
#                index = np.where(np.squeeze(np.isin(self.voterRoleArray[run], 1)))[0]
#                print(self.voterPositionArray[index, run])
#                ax.scatter(self.voterPositionArray[index, run], [0], s = 60, c = "lightblue", label = "Agenda Setter", clip_on = False)
#
#                as_patch = Circle((self.voterPositionArray[index, run], 0), self.voterRadiusArray[index, run],
#                                   facecolor = "blue", edgecolor = "black", linewidth = 0.5, alpha = 0.2)                      
#                    
#                ax.add_artist(as_patch)
#                as_patch.set_clip_box(ax.bbox)
#                
#                ax.scatter(self.statusQuo[run], 0, s = 60, c = "orange", label = "Status Quo", clip_on = False)
#                
#                ax.scatter(self.outcomes[run], 0, s = 50, c = "yellow", label = "Outcome", clip_on = False)
#    
#                box = ax.get_position()
#                
#                ax.set_position([box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9])
#                
#                ax.legend(scatterpoints = 1, loc = "upper center", shadow = "True", bbox_to_anchor = (0.5, -0.05), ncol = 3, fancybox = True)
#                
#                ax.annotate("Run: " + str(run+1), xy = (1, 1), xycoords = "axes fraction")
#        
#                filename = "".join((self.Variables.directory, "/", str(run), ".png"))
#                
#                fig.savefig(filename, bbox_inches = "tight")
#                                
#                filenames.append(filename)
#    
#                plt.close("all")
#                
#
#        elif self.Variables.dimensions == 2:
#            """""""""
#            2D Plot
#            """""""""
#            
#            for dim in range(self.Variables.dimensions):
#                vis_limits[dim] = ((self.voterPositionArray - self.voterRadiusArray).min(),
#                          (self.voterPositionArray + self.voterRadiusArray).max())
#                    
#                
#            self.Variables.traceTotalChange = False
#            if self.Variables.traceTotalChange is True:
#                fig, (ax, ax1) = plt.subplots(2, 1, gridspec_kw = {"height_ratios":[4, 1]})
#                fig.set_size_inches(10, 10)
#                fig.set_dpi(80)
#                ax1.plot(range(self.Variables.runs), self.totalPythDistance, c = "#1f77b4")
#                ax1.scatter(run, self.totalPythDistance[run], c = "#d62728", s = 40, clip_on = False)
#
#            else:
#                fig = plt.figure(figsize = (18.5, 10.5))
#                ax = fig.add_subplot(111, aspect="equal")
#                    
#
#                
#            for run in range(self.Variables.runs):
#                ax.set_xlim(vis_limits[0, 0], vis_limits[0, 1])
#                ax.set_ylim(vis_limits[1, 0], vis_limits[1, 1])
#                
#                if 0 in self.voterRoleArray[run]:
#                    """
#                    plot normal voters
#                    """
#                    index = np.where(np.squeeze(self.voterRoleArray[run] == 0))[0]
#
#                    ax.scatter(self.voterPositionArray[index, run, 0], self.voterPositionArray[index, run, 1],
#                            s = 30, c = "#7f7f7f", label = "Voters")
#
#                    norm_patches = [Circle((xx, yy), rr) for xx, yy, rr in zip(
#                                    self.voterPositionArray[index, run, 0],
#                                    self.voterPositionArray[index, run, 1],
#                                    self.voterRadiusArray[index, run])]
#                                    
#                    norm_collection = PatchCollection(norm_patches, facecolors = "#7f7f7f",
#                                                      edgecolors = "black", linewidths = 0.5, alpha = 0.2)
#                                    
#                    ax.add_collection(norm_collection)
#                    norm_collection.set_clip_box(ax.bbox)
#
#                if 1 in self.voterRoleArray[run]:
#                    """
#                    plot veto players
#                    """ 
#                    index = np.where(np.squeeze(self.voterRoleArray[run] == 1))[0]
#                    
#                    ax.scatter(self.voterPositionArray[index, run, 0], self.voterPositionArray[index, run, 1],
#                               s = 30, c = "#d62728", label = "Veto Players")
#                    
#                    veto_patches = [Circle((xx, yy), rr) for xx, yy, rr in zip(
#                            self.voterPositionArray[index, run, 0], 
#                            self.voterPositionArray[index, run, 1],
#                            self.voterRadiusArray[index, run])]
#
#                    veto_collection = PatchCollection(veto_patches, facecolors = "#d62728", 
#                                                      alpha = 0.2, linewidths = 0.5, edgecolors = "black")
#                    
#                    ax.add_collection(veto_collection)
#                    veto_collection.set_clip_box(ax.bbox)
#                    
#                """
#                plot agenda setter
#                """
#                index = np.where(np.squeeze(self.voterRoleArray[run] == 2))[0]
#                ax.scatter(self.voterPositionArray[index, run, 0], self.voterPositionArray[index, run, 1],
#                        s = 30, c = "#1f77b4", label = "Agenda Setter")
#                
#                as_patch = Circle((
#                        self.voterPositionArray[index, run, 0],
#                        self.voterPositionArray[index, run, 1]),
#                        self.voterRadiusArray[index, run],
#                        facecolor = "#1f77b4", edgecolor = "black", linewidth = 0.5, alpha = 0.2)
#
#                ax.add_artist(as_patch)
#                as_patch.set_clip_box(ax.bbox)
#                
#                """
#                plot status quo and outcome
#                """
#                ax.scatter(self.statusQuo[run, 0], self.statusQuo[run, 1], s = 35, c = "#8c564b", label = "Status Quo")
#                ax.scatter(self.outcomes[run, 0], self.outcomes[run, 1], s = 30, c = "#ff7f0e", label = "Outcome")
#                
#                """add precise winset patch"""
#                if self.Variables.method == "optimization" and self.winsetPatches[run] is not None:
#                    ax.add_collection(self.winsetPatches[run])
#                    
#                #trace status quo
#                if self.Variables.trace is True:
#                    lines = [mlines.Line2D([self.statusQuo[run, 0], self.outcomes[run, 0]], 
#                                           [self.statusQuo[run, 1], self.outcomes[run, 1]],
#                                           linewidth = 2, color = "#2ca02c", alpha = 1)]
#                        
#                    if run <= 4:
#                        lines += [mlines.Line2D([self.statusQuo[run - i - 1, 0], self.statusQuo[run - i, 0]],
#                                                [self.statusQuo[run - i - 1, 1], self.statusQuo[run - i, 1]],
#                                                linewidth = 2, color = "#2ca02c", alpha = (0.8 - i * .2)) for i in range(run)]
#                        
#                    else: 
#                        lines += [mlines.Line2D([self.statusQuo[run - i - 1, 0], self.statusQuo[run - i, 0]], 
#                                               [self.statusQuo[run - i - 1, 1], self.statusQuo[run - i, 1]],
#                                               linewidth = 2, color = "#2ca02c", alpha = (0.8 - i * .2)) for i in range(5)]
#    
#                    [ax.add_line(line) for line in lines]
#                
#                box = ax.get_position()
#                
##                ax.set_position([box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9])
#                
#                ax.legend(scatterpoints = 1, loc = "upper center", shadow = "True", bbox_to_anchor = (0.5, -0.05), ncol = 3, fancybox = True)
#                
#                ax.annotate("Run: " + str(run+1), xy = (1, 1), xycoords="axes fraction")
#    
#                filename = os.path.join(self.Variables.directory, "run" + str(run) + ".png")
#                print(filename)
#                fig.savefig(filename, bbox_inches = "tight", dpi = 100)
#                    
#                filenames.append(filename)
#                
##                plt.close("all")
#                plt.cla()
#                
#        elif self.Variables.dimensions == 3:
#            from mpl_toolkits.mplot3d import Axes3D
#            def drawSphere(xCenter, yCenter, zCenter, r):
#                #draw sphere
#                u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
#                x=np.cos(u)*np.sin(v)
#                y=np.sin(u)*np.sin(v)
#                z=np.cos(v)
#                # shift and scale sphere
#                x = r*x + xCenter
#                y = r*y + yCenter
#                z = r*z + zCenter
#                return (x,y,z)
#            
#            for dim in range(self.Variables.number_dimensions):
#                
#                vis_limits[dim] = (
#                        (self.voterPositionArray - self.voterRadiusArray)[:, :, dim].min(),
#                        (self.voterPositionArray + self.voterRadiusArray)[:, :, dim].max()
#                        )
#            
#            for run in range(self.Variables.runs):
#            
#                fig = plt.figure(figsize = (18.5, 10.5), dpi = 80)
#                ax = fig.gca(projection="3d")
#                ax.set_aspect("equal")
#              
#                ax.set_xlim(vis_limits[0, 0], vis_limits[0, 1])
#                ax.set_ylim(vis_limits[1, 0], vis_limits[1, 1])
#                ax.set_zlim(vis_limits[2, 0], vis_limits[2, 1])
#                
#                if 0 in self.voterRoleArray[:, run]:                    
#                    index = np.where(np.squeeze(np.isin(self.voterRoleArray[:, run], 0)))[0]
#                    
#                    ax.scatter(
#                            self.voterPositionArray[index, run, 0], 
#                            self.voterPositionArray[index, run, 1],
#                            self.voterPositionArray[index, run, 2],
#                            s = 40, c = "#7f7f7f", label = "Voters"
#                            )
#                    
#                    [ax.plot_wireframe(*drawSphere(xx, yy, zz, rr), color="#7f7f7f", linewidths = 1, alpha = 0.3) for xx, yy, zz, rr in zip(
#                            self.voterPositionArray[index, run, 0],
#                            self.voterPositionArray[index, run, 1],
#                            self.voterPositionArray[index, run, 2],
#                            self.voterPositionArray[index, run])]
#                    
#                if 2 in self.voterRoleArray[run]:
#                    index = np.where(np.squeeze(np.isin(self.voterRoleArrayay[:, run], 2)))[0]
#                    
#                    ax.scatter(self.voterPositionArray[index, run, 0], 
#                               self.voterPositionArray[index, run, 1],
#                               self.voterPositionArray[index, run, 2],
#                               s = 40, c = "#d62728", label = "Veto Players")
#                    
#                    [ax.plot_wireframe(*drawSphere(xx, yy, zz, rr), color="#d62728", linewidths = 1, alpha = 0.3) for xx, yy, zz, rr in zip(
#                            self.voterPositionArray[index, run, 0],
#                            self.voterPositionArray[index, run, 1],
#                            self.voterPositionArray[index, run, 2],
#                            self.voterRadiusArray[index, run])]                   
#                    
#                index = np.where(np.squeeze(np.isin(self.voterRoleArray[run], 1)))[0]
#                
#                ax.scatter(
#                        self.voterPositionArray[index, run, 0],
#                        self.voterPositionArray[index, run, 1],
#                        s = 30, c = "#1f77b4", label = "Agenda Setter"
#                        )
#                
#                ax.plot_wireframe(*drawSphere(self.voterPositionArray[index, run, 0], 
#                                              self.voterPositionArray[index, run, 1],
#                                              self.voterPositionArray[index, run, 2],
#                                              self.voterRadiusArray[index, run]), color = "#1f77b4", alpha = 0.3)
#                
#                ax.scatter(self.statusQuo[run, 0], self.statusQuo[run, 1], self.statusQuo[run, 2], s = 55, c = "#8c564b", alpha = 1, label = "Status Quo")
#                ax.scatter(self.outcomes[run, 0], self.outcomes[run, 1], self.outcomes[run, 2], s = 50, c = "#ff7f0e", alpha = 1, label = "Outcome")               
#            
#                if self.Variables.trace is True:     
#                    line1 = [(self.statusQuo[run, 0], self.outcomes[run, 0]),
#                             (self.statusQuo[run, 1], self.outcomes[run, 1]),
#                             (self.statusQuo[run, 2], self.outcomes[run, 2])]
#                        
#                    if run <= 4:
#                        lines = [[(self.statusQuo[run - i - 1, 0], self.statusQuo[run - i, 0]),
#                                  (self.statusQuo[run - i - 1, 1], self.statusQuo[run - i, 1]),
#                                  (self.statusQuo[run - i - 1, 2], self.statusQuo[run - i, 2])] for i in range(run)]
#                                  
#                    else: 
#                        lines = [[(self.statusQuo[run - i - 1, 0], self.statusQuo[run - i, 0]),
#                                  (self.statusQuo[run - i - 1, 1], self.statusQuo[run - i, 1]),
#                                  (self.statusQuo[run - i - 1, 2], self.statusQuo[run - i, 2])] for i in range(5)]
#                        
#                    ax.plot(*line1, alpha = 1, color = "#2ca02c")
#                    for i, item in enumerate(lines):
#                        ax.plot(item[0], item[1], item[2], color = "#2ca02c", alpha = (0.8 - i * .2))
#    
#                box = ax.get_position()
#                
#                ax.set_position([box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9])
#                
#                ax.legend(scatterpoints = 1, loc = "upper center", shadow = "True", bbox_to_anchor = (0.5, -0.05), ncol = 3, fancybox = True)
#                
#                ax.annotate("Run: " + str(run+1), xy = (1, 1), xycoords = "axes fraction")
#    
#                filename = os.path.join(self.Variables.directory, "run" + str(run) + ".png")
#                
#                fig.savefig(filename, bbox_inches = "tight")
#                    
#                filenames.append(filename)
#                
#                plt.close("all")    
#                            
#        if animate is True:
#            import imageio
#            images = [imageio.imread(file) for file in filenames]
#            imageio.mimsave(os.path.join(self.Variables.directory, "animation.gif"), images, duration = 1 / 10)
            
            
    def saveResults(self):
        """
        Save results to csv
        """
        colnames = [y for x in [
                ["Voter " + str(i + 1) + "-" + voter + "-ROLE"] + 
                ["Voter " + str(i + 1) + "-" + voter + "-DIM-" + str(dim + 1) for dim in range(self.Variables.dimensions)] +
                ["Voter " + str(i + 1) + "-" + voter + "-RADIUS"] for i, voter in enumerate(self.Variables.voterNames)] for y in x] +\
                ["Status Quo" + "-DIM " + str(dim + 1) for dim in range(self.Variables.dimensions)]+\
                ["Outcome" + "-DIM " + str(dim + 1) for dim in range(self.Variables.dimensions)]+\
                ["Total Euclidean Distance", "Total Manhattan Distance"]+\
                ["Distance" + "-dim " + str(dim + 1) for dim in range(self.Variables.dimensions)]+\
                ["Number Veto Players", "Number Normal Voters"]

        #data
        
        data = np.column_stack([self.voterRoleArray] +\
                               [np.column_stack((self.voterPositionArray[i],
                                                 self.voterRadiusArray[i])) for
                    i in range(len(self.Variables.voterNames))] +\
                                                 [self.statusQuo,
                                                  self.outcomes,
                                                  self.totalPythDistance,
                                                  self.totalManhDistance,
                                                  self.dimensionDistance,
                                                  np.sum(self.voterRoleArray == 1, axis = 1, keepdims = True),
                                                  np.sum(self.voterRoleArray == 0, axis = 1, keepdims = True)])
                
        dataframe = DataFrame(data = data, columns = colnames)
   
        # setting up filename and folder
        timestr = time.strftime("%Y-%m-%d_%H%M")
        
        filename = "".join(("results", "-", str(self.Variables.runs), "r-", str(self.Variables.dimensions), "d-", "__", timestr, ".csv"))
        
        csv_path = os.path.join(self.Variables.directory, filename)
    
        dataframe.to_csv(csv_path)
    
        return filename
    
    def saveRoleArray(self):
        import json
        out = {}
        out["sequence"] = self.voterRoleArray.tolist()
        
        with open(os.path.join(self.Variables.directory, "voter_sequence.txt"), "w") as outfile:
            json.dump(out, outfile)
    #----------------------------------------------------------------------------------------------------#
    
    def setVibration(self, size):
        """
        This function picks the appropriate distribution to draw from
        for the vibration of players and status quo.
        """
        if self.Variables.distribution == "normal":
            return self.randomNormal()
        
        elif self.Variables.distribution == "uniform":
            return np.random.uniform(low = -1, high = 1, size = size)
        
        elif self.Variables.distribution == "exponential":
            return self.randomExponential()
        
        elif self.Variables.distribution == "paretian":
            return self.randomPareto()
    
    #----------------------------------------------------------------------------------------------------#   
    #draws from specified distribution
    def randomNormal(self):
        return np.random.normal(-0.2, 0.2)
    
    def randomUniform(self):
        return np.random.uniform(low = -5.0, high = 5.0, size = self.Variables.dimensions)
    
    def randomExponential(self):
        return np.random.exponential(scale = 1.0)
    
    def randomPareto(self):
        return np.random.pareto(5)