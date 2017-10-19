'''''''''
'' vetoboxing.py
'' This script is designed to run a simulation of veto player voting processes.
'''''''''
#----------------------------------------------------------------------------------------------------#
import os
import itertools
import random
from math import floor, ceil
import numpy as np
import logging
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib.collections import PatchCollection
import matplotlib.lines as mlines
import vb_init as vinit
import vb_animation_drawer
from scipy.spatial import distance as dist
from pandas import DataFrame
import time

logging.basicConfig(filename = 'vb_log.log', level = logging.DEBUG)

#----------------------------------------------------------------------------------------------------#
###################### Class that contains the main functions of the simulation ######################
#----------------------------------------------------------------------------------------------------#

class Simulation(object):
    def __init__(self):
        #set up variables from var.py / gui 
        self.Variables = vinit.setVars()
        
    def __id__(self, x):
        return x.__array_interface__['data'][0]

    def simulation(self):  
        '''
        Function to run the simulation. Here, all different parts of the simulation come together. Reading it
        will give you a general understanding of the logic of this script. In adddition, all variables that
        are ultimately saved to csv are stored in this function.
        '''
        #initialize arrays
        start_time = time.time()
        
        self.voter_position_array = np.zeros((len(self.Variables.voters), self.Variables.runs, self.Variables.number_dimensions))
        self.voter_radius_array = np.zeros((len(self.Variables.voters), self.Variables.runs, 1))
        
        if self.Variables.custom_role_array is True:
            self.voter_role_array = np.array(self.Variables.role_array)
        else:
            self.voter_role_array = np.zeros((len(self.Variables.voters), self.Variables.runs, 1))
        
        self.status_quo = np.zeros(((self.Variables.runs, self.Variables.number_dimensions)))
        self.outcomes = np.zeros(((self.Variables.runs, self.Variables.number_dimensions)))
        self.dimension_distance = np.zeros((self.Variables.runs, self.Variables.number_dimensions))
        
        self.total_pyth_distance = np.zeros((self.Variables.runs, 1))
        self.total_manh_distance = np.zeros((self.Variables.runs, 1))
        
        break_decimal = pow(10, str(self.Variables.breaks)[::-1].find('.'))
            
        for run in range(self.Variables.runs):
            
            logging.info('Simulation number ' + str(run + 1) + ' running')
            print('run nr {0} running'.format(str(run + 1)))
            
            if self.Variables.custom_role_array is not True and self.Variables.custom_sequence is True:
                self.roleAssignment(run)

            # get the voter positions and status quo
            for _, voter in enumerate(self.Variables.voters):
                self.voter_position_array[_, run] = voter.position
          
            self.status_quo[[run]] = self.Variables.status_quo
                           
            #get the roles & update role and index arrays
            if self.Variables.custom_role_array is True:
                as_index = np.where(self.voter_role_array[:, run] == 1)[0].tolist()
                veto_index = np.where(self.voter_role_array[:, run] == 2)[0].tolist()
                normal_index = np.where(self.voter_role_array[:, run] == 0)[0].tolist()                
                
            else:
                as_index = [i for i, _ in enumerate(self.Variables.voters) if _.agenda_setter is True]
                veto_index = [i for i, _ in enumerate(self.Variables.voters) if _.veto_player is True]
                normal_index = [i for i, _ in enumerate(self.Variables.voters) if _.veto_player is not True 
                                and _.agenda_setter is  not True]
            
                self.voter_role_array[as_index, run] = 1
                                
                self.voter_role_array[veto_index, run] = 2
                                 
            #calculate radius for all voters & update radius array
            self.voter_radius_array[as_index, run] = self.determineDistance(self.voter_position_array[as_index, run], 
                                   self.status_quo[[run]], self.Variables.distance_type)
            
            if veto_index:
                self.voter_radius_array[veto_index, run, 0] = self.determineDistance(self.status_quo[[run]], 
                                       self.voter_position_array[veto_index, run], self.Variables.distance_type)
            
            if normal_index:
                self.voter_radius_array[normal_index, run, 0] = self.determineDistance(self.status_quo[[run]], 
                                       self.voter_position_array[normal_index, run], self.Variables.distance_type)

            if (self.voter_position_array[as_index, run] == self.status_quo[run]).all():
                self.outcomes[run] = self.status_quo[run]
                self.total_pyth_distance[run] = 0
                self.total_manh_distance[run] = 0
                self.dimension_distance[run] = [0 for i in range(self.Variables.number_dimensions)]
                self.alterStatusQuo(self.outcomes[[run]])
                self.alterPlayerPreferences()
                continue
                
            #grid index to create grid of potential outcomes (this is a square around agenda setter radius)
            grid_index = [[self.voter_position_array[as_index, run].item(dim) - 
                           self.voter_radius_array[as_index, run].item(0) 
                           for dim in range(self.Variables.number_dimensions)],
                           [self.voter_position_array[as_index, run].item(dim) + 
                            self.voter_radius_array.item(0) for dim in range(self.Variables.number_dimensions)]]

            random_points = self.paintGrid(*grid_index, self.Variables.breaks, break_decimal)
            
            #exclude points that are outside of agenda setter & veto player winsets
            random_points = self.pointsInWinset(random_points, self.status_quo[[run]], self.voter_position_array[as_index, run])
            random_points = self.pointsInWinset(random_points, self.status_quo[[run]], self.voter_position_array[veto_index, run])
            
            #determine possible coalitions that can form a majority - must include veto players and as
            possible_coalitions = self.determineCoalitions(as_index, veto_index, normal_index)
            print("as index", as_index)
            print("veto index", veto_index)
            print("normal index", normal_index)
            print("coal done")
            print(possible_coalitions)
            possible_outcomes = []
            
            #determine the possible outcomes of all coalitions
            if possible_coalitions:
                for coalition in possible_coalitions:
                    #select the points that are in winset of the ith coalition
                    points_in_circle = self.pointsInWinset(random_points, self.status_quo[[run]],
                                                           np.vstack([self.voter_position_array[coalition, run]]))
    
                    possible_outcome = self.closestToAgendaSetter(points_in_circle, as_index, run)
                    
                    possible_outcomes.append(possible_outcome)
                    
            else:              
                possible_outcomes.append(self.closestToAgendaSetter(random_points, as_index, run))
                
            if len(possible_outcomes) > 1:
                possible_outcomes = np.vstack([item for item in possible_outcomes])
                # select the point preferred by the agenda setter out of all possible outcomes, and append to results
                outcome = self.closestToAgendaSetter(possible_outcomes, as_index, run)
                self.outcomes[run] = outcome
                                
            else:
                self.outcomes[run] = possible_outcomes[0]
                
            # determine the euclidean and manhattan distance that was travelled in this run 
            self.total_pyth_distance[run] = self.determineDistance(self.outcomes[[run]], self.status_quo[[run]], 'euclidean')
            self.total_manh_distance[run] = self.determineDistance(self.outcomes[[run]], self.status_quo[[run]], 'cityblock')

            # determine the distance travelled in each dimension and append to results
            self.dimension_distance[run] = np.column_stack([self.determineDistance(self.status_quo[[run]][None,:,dim], 
                                                      self.outcomes[[run]][None,:,dim], 
                                                      self.Variables.distance_type) for dim in range(self.Variables.number_dimensions)])
            
            # set the new status quo
            self.alterStatusQuo(self.outcomes[[run]])

            # set the players' new preferences
            self.alterPlayerPreferences()  
        print("--- %s seconds ---" % (time.time() - start_time))
        if self.Variables.visualize == True:
            logging.info('Visualizing results')
                                    
            self.Variables.figs = self.visualizeResults(self.Variables.directory)
            
        if self.Variables.save_results == True:
            logging.info('Saving results to CSV')
            
            self.saveResults()
            
        if any([self.Variables.randomize_as, self.Variables.randomize_veto, self.Variables.save_sequence]):
            self.saveRoleArray()

        logging.info("Simulation complete")
        
#        logging.info('Find results at ' + filename)
        
    def paintGrid(self, start, stop, breaks, break_decimal):
        '''
        Points are added at set intervals to a grid of a given size.
        '''
        logging.info('Creating Grid')
        try:
            start_r = [floor(strt * break_decimal) / break_decimal for strt in start]
            stop_r  = [ceil(stp * break_decimal) / break_decimal for stp in stop]
            bins = np.array([(stp - strt) / breaks for stp, strt in zip(stop_r, start_r)])
            bounds = np.array([[begin, end ] for begin, end in zip(start_r, stop_r)])
                    
            position = np.mgrid[[slice(row[0], row[1], n*1j) for row, n in zip(bounds, bins)]]
            position = position.reshape(self.Variables.number_dimensions, -1).T
            return position  

        except MemoryError:
            logging.error('Memory Error. Could not create grids // Try setting larger breaks')
            raise

    def pointsInWinset(self, random_points, status_quo, player):
        '''
        Function to determine which points fall inside preference circles of specified players.
        This function is first used to determine the optimum within each coalition, and then
        to determine the final outcome: the optimal point across all coalitions.
        '''
        logging.info('Calculating points in winset')
        
        radius = self.determineDistance(player, status_quo, self.Variables.distance_type).T
        
        distance = self.determineDistance(random_points, player, self.Variables.distance_type)

        index = np.where(np.all(np.greater_equal(radius, distance), axis = 1))[0]
        
        return random_points[index]
                
    
    def determineCoalitions(self, agenda_setter, veto_players, normal_voters):
        '''
        Determines which possible coalitions can form a majority. It checks how many more
        (if any) voters are needed besides the veto players and the agenda setter 
        (which are always required to vote for a proposal) and creates all possible combinations thereof.
        '''
        
        logging.info('Determining possible coalitions')
        
        # required voters: agenda setter and veto players
        required_voters = agenda_setter + veto_players
        print("voters-----------------")
        print(self.Variables.voters)
        # check if veto players and the agenda setter are a majority by themselves
        if len(required_voters) <= 0.5 * len(self.Variables.voters):
            print("coal need")
            #determine how many more voters are needed
            more_voters = ceil(0.5 * len(self.Variables.voters) + 1) - len(self.Variables.voters)%2 - len(required_voters)
#            more_voters = ceil(abs(0.5 * len(self.Variables.voters) - len(required_voters) - 1))
            
            if more_voters == 0:
                more_voters == 1
            print("more voters", more_voters)
            # the combinations of voters that can be added to the required voters to get a coalition
#            possible_coalitions = [list(coalition) + veto_players for coalition in itertools.combinations(normal_voters, more_voters)]           
            possible_coalitions = [list(coalition) for coalition in itertools.combinations(normal_voters, more_voters)]           
            print(possible_coalitions)
            print("----------------------------")
        # if VPs and agenda setter are already a majority, they are the only coalition
        else:
            possible_coalitions = []
    
        return possible_coalitions
    
    def closestToAgendaSetter(self, points_in_selection, as_index, run):
        '''
        This function determines which point from a given array is closest to the agenda setter. It takes all
        points that a have a theoretical majority; now the point is to determine which the AS likes most. This
        will be the most-preferred point and the outcome of the veto-player game. If there is no point that
        lies in the preference circles of all veto players and the agenda setter, this function returns the
        status quo.
        '''
        
        logging.info('Determining outcome')
        
        #if there are no points inside all preference circles, the outcome will be the status quo
        if points_in_selection.size == 0:
            preferred_point = self.Variables.status_quo
    
        else:
            # determine the distance of each eligible point to the agenda setter
            #TODO: This dist calc is double, store values from pointsInWinset and reuse?
            distance = self.determineDistance(points_in_selection, self.voter_position_array[as_index, run], 
                                              self.Variables.distance_type)
            
            # retrieve the index of minimum distance and get the actual point value
            index = np.where(distance == distance.min())

            # currently, only the first value is used. for games with 0 agenda setter better system needed
            preferred_point = points_in_selection[index[0][0]]
            
        return preferred_point
    
    
    def determineDistance(self, point1, point2, dist_type = 'euclidean'):  
        '''
        This function determines the distance between two points in any number of dimensions.
        As such, it can also be used to determine the radius of a preference circle (by inputting
        a point and the status quo).
        '''
        if point1.ndim == 1:
            point1 = point1[None, :]
            
        if point2.ndim == 1:
            point2 = point2[None, :]
          
        return dist.cdist(point1, point2, metric = dist_type)
        
              
    def alterStatusQuo(self, outcome):
        '''
        This function sets the status quo for the new simulation. Based on the parameters
        defined at the top of the document, a new value for the status quo is picked.
        '''
        
        logging.info('Altering Status Quo')
        
        # setting the appropriate vibration type
        vibration = self.setVibration()
    
        # if the status quo doesn't change there is still vibration
        if self.Variables.alter_status_quo == 'no':
            self.Variables.status_quo = self.Variables.status_quo + vibration
        
        # place a completely random status quo on the grid
        #TODO fix (0, WHAT)
        elif self.Variables.alter_status_quo == 'random':
            self.Variables.status_quo = np.random.uniform(0, 100, (1, self.Variables.number_dimensions)) + vibration
        
        # alter status quo based on outcome and vibration
        elif self.Variables.alter_status_quo == 'history':
            self.Variables.status_quo = outcome + vibration
            
        # alter status quo based on outcome of previous run, drift, and vibration
        elif self.Variables.alter_status_quo == 'history + drift':
            self.Variables.status_quo = outcome + vibration + self.Variables.drift_status_quo
        
            
    def alterPlayerPreferences(self):
        '''
        Function to alter the preferences of the players for every run. Two options: preferences
        do not change (yet there is some vibration), or preferences have a drift in a certain
        direction.
        '''
        
        logging.info('Altering player preferences')
            
        # there is always vibration
        for voter in self.Variables.normal_voters:
            voter.position = voter.position + self.setVibration()
        
        for voter in self.Variables.veto_players:
            voter.position = voter.position + self.setVibration()
            
        self.Variables.agenda_setter.position = self.Variables.agenda_setter.position + self.setVibration()
    
        if self.Variables.alter_preferences == 'drift':
            for voter in self.Variables.normal_voters:
                voter.position = voter.position + voter.drift
        
            for voter in self.Variables.veto_players:
                voter.position = voter.position + voter.drift
            
            self.Variables.agenda_setter.position = self.Variables.agenda_setter.position + self.Variables.agenda_setter.drift
    
    
    def roleAssignment(self, run):
        if self.Variables.randomize_as is True and self.Variables.randomize_veto is True:
            self.Variables.agenda_setter.agenda_setter = False
            for voter in self.Variables.veto_players:
                voter.veto_player = False
            
        if self.Variables.randomize_as is True:
            self.Variables.agenda_setter.agenda_setter = False
            
            new_agenda_setter = random.choice(
                    [voter for voter in self.Variables.voters if voter.veto_player is False])
            
            new_agenda_setter.agenda_setter = True
            
        if self.Variables.randomize_veto is True:
            for voter in self.Variables.veto_players:
                voter.veto_player = False

            veto_possibilities = []
            
            for i, _ in enumerate(self.Variables.voters):
                    if _.agenda_setter is False:
                        veto_possibilities.append(i)
                        
            num_veto_players = random.choice(range(len(veto_possibilities) + 1))
            
            new_veto_players =  random.sample(veto_possibilities, num_veto_players)
            
            for index, voter in enumerate(self.Variables.voters):
                if index in new_veto_players:
                    voter.veto_player = True
                else:
                    voter.veto_player = False 
    
        self.Variables.agenda_setter = [voter for voter in self.Variables.voters if voter.agenda_setter][0]
        self.Variables.veto_players = [voter for voter in self.Variables.voters if voter.veto_player]
        self.Variables.normal_voters = [voter for voter in self.Variables.voters if not voter.agenda_setter and not voter.veto_player]
          

    def visualizeResults(self, visualization_dir, animate = True):
        '''
        This function visualizes the results of the runs and saves them as png files in a specified folder
        '''
        #initialize array to find all axis limits for each dimension
        if self.Variables.number_dimensions == 1:
            vis_limits = np.zeros((2, 2))
        else:
            vis_limits = np.zeros((self.Variables.number_dimensions, 2))
                    
        #store filenames for gif creation
        filenames = []
        
        if self.Variables.number_dimensions == 1:
            
            vis_limits[0] = (
                    (self.voter_position_array - self.voter_radius_array)[:, :, 0].min(),
                    (self.voter_position_array + self.voter_radius_array)[:, :, 0].max()
                    )
            
            vis_limits[1] = (
                     0,
                    (self.voter_radius_array.max())
                    )
            
            for run in range(self.Variables.runs):
                
                fig = plt.figure(figsize = (20, 5), dpi = 80)

                ax = fig.add_subplot(111)
                ax.set_xlim(vis_limits[0, 0], vis_limits[0, 1])
                ax.set_ylim(vis_limits[1, 0], vis_limits[1, 1])

                #in role array, normal voter == 0, agenda setter == 1, veto player == 2
                if 0 in self.voter_role_array[:, run]:
                    
                    index = np.where(np.squeeze(np.isin(self.voter_role_array[:, run], 0)))[0]
                    
                    ax.scatter(self.voter_position_array[index, run], [0 for i in index],
                               s = 70, c = 'black', label = 'Voters', clip_on = False)

                    norm_patches = [Circle((xx, 0), rr) for xx, rr in zip(
                            self.voter_position_array[index, run], 
                            self.voter_radius_array[index, run])]
                    
                    norm_collection = PatchCollection(norm_patches, facecolors = 'grey', 
                                                      edgecolors = 'black', linewidths = 0.5, alpha = 0.2)
                    
                    ax.add_collection(norm_collection)
                    norm_collection.set_clip_box(ax.bbox)


                if 2 in self.voter_role_array[:, run]:
                    
                    index = np.where(np.squeeze(np.isin(self.voter_role_array[:, run], 2)))[0]

                    ax.scatter(self.voter_position_array[index, run], [0 for i in index],
                               s = 60, c = 'red', label = 'Veto Players', clip_on = False)
                    
                    veto_patches = [Circle((xx, 0), rr) for xx, rr in zip(
                            self.voter_position_array[index, run], 
                            self.voter_radius_array[index, run])]
                    
                    veto_collection = PatchCollection(veto_patches, facecolors = 'red', 
                                                      edgecolors = 'black', linewidths = 0.5, alpha = 0.2)
                    
                    ax.add_collection(veto_collection)
                    veto_collection.set_clip_box(ax.bbox)
                    
                index = np.where(np.squeeze(np.isin(self.voter_role_array[:, run], 1)))[0]
                
                ax.scatter(self.voter_position_array[index, run], 0, s = 60, c = 'lightblue', label = 'Agenda Setter', clip_on = False)

                as_patch = Circle((self.voter_position_array[index, run], 0), self.voter_radius_array[index, run],
                                   facecolor = 'blue', edgecolor = 'black', linewidth = 0.5, alpha = 0.2)                      
                    
                ax.add_artist(as_patch)
                as_patch.set_clip_box(ax.bbox)
                
                ax.scatter(self.status_quo[run], 0, s = 60, c = 'orange', label = 'Status Quo', clip_on = False)
                
                ax.scatter(self.outcomes[run], 0, s = 50, c = 'yellow', label = 'Outcome', clip_on = False)
    
                box = ax.get_position()
                
                ax.set_position([box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9])
                
                ax.legend(scatterpoints = 1, loc = 'upper center', shadow = 'True', bbox_to_anchor = (0.5, -0.05), ncol = 3, fancybox = True)
                
                ax.annotate('Run: ' + str(run+1), xy = (1, 1), xycoords = 'axes fraction')
        
                filename = ''.join((self.Variables.directory, '/', str(run), '.png'))
                
                fig.savefig(filename, bbox_inches = 'tight')
                                
                filenames.append(filename)
    
                plt.close('all')
                
    
        elif self.Variables.number_dimensions == 2:
            
            for dim in range(self.Variables.number_dimensions):
                
                vis_limits[dim] = (
                        (self.voter_position_array - self.voter_radius_array).min(),
                        (self.voter_position_array + self.voter_radius_array).max()
                        )
                            
            for run in range(self.Variables.runs):
                
                if self.Variables.trace_total_change is True:
                    fig, (ax, ax1) = plt.subplots(2, 1, gridspec_kw = {'height_ratios':[4, 1]})
                    fig.set_size_inches(10, 10)
                    fig.set_dpi(80)
                    ax1.plot(range(self.Variables.runs), self.total_pyth_distance, c = '#1f77b4')
                    ax1.scatter(run, self.total_pyth_distance[run], c = '#d62728', s = 40, clip_on = False)

                else:
                    fig = plt.figure(figsize = (18.5, 10.5), dpi = 80)
                    
                    ax = fig.add_subplot(111, aspect='equal')
                    
                ax.set_xlim(vis_limits[0, 0], vis_limits[0, 1])
                ax.set_ylim(vis_limits[1, 0], vis_limits[1, 1])
                
                #in role array, normal voter == 0, agenda setter == 1, veto player == 2
                if 0 in self.voter_role_array[:, run]:
                    
                    index = np.where(np.squeeze(np.isin(self.voter_role_array[:, run], 0)))[0]
                    
                    ax.scatter(
                            self.voter_position_array[index, run, 0], 
                            self.voter_position_array[index, run, 1],
                            s = 30, c = '#7f7f7f', label = 'Voters'
                            )
                    
                    norm_patches = [Circle((xx, yy), rr) for xx, yy, rr in zip(
                                    self.voter_position_array[index, run, 0],
                                    self.voter_position_array[index, run, 1],
                                    self.voter_radius_array[index, run])]
                                    
                    norm_collection = PatchCollection(norm_patches, facecolors = '#7f7f7f',
                                                      edgecolors = 'black', linewidths = 0.5, alpha = 0.2)
                                    
                    ax.add_collection(norm_collection)
                    norm_collection.set_clip_box(ax.bbox)
                    
                    
                if 2 in self.voter_role_array[:, run]:
                    
                    index = np.where(np.squeeze(np.isin(self.voter_role_array[:, run], 2)))[0]
                    
                    ax.scatter(self.voter_position_array[index, run, 0], 
                               self.voter_position_array[index, run, 1],
                               s = 30, c = '#d62728', label = 'Veto Players')
                    
                    veto_patches = [Circle((xx, yy), rr) for xx, yy, rr in zip(
                            self.voter_position_array[index, run, 0], 
                            self.voter_position_array[index, run, 1],
                            self.voter_radius_array[index, run])]

                    veto_collection = PatchCollection(veto_patches, facecolors = "#d62728", 
                                                      alpha = 0.2, linewidths = 0.5, edgecolors = "black")
                    
                    ax.add_collection(veto_collection)
                    veto_collection.set_clip_box(ax.bbox)
                    
                    
                index = np.where(np.squeeze(np.isin(self.voter_role_array[:, run], 1)))[0]
                ax.scatter(
                        self.voter_position_array[index, run, 0],
                        self.voter_position_array[index, run, 1],
                        s = 30, c = '#1f77b4', label = 'Agenda Setter'
                        )
                
                as_patch = Circle((
                        self.voter_position_array[index, run, 0],
                        self.voter_position_array[index, run, 1]),
                        self.voter_radius_array[index, run],
                        facecolor = '#1f77b4', edgecolor = 'black', linewidth = 0.5, alpha = 0.2
                        )

                ax.add_artist(as_patch)
                as_patch.set_clip_box(ax.bbox)
                
                ax.scatter(self.status_quo[run, 0], self.status_quo[run, 1], s = 35, c = '#8c564b', label = 'Status Quo')
                ax.scatter(self.outcomes[run, 0], self.outcomes[run, 1], s = 30, c = '#ff7f0e', label = 'Outcome')
                
                #trace status quo
                if self.Variables.trace is True:
                    lines = [mlines.Line2D([self.status_quo[run, 0], self.outcomes[run, 0]], 
                                           [self.status_quo[run, 1], self.outcomes[run, 1]],
                                           linewidth = 2, color = '#2ca02c', alpha = 1)]
                        
                    if run <= 4:
                        lines += [mlines.Line2D([self.status_quo[run - i - 1, 0], self.status_quo[run - i, 0]],
                                                [self.status_quo[run - i - 1, 1], self.status_quo[run - i, 1]],
                                                linewidth = 2, color = '#2ca02c', alpha = (0.8 - i * .2)) for i in range(run)]
                        
                    else: 
                        lines += [mlines.Line2D([self.status_quo[run - i - 1, 0], self.status_quo[run - i, 0]], 
                                               [self.status_quo[run - i - 1, 1], self.status_quo[run - i, 1]],
                                               linewidth = 2, color = '#2ca02c', alpha = (0.8 - i * .2)) for i in range(5)]
    
                    [ax.add_line(line) for line in lines]
                
            
                box = ax.get_position()
                
                ax.set_position([box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9])
                
                ax.legend(scatterpoints = 1, loc = 'upper center', shadow = 'True', bbox_to_anchor = (0.5, -0.05), ncol = 3, fancybox = True)
                
                ax.annotate("Run: " + str(run+1), xy = (1, 1), xycoords='axes fraction')
    
                filename = os.path.join(self.Variables.directory, "run" + str(run) + '.png')
                
                fig.savefig(filename, bbox_inches = 'tight')
                    
                filenames.append(filename)
                
                plt.close("all")
                
        elif self.Variables.number_dimensions == 3:
            from mpl_toolkits.mplot3d import Axes3D
            def drawSphere(xCenter, yCenter, zCenter, r):
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
                
                vis_limits[dim] = (
                        (self.voter_position_array - self.voter_radius_array)[:, :, dim].min(),
                        (self.voter_position_array + self.voter_radius_array)[:, :, dim].max()
                        )
            
            for run in range(self.Variables.runs):
            
                fig = plt.figure(figsize = (18.5, 10.5), dpi = 80)
                ax = fig.gca(projection='3d')
                ax.set_aspect("equal")
              
                ax.set_xlim(vis_limits[0, 0], vis_limits[0, 1])
                ax.set_ylim(vis_limits[1, 0], vis_limits[1, 1])
                ax.set_zlim(vis_limits[2, 0], vis_limits[2, 1])
                
                if 0 in self.voter_role_array[:, run]:                    
                    index = np.where(np.squeeze(np.isin(self.voter_role_array[:, run], 0)))[0]
                    
                    ax.scatter(
                            self.voter_position_array[index, run, 0], 
                            self.voter_position_array[index, run, 1],
                            self.voter_position_array[index, run, 2],
                            s = 40, c = '#7f7f7f', label = 'Voters'
                            )
                    
                    [ax.plot_wireframe(*drawSphere(xx, yy, zz, rr), color='#7f7f7f', linewidths = 1, alpha = 0.3) for xx, yy, zz, rr in zip(
                            self.voter_position_array[index, run, 0],
                            self.voter_position_array[index, run, 1],
                            self.voter_position_array[index, run, 2],
                            self.voter_radius_array[index, run])]
                    
                if 2 in self.voter_role_array[:, run]:
                    index = np.where(np.squeeze(np.isin(self.voter_role_array[:, run], 2)))[0]
                    
                    ax.scatter(self.voter_position_array[index, run, 0], 
                               self.voter_position_array[index, run, 1],
                               self.voter_position_array[index, run, 2],
                               s = 40, c = '#d62728', label = 'Veto Players')
                    
                    [ax.plot_wireframe(*drawSphere(xx, yy, zz, rr), color='#d62728', linewidths = 1, alpha = 0.3) for xx, yy, zz, rr in zip(
                            self.voter_position_array[index, run, 0],
                            self.voter_position_array[index, run, 1],
                            self.voter_position_array[index, run, 2],
                            self.voter_radius_array[index, run])]                   
                    
                index = np.where(np.squeeze(np.isin(self.voter_role_array[:, run], 1)))[0]
                
                ax.scatter(
                        self.voter_position_array[index, run, 0],
                        self.voter_position_array[index, run, 1],
                        s = 30, c = '#1f77b4', label = 'Agenda Setter'
                        )
                
                ax.plot_wireframe(*drawSphere(self.voter_position_array[index, run, 0], 
                                              self.voter_position_array[index, run, 1],
                                              self.voter_position_array[index, run, 2],
                                              self.voter_radius_array[index, run]), color = '#1f77b4', alpha = 0.3)
                
                ax.scatter(self.status_quo[run, 0], self.status_quo[run, 1], self.status_quo[run, 2], s = 55, c = '#8c564b', alpha = 1, label = 'Status Quo')
                ax.scatter(self.outcomes[run, 0], self.outcomes[run, 1], self.outcomes[run, 2], s = 50, c = '#ff7f0e', alpha = 1, label = 'Outcome')               
            
                if self.Variables.trace is True:     
                    line1 = [(self.status_quo[run, 0], self.outcomes[run, 0]),
                             (self.status_quo[run, 1], self.outcomes[run, 1]),
                             (self.status_quo[run, 2], self.outcomes[run, 2])]
                        
                    if run <= 4:
                        lines = [[(self.status_quo[run - i - 1, 0], self.status_quo[run - i, 0]),
                                  (self.status_quo[run - i - 1, 1], self.status_quo[run - i, 1]),
                                  (self.status_quo[run - i - 1, 2], self.status_quo[run - i, 2])] for i in range(run)]
                                  
                    else: 
                        lines = [[(self.status_quo[run - i - 1, 0], self.status_quo[run - i, 0]),
                                  (self.status_quo[run - i - 1, 1], self.status_quo[run - i, 1]),
                                  (self.status_quo[run - i - 1, 2], self.status_quo[run - i, 2])] for i in range(5)]
                        
                    ax.plot(*line1, alpha = 1, color = '#2ca02c')
                    for i, item in enumerate(lines):
                        ax.plot(item[0], item[1], item[2], color = '#2ca02c', alpha = (0.8 - i * .2))
    
                box = ax.get_position()
                
                ax.set_position([box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9])
                
                ax.legend(scatterpoints = 1, loc = 'upper center', shadow = 'True', bbox_to_anchor = (0.5, -0.05), ncol = 3, fancybox = True)
                
                ax.annotate('Run: ' + str(run+1), xy = (1, 1), xycoords = 'axes fraction')
    
                filename = os.path.join(self.Variables.directory, "run" + str(run) + '.png')
                
                fig.savefig(filename, bbox_inches = 'tight')
                    
                filenames.append(filename)
                
                plt.close('all')    
                            
        if animate is True:
            import imageio
            images = [imageio.imread(file) for file in filenames]
            imageio.mimsave(os.path.join(self.Variables.directory, 'animation.gif'), images, duration = 1 / 10)
            
            
    def saveResults(self):
        '''
        Save results to a csv file in specified directory.
        '''
        colnames = [y for x in [
                ['Voter ' + str(i + 1) + '-' + voter.name + '-ROLE'] + 
                ['Voter ' + str(i + 1) + '-' + voter.name + '-DIM-' + str(dim + 1) for dim in range(self.Variables.number_dimensions)] +
                ['Voter ' + str(i + 1) + '-' + voter.name + '-RADIUS'] for i, voter in enumerate(self.Variables.voters)] for y in x] +\
                ['Status Quo' + '-DIM ' + str(dim + 1) for dim in range(self.Variables.number_dimensions)]+\
                ['Outcome' + '-DIM ' + str(dim + 1) for dim in range(self.Variables.number_dimensions)]+\
                ['Total Euclidean Distance', 'Total Manhattan Distance']+\
                ['Distance' + '-dim ' + str(dim + 1) for dim in range(self.Variables.number_dimensions)]+\
                ['Number Veto Players', 'Number Normal Voters']
        #data
        data = np.column_stack([np.column_stack((self.voter_role_array[i],
                                                  self.voter_position_array[i], 
                                                  self.voter_radius_array[i])) for i in range(len(self.Variables.voters))] +\
                [self.status_quo,
                self.outcomes,
                self.total_pyth_distance,
                self.total_manh_distance,
                self.dimension_distance,
                np.sum(np.column_stack((self.voter_role_array)) == 2, axis = 1, keepdims = True), 
                np.sum(np.column_stack((self.voter_role_array)) == 0, axis = 1, keepdims = True)])
                
        dataframe = DataFrame(data = data, columns = colnames)
   
        # setting up filename and folder
        timestr = time.strftime("%Y-%m-%d_%H%M")
        
        filename = ''.join(('results', '-', str(self.Variables.runs), 'r-', str(self.Variables.number_dimensions), 'd-', '__', timestr, '.csv'))
        
        csv_path = os.path.join(self.Variables.directory, filename)
    
        dataframe.to_csv(csv_path)
    
        return filename
    
    def saveRoleArray(self):
        import json
        out = {}
        out['sequence'] = self.voter_role_array.tolist()
        
        with open(os.path.join(self.Variables.directory, 'voter_sequence.txt'), 'w') as outfile:
            json.dump(out, outfile)
        

    #----------------------------------------------------------------------------------------------------#
    
    def setVibration(self):
        '''
        This function picks the appropriate distribution to draw from
        for the vibration of players and status quo.
        '''
        if self.Variables.distribution_type == 'normal':
            return self.randomNormal()
        
        elif self.Variables.distribution_type == 'uniform':
            return self.randomUniform()
        
        elif self.Variables.distribution_type == 'exponential':
            return self.randomExponential()
        
        elif self.Variables.distribution_type == 'paretian':
            return self.randomPareto()
    
    #----------------------------------------------------------------------------------------------------#   
    #draws from specified distribution
    def randomNormal(self):
        return np.random.normal(-0.2, 0.2)
    
    def randomUniform(self):
        return np.random.uniform(low = -5.0, high = 5.0, size = self.Variables.number_dimensions)
    
    def randomExponential(self):
        return np.random.exponential(scale = 1.0)
    
    def randomPareto(self):
        return np.random.pareto(5)

#----------------------------------------------------------------------------------------------------#

# running the simulation
    def run(self):
        try:

            self.simulation()
            
#            if self.Variables.visualize is True:
#                logging.info('Displaying Drawer')
#                drawer.main(self.Variables.figs)

            if self.Variables.animate is True:
                logging.info('Displaying Animation')
                vb_animation_drawer.main(os.path.join(self.Variables.directory, 'animation.gif')) 
            
        except:
            raise