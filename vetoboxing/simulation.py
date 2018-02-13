"""""""""
"" vetoboxing.py
"" This script is designed to run a simulation of veto player voting processes.
"""""""""
# ----------------------------------------------------------------------------------------------------#
import os
import time
import logging
from pandas import DataFrame
import numpy as np
from itertools import combinations
from math import floor, ceil
from collections import namedtuple

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon
from matplotlib.collections import PatchCollection
import matplotlib.lines

from shapely.geometry import Point, LinearRing
from scipy.spatial import distance as dist
from scipy.spatial import ConvexHull
import copy

# logging.basicConfig(filename = "vblog.log", level = logging.DEBUG)

class Simulation:
    def __init__(self, variables, visualization=None, parent=None):

        self.custom_position_array_set = False
        
        self.parent = parent
        #self.parent.logWidget.log.append("log3")

        self.variables = variables
        
        if visualization is None:
            visualization_options = namedtuple("visualization_options",
                                               "normal_voter_maincolor", "normal_voter_circlecolor", "normal_voter_size",
                                               "normal_voter_opacity", "normal_voter_linewidth", "veto_player_maincolor",
                                               "veto_player_circlecolor", "veto_player_size", "veto_player_opacity",
                                               "veto_player_linewidth", "agenda_setter_maincolor", "agenda_setter_circlecolor",
                                               "agenda_setter_size", "agenda_setter_opacity", "agenda_setter_linewidth",
                                               "trace_linewidth", "trace_line_opacity", "trace_line_maincolor", "winset_linewidth",
                                               "winset_opacity", "winset_maincolor", "trace_status_quo", "plot_total_change",
                                               "plot_role_array")
            
            visualization = visualization_options(normal_voter_maincolor = "#7f7f7f", normal_voter_circlecolor = "#7f7f7f",
                                                  normal_voter_size = 30, normal_voter_opacity = 0.2, normal_voter_linewidth = 0.5,
                                                  veto_player_maincolor = "#d62728", veto_player_circlecolor = "#d62728",
                                                  veto_player_size = 30, veto_player_opacity = 0.2, veto_player_linewidth = 0.5,
                                                  agenda_setter_maincolor = "#1f77b4", agenda_setter_circlecolor = "#1f77b4",
                                                  agenda_setter_size = 30, agenda_setter_opacity = 0.2, agenda_setter_linewidth = 0.5,
                                                  trace_linewidth = 2, trace_line_opacity = 0.5, trace_line_maincolor = "#2ca02c",
                                                  winset_linewidth = 0.5, winset_opacity = 0.7, winset_maincolor = "red",
                                                  trace_status_quo = "Yes", plot_total_change = "No", plot_role_array = "No")
        else:
            self.visualization = visualization
#        self.variables.custom_role_array = False  # TODO implement this

        """Initialize Voter Arrays"""
        if self.variables.custom_position_array is None:
            print("CUSTOM ARRAY NONE")
            self.voter_position_array = np.zeros(
                (self.variables.votercount, self.variables.runs, self.variables.dimensions))

            if not self.variables.alter_preferences == "drift":
                for i, voter in enumerate(self.variables.voter_positions):
                    self.voter_position_array[i] = voter
            else:
                self.voter_position_array[:, 0, :] = self.variables.voter_positions
        else:
            print("CUSTOM ARRAY NOT NONE")
            self.voter_position_array = self.variables.custom_position_array
            self.custom_position_array_set = True

        self.voter_radius_array = np.zeros((self.variables.runs, self.variables.votercount))

        if self.variables.custom_role_array is not None:
            self.voter_role_array = np.array(self.variables.custom_role_array)
        else:
            if self.variables.random_veto_player and not self.variables.random_agenda_setter:
                self.voter_role_array = np.random.choice([0, 1], size=(self.variables.runs, self.variables.votercount))
                
                self.voter_role_array[np.arange(self.voter_role_array.shape[0]), self.variables.voter_roles.index(2)] = 2

            elif self.variables.random_agenda_setter and not self.variables.random_veto_player:
                self.voter_role_array = np.repeat(np.array([self.variables.voter_roles]), self.variables.runs, axis=0)
                
                self.voter_role_array[np.arange(self.voter_role_array.shape[0]),
                                      np.random.choice(np.where(self.voter_role_array[0] != 1)[0],
                                                       size=(self.voter_role_array.shape[0],))] = 2

            elif self.variables.random_veto_player and self.variables.random_agenda_setter:
                self.voter_role_array = np.random.choice([0, 1], size=(self.variables.runs, self.variables.votercount))
                """set agenda setter at random index per row, np.arange to index all rows"""
                self.voter_role_array[np.arange(self.voter_role_array.shape[0]),
                                      np.random.choice(np.arange(self.voter_role_array.shape[1]),
                                                       size=(self.voter_role_array.shape[0],))] = 2

            else:
                self.voter_role_array = np.repeat(np.array([self.variables.voter_roles]), self.variables.runs, axis=0)

        """Initialize SQ, Outcome, Dist Arrays"""
        self.statusquo = np.zeros((self.variables.runs, self.variables.dimensions))
        self.statusquo[0] = self.variables.statusquo_position

        self.outcomes = np.zeros((self.variables.runs, self.variables.dimensions))
        self.dimension_distance = np.zeros((self.variables.runs, self.variables.dimensions))

        self.total_pyth_distance = np.zeros((self.variables.runs, 1))
        self.total_manh_distance = np.zeros((self.variables.runs, 1))

        self.break_decimal = pow(10, str(self.variables.breaks)[::-1].find("."))

        if self.variables.method == "random grid":
            #            self.seed = np.random.randint(low = 0, high = 100, size = 1).item()
            #            np.random.seed(self.seed)
            self.seeds = []
            self.start = []
            self.stop  = []

        """if shapely, initialize shapely objects for each voter"""
        if self.variables.method == "optimization":
            self.winset_patches = []
            self.winset_centroids = []
            self.winset_rads = []

            #            self.voterPoints = [Point(position) for position in self.Variables.voterPositions[:, 0, :]]
            #            self.voterCircles = [point.buffer(point.distance(self.statusQuo[0])) for point in self.voterPoints]

    def simulation(self):
        """explain"""
        for run in range(self.variables.runs):
            print("run nr {0} running".format(str(run + 1)))

            """get indexes for all roles for specific run"""
            agenda_setter_index = np.where(self.voter_role_array[run, :] == 2)[0]
            veto_player_index = np.where(self.voter_role_array[run, :] == 1)[0]
            normal_player_index = np.where(self.voter_role_array[run, :] == 0)[0]

            """calculate run radius for all voters and update radius array"""
            self.voter_radius_array[run, agenda_setter_index] = self.determine_distance(
                self.voter_position_array[agenda_setter_index, run],
                self.statusquo[[run]], self.variables.distance_type)

            if veto_player_index.any():
                self.voter_radius_array[run, veto_player_index] = self.determine_distance(
                    self.statusquo[[run]], self.voter_position_array[veto_player_index, run], self.variables.distance_type)

            if normal_player_index.any():
                self.voter_radius_array[run, normal_player_index] = self.determine_distance(
                    self.statusquo[[run]], self.voter_position_array[normal_player_index, run], self.variables.distance_type)

            """check if agenda setter position == status quo position, in which case the outcome is predetermined"""
            if (self.voter_position_array[agenda_setter_index, run] == self.statusquo[run]).all():
                self.outcomes[run] = self.statusquo[run]
                self.total_pyth_distance[run] = 0
                self.total_manh_distance[run] = 0
                self.dimension_distance[run] = [0 for _ in range(self.variables.dimensions)]
                if self.variables.runs > 1 and run != self.variables.runs - 1:
                    self.alter_statusquo(run)
                    self.alter_player_preferences(run)
                continue

            """determine possible coalitions given a selected majority rule -- coalitions necessarily include veto players and agenda setter"""
            possible_coalitions = self.determine_coalitions(agenda_setter_index, veto_player_index, normal_player_index)
            # TODO from coalition grid search to function
            possible_outcomes = []

            """grid search"""
            if self.variables.method == "grid" or self.variables.method == "random grid":
                """grid index to make grid a square around agenda setter radius"""
                grid_index = [[self.voter_position_array[agenda_setter_index, run].item(dim) - self.voter_radius_array[
                    run, agenda_setter_index].item(0) for
                               dim in range(self.variables.dimensions)],
                              [self.voter_position_array[agenda_setter_index, run].item(dim) +
                               self.voter_radius_array[run, agenda_setter_index].item(0) for dim in
                               range(self.variables.dimensions)]]

                if self.variables.method == "grid":
                    point_grid = self.grid_paint(*grid_index, self.variables.breaks, self.break_decimal)
                else:
                    point_grid = self.random_grid_paint(*grid_index)

                """exclude points that are outside of agenda setter and veto player winsets"""
                point_grid = self.grid_points_in_winset(point_grid, self.statusquo[[run]],
                                                        self.voter_position_array[agenda_setter_index, run])
                point_grid = self.grid_points_in_winset(point_grid, self.statusquo[[run]],
                                                        self.voter_position_array[veto_player_index, run])

                if possible_coalitions:
                    """select outcomes for all coalitions"""
                    for coalition in possible_coalitions:
                        points_in_winset = self.grid_points_in_winset(point_grid, self.statusquo[[run]],
                                                                      np.vstack(
                                                                          [self.voter_position_array[coalition, run]]))
                        possible_outcome = self.grid_closest_to_agenda_setter(points_in_selection=points_in_winset,
                                                                              as_index=agenda_setter_index, run=run)
                        possible_outcomes.append(possible_outcome)

                else:
                    possible_outcomes.append(self.grid_closest_to_agenda_setter(point_grid, agenda_setter_index, run))

                if len(possible_outcomes) > 1:
                    possible_outcomes = np.vstack([item for item in possible_outcomes])
                    """select outcome closest to agenda setter"""
                    outcome = self.grid_closest_to_agenda_setter(possible_outcomes, agenda_setter_index, run)
                    self.outcomes[run] = outcome
                else:
                    self.outcomes[run] = possible_outcomes[0]

            
            else:
                statusquo_point = Point(self.statusquo[run])
                voter_points = [Point(position) for position in self.voter_position_array[:, run, :]]
                voter_circles = [point.buffer(point.distance(statusquo_point)) for point in voter_points]

                winsets = []
                if possible_coalitions:
                    for coalition in possible_coalitions:
                        intersection = voter_circles[agenda_setter_index.item()]
                        #                        intersection = [voter_circles[index] for index in agendaSetterIndex][0]

                        for voter in coalition + veto_player_index.tolist():
                            #                            intersection = intersection.intersection(voter_circles[voter])
                            intersection = intersection.intersection([voter_circles[index] for index in [voter]][0])

                        winsets.append(intersection)

                else:
                    intersection = voter_circles[agenda_setter_index.item()]

                    for voter in veto_player_index:
                        #                        intersection = intersection.intersection(voter_circles[voter])
                        intersection = intersection.intersection([voter_circles[index] for index in [voter]][0])

                    winsets.append(intersection)

                agenda_setter_overlap = False
                closest_points = []

                for i, winset in enumerate(winsets):
                    if winset.area > 0:
                        if winset.contains(voter_points[agenda_setter_index[0]]):
                            closest_points.append(voter_points[agenda_setter_index[0]])
                            min_index = i
                            agenda_setter_overlap = True
                            break
                        pol_ext = LinearRing(winset.exterior.coords)
                        #d = polExt.project(voter_points[agendaSetterIndex])
                        d = pol_ext.project([voter_points[index] for index in agenda_setter_index][0])
                        p = pol_ext.interpolate(d)
                        closest_point = p.coords[0]
                        closest_points.append(closest_point)

                    else:
                        closest_points.append(self.statusquo[run].tolist())

                if agenda_setter_overlap:
                    self.outcomes[run] = closest_points[0]
                                        
                else:
                    closest_points_distances = [
                        self.determine_distance(self.voter_position_array[agenda_setter_index, run], np.array([point])) for
                        point
                        in closest_points]
                    min_index = np.argmin(closest_points_distances)
                    self.outcomes[run] = closest_points[min_index]

                if self.variables.visualize:
                    if np.any(self.outcomes[run] != self.statusquo[run]): #any vs all ? 
                        self.winset_patches.append(
                            PatchCollection([Polygon(winsets[min_index].exterior)], facecolor="red", linewidth=.5,
                                            alpha=.7))

                    else:
                        self.winset_patches.append(None)
                        self.winset_rads.append(None)
                        self.winset_centroids.append(None)

            """determine distances travelled in run"""
            self.total_pyth_distance[run] = self.determine_distance(self.outcomes[[run]], self.statusquo[[run]])
            self.total_manh_distance[run] = self.determine_distance(self.outcomes[[run]], self.statusquo[[run]], "cityblock")

            self.dimension_distance[run] = np.column_stack([self.determine_distance(self.statusquo[[run]][None, :, dim],
                                                                                    self.outcomes[[run]][None, :, dim],
                                                                                    self.variables.distance_type) for dim
                                                            in range(self.variables.dimensions)])

            """alter status quo and preferences"""
            if self.variables.runs > 1 and run != self.variables.runs - 1:
                self.alter_statusquo(run)
                # original passed on "self.outcomes[[run]])"
                if not self.custom_position_array_set:
                    self.alter_player_preferences(run)

                #        if self.Variables.visualize:
                #            self.visualizeResults()

        if self.variables.save.lower() == 'yes':
            self.save_results()

        if any([self.variables.random_veto_player, self.variables.random_agenda_setter]):
            self.save_role_array()

    def determine_coalitions(self, agenda_setter, veto_players, normal_voters):
        """
        Determines which possible coalitions can form a majority. It checks how many more
        (if any) voters are needed besides the veto players and the agenda setter 
        (which are always required to vote for a proposal) and creates all possible combinations thereof
        """
        required_voters = agenda_setter.tolist() + veto_players.tolist()
        # check if veto players and the agenda setter are a majority by themselves
        if len(required_voters) <= 0.5 * self.variables.votercount:
            # determine how many more voters are needed
            more_voters = ceil(0.5 * self.variables.votercount + 1) - self.variables.votercount % 2 - len(
                required_voters)

            possible_coalitions = [list(coalition) for coalition in combinations(normal_voters, more_voters)]
            # if VPs and agenda setter are already a majority, they are the only coalition
        else:
            possible_coalitions = []

        return possible_coalitions

    @staticmethod
    def determine_distance(point1, point2, distance_type="euclidean"):
        """
        Determine the distance between two points in any number of dimensions.
        As such, it can also be used to determine the radius of a preference circle (by inputting
        a point and the status quo).
        """
        if distance_type == "manhattan":
            distance_type = "cityblock" #TODO fix this in namespace
        return dist.cdist(point1, point2, metric=distance_type)

    def grid_paint(self, start, stop, breaks, break_decimal):
        """
        Points are added at set intervals to a grid of a given size.
        """
        try:
            start_r = [floor(strt * break_decimal) / break_decimal for strt in start]
            stop_r = [ceil(stp * break_decimal) / break_decimal for stp in stop]
            bins = np.array([(stp - strt) / breaks for stp, strt in zip(stop_r, start_r)])
            bounds = np.array([[begin, end] for begin, end in zip(start_r, stop_r)])
            position = np.mgrid[[slice(row[0], row[1], n * 1j) for row, n in zip(bounds, bins)]]
            position = position.reshape(self.variables.dimensions, -1).T
            return position

        except MemoryError:
            logging.error("Memory Error. Could not create grids // Try setting larger breaks")
            raise

    def random_grid_paint(self, start, stop):
        """
        Points are added randomly and with a given density, simulating information incompleteness
        """
        try:
            seed = np.random.randint(low=0, high=2 ** 21 - 1, size=1).item()

            self.seeds.append(seed)
            self.start.append(start)
            self.stop.append(stop)

            np.random.seed(seed)
            point_count = ceil((self.variables.density ** self.variables.dimensions) * abs(start[0] - stop[0]))
#            x = np.random.uniform(low=start[0], high=stop[0], size=((point_count, 1)))
#            y = np.random.uniform(low=start[1], high=stop[1], size=((point_count, 1)))
            grid = np.column_stack([np.random.uniform(low = start[dim], high = stop[dim], size = ((point_count, 1))) for
                                    dim in range(self.variables.dimensions)])
            return grid

        except MemoryError:
            raise

    def grid_points_in_winset(self, random_points, status_quo, player):
        """
        Function to determine which points fall inside preference circles of specified players.
        This function is first used to determine the optimum within each coalition, and then
        to determine the final outcome: the optimal point across all coalitions.
        """
        radius = self.determine_distance(player, status_quo, self.variables.distance_type).T
        distance = self.determine_distance(random_points, player, self.variables.distance_type)
        index = np.where(np.all(np.greater_equal(radius, distance), axis=1))[0]
        return random_points[index]

    def grid_closest_to_agenda_setter(self, points_in_selection, as_index, run):
        """
        This function determines which point from a given array is closest to the agenda setter. It takes all
        points that a have a theoretical majority; now the point is to determine which the AS likes most. This
        will be the most-preferred point and the outcome of the veto-player game. If there is no point that
        lies in the preference circles of all veto players and the agenda setter, this function returns the
        status quo.
        """
        # if there are no points inside all preference circles, the outcome will be the status quo
        if not points_in_selection.any():
            preferred_point = self.statusquo[run].tolist()
        else:
            # determine the distance of each eligible point to the agenda setter
            # TODO: This dist calc is double, store values from points_in_winset and reuse?
            distance = self.determine_distance(points_in_selection, self.voter_position_array[as_index, run],
                                               self.variables.distance_type)
            # retrieve the index of minimum distance and get the actual point value
            index = np.where(distance == distance.min())
            # currently, only the first value is used. for games with 0 agenda setter better system needed
            preferred_point = np.array([points_in_selection[index[0][0]]])

        return preferred_point

    def alter_statusquo(self, run):
        """
        Set the status quo for the new simulation based on alterStatusQuo and vibration distribution
        """
        #status quo is constant throughout.
        if self.variables.alter_statusquo == "no":
            self.statusquo[run + 1] = self.statusquo[run]

        # place a completely random status quo on the grid
        # TODO fix to only SQ in winset
        elif self.variables.alter_statusquo == "random":
            self.statusquo[run + 1] = np.random.uniform(0, 100, (1, self.variables.dimensions))

        # alter status quo based on outcome
        elif self.variables.alter_statusquo == "history":
            self.statusquo[run + 1] = self.outcomes[run]

        # alter status quo based on outcome of previous run, drift
        elif self.variables.alter_statusquo == "history+drift":
            self.statusquo[run + 1] = self.outcomes[run] + self.variables.statusquo_drift

        if self.variables.vibrate_sq is True:
            self.statusquo[run + 1] += self.set_vibration(self.statusquo[run].shape)
            

    def alter_player_preferences(self, run):
        """
        Function to alter the preferences of the players for every run. Two options: preferences
        do not change (yet there is some vibration), or preferences have a drift in a certain
        direction.
        """
        if self.variables.alter_preferences == "random_drift":
            self.voter_position_array[:, run + 1, :] = self.voter_position_array[:, run, :] + self.set_vibration(
                size=self.voter_position_array[:, run, :].shape)

        if self.variables.alter_preferences == "drift":
            pass
#            self.voter_position_array[:, run + 1, :] = self.voter_position_array[:, run, :] + self.variables.voterDrift

    def visualize_init(self, animate=True, save=False):
        """
        Initialize Figure + Axis
        """
        """""""Initialize ax lim array"""""""
        if self.variables.dimensions == 1:
            self.visualize_limits = np.zeros((2, 2))
        else:
            self.visualize_limits = np.zeros((self.variables.dimensions, 2))

        if animate:
            filenames = []

        if self.variables.dimensions == 1:
            """""""""
            1D Figure
            """""""""
            self.visualize_limits[0] = ((self.voter_position_array - self.voter_radius_array.
                                 reshape((self.variables.votercount, self.variables.runs, 1))).min(),
                                        (self.voter_position_array + self.voter_radius_array).max())
            self.visualize_limits[1] = (0, self.voter_radius_array.max())

            if save is True:
                fig = plt.figure(figsize=(20, 5))
                ax = fig.add_subplot(111)
                for run in range(self.variables.runs):
                    self.visualize_draw_on_axis(1, ax, run, self.visualize_limits)

                    filename = os.path.join(self.variables.directory, "run" + str(run) + ".png")
                    fig.savefig(filename, bbox_inches="tight")

                    if animate:
                        filenames.append(filename)

                plt.close(fig)

        elif self.variables.dimensions == 2:
            """""""""
            2D Figure
            """""""""
            for dim in range(self.variables.dimensions):
                self.visualize_limits[dim] = ((self.voter_position_array - self.voter_radius_array.
                                     reshape((self.variables.votercount, self.variables.runs, 1))).min(),
                                              (self.voter_position_array + self.voter_radius_array.
                                               reshape((self.variables.votercount, self.variables.runs, 1))).max())

            if save is True:
                if self.visualization.plot_total_change.lower() == "yes":
                    fig, (ax, ax1) = plt.subplots(2, 1, gridspec_kw={"height_ratios": [4, 1]})
                    fig.set_size_inches(10, 10)
                    fig.set_dpi(80)
 
                else:
                    fig = plt.figure(figsize=(18.5, 10.5))
                    ax = fig.add_subplot(111, aspect="equal")

                for run in range(self.variables.runs):
                    print("Saving figure " + str(run+1) + "/" + str(self.variables.runs))
                    self.visualize_draw_on_axis(2, ax, run, self.visualize_limits)
                    
                    if self.visualization.plot_total_change.lower() == "yes":
                        self.visualize_total_change(ax1, run)

                    filename = os.path.join(self.variables.directory, "run" + str(run) + ".png")
                    fig.savefig(filename, bbox_inches="tight")

                    if animate:
                        filenames.append(filename)

                plt.close(fig)

        elif self.variables.dimensions == 3:
            """""""""
            3D Figure
            """""""""

            from mpl_toolkits.mplot3d import Axes3D

            def draw_sphere(x_center, y_center, z_center, r):
                # draw sphere
                u, v = np.mgrid[0:2 * np.pi:20j, 0:np.pi:10j]
                x = np.cos(u) * np.sin(v)
                y = np.sin(u) * np.sin(v)
                z = np.cos(v)
                # shift and scale sphere
                x = r * x + x_center
                y = r * y + y_center
                z = r * z + z_center
                return (x, y, z)

            for dim in range(self.variables.dimensions):
                self.visualize_limits[dim] = ((self.voter_position_array - self.voter_radius_array)[:, :, dim].min(),
                                              (self.voter_position_array + self.voter_radius_array)[:, :, dim].max())

    def visualize_total_change(self, ax, run):
        ax.clear()
        ax.plot(range(self.variables.runs), self.total_pyth_distance, c="#1f77b4")
        ax.scatter(run, self.total_pyth_distance[run], c="#d62728", s=20, clip_on=False)
                       
    def visualize_draw_on_axis(self, dim, ax, run, lims, fromUI=False):
        """
        Clear and then plot on given axis
        """
        print("plot fig" + str(run))
        ax.clear()

        if dim == 1:
            """
            1D
            """
            ax.set_xlim(lims[0, 0], lims[0, 1])
            ax.set_ylim(lims[1, 0], lims[1, 1])
            
            """draw random grid points"""
            if self.variables.method == "random grid":
                    np.random.seed(self.seeds[run])
                    point_count = ceil(
                        (self.variables.density ** self.variables.dimensions) * abs(self.start[run][0] - self.stop[run][0]))
                    x = np.random.uniform(low=self.start[run][0], high=self.stop[run][0], size=(point_count, 1))
                    ax.scatter(x, [0 for _ in range(x.size)], s=15, c="#3A3238")
                               
            # in role array, normal voter == 0, agenda setter == 1, veto player == 2
            if 0 in self.voter_role_array[run]:
                index = np.where(np.squeeze(np.isin(self.voter_role_array[run], 0)))[0]

                ax.scatter(self.voter_position_array[index, run], [0 for i in index],
                           s=self.visualization.normal_voter_size, 
                           c=self.visualization.normal_voter_maincolor, 
                           label="Voters", clip_on=False)

                norm_patches = [Circle((xx, 0), rr) for xx, rr in
                                zip(self.voter_position_array[index, run], self.voter_radius_array[run, index])]

                norm_collection = PatchCollection(norm_patches, 
                                                  facecolors=self.visualization.normal_voter_circlecolor, 
                                                  edgecolors="black", linewidths=0.5, 
                                                  alpha=self.visualization.veto_player_opacity)

                ax.add_collection(norm_collection)
                norm_collection.set_clip_box(ax.bbox)

            if 1 in self.voter_role_array[run]:
                index = np.where(np.squeeze(np.isin(self.voter_role_array[run], 1)))[0]

                ax.scatter(self.voter_position_array[index, run], [0 for _ in index], 
                           s=self.visualization.veto_player_size, c=self.visualization.veto_player_maincolor,
                           label="Veto Players",
                           clip_on=False)

                veto_patches = [Circle((xx, 0), rr) for xx, rr in
                                zip(self.voter_position_array[index, run], self.voter_radius_array[run, index])]

                veto_collection = PatchCollection(veto_patches, 
                                                  facecolors=self.visualization.veto_player_circlecolor, 
                                                  edgecolors="black", linewidths=0.5,
                                                  alpha=self.visualization.veto_player_opacity)

                ax.add_collection(veto_collection)
                veto_collection.set_clip_box(ax.bbox)

            index = np.where(np.squeeze(np.isin(self.voter_role_array[run], 2)))[0]

            ax.scatter(self.voter_position_array[index, run], 0, 
                       s=self.visualization.agenda_setter_size, 
                       c=self.visualization.agenda_setter_maincolor, label="Agenda Setter",
                       clip_on=False)

            as_patch = Circle((self.voter_position_array[index, run], 0), self.voter_radius_array[run, index],
                              facecolor=self.visualization.agenda_setter_circlecolor, 
                              edgecolor="black", linewidth=0.5, alpha=self.visualization.agenda_setter_opacity)

            ax.add_artist(as_patch)
            as_patch.set_clip_box(ax.bbox)

            ax.scatter(self.statusquo[run], 0, s=60, c="orange", label="Status Quo", clip_on=False)

            ax.scatter(self.outcomes[run], 0, s=50, c="yellow", label="Outcome", clip_on=False)

            ax.legend(scatterpoints=1, loc="upper center", shadow="True", bbox_to_anchor=(0.5, -0.05), ncol=3,
                      fancybox=True)

            ax.annotate("Run: " + str(run + 1), xy=(1, 1), xycoords="axes fraction")

        elif dim == 2:
            """
            2D
            """
            ax.set_xlim(lims[0, 0], lims[0, 1])
            ax.set_ylim(lims[1, 0], lims[1, 1])

            if self.variables.method == "random grid":
                np.random.seed(self.seeds[run])
                point_count = ceil(
                    (self.variables.density ** self.variables.dimensions) * abs(self.start[run][0] - self.stop[run][0]))
                x = np.random.uniform(low=self.start[run][0], high=self.stop[run][0], size=(point_count, 1))
                y = np.random.uniform(low=self.start[run][1], high=self.stop[run][1], size=(point_count, 1))
                grid = np.column_stack([x, y])
                ax.scatter(grid[:, 0], grid[:, 1], s=15, c="#3A3238")

            if 0 in self.voter_role_array[run]:
                """
                plot normal voters
                """
                index = np.where(np.squeeze(self.voter_role_array[run] == 0))[0]

                ax.scatter(self.voter_position_array[index, run, 0], self.voter_position_array[index, run, 1], 
                           s=self.visualization.normal_voter_size,
                           c=self.visualization.normal_voter_maincolor, label="Voters", zorder=100)

                norm_patches = [Circle((xx, yy), rr) for xx, yy, rr in zip(self.voter_position_array[index, run, 0],
                                                                           self.voter_position_array[index, run, 1],
                                                                           self.voter_radius_array[run, index])]

                norm_collection = PatchCollection(norm_patches, 
                                                  facecolors=self.visualization.normal_voter_circlecolor, 
                                                  edgecolors="black",
                                                  linewidths=0.5, alpha=self.visualization.normal_voter_opacity)

                ax.add_collection(norm_collection)
                norm_collection.set_clip_box(ax.bbox)

            if 1 in self.voter_role_array[run]:
                """
                plot veto players
                """
                index = np.where(np.squeeze(self.voter_role_array[run] == 1))[0]

                ax.scatter(self.voter_position_array[index, run, 0], self.voter_position_array[index, run, 1],
                           s=self.visualization.veto_player_size, 
                           c=self.visualization.veto_player_maincolor, label="Veto Players", zorder=100)

                veto_patches = [Circle((xx, yy), rr) for xx, yy, rr in zip(
                    self.voter_position_array[index, run, 0],
                    self.voter_position_array[index, run, 1],
                    self.voter_radius_array[run, index])]

                veto_collection = PatchCollection(veto_patches, facecolors=self.visualization.veto_player_circlecolor,
                                                  alpha=self.visualization.veto_player_opacity, linewidths=0.5, edgecolors="black")

                ax.add_collection(veto_collection)
                veto_collection.set_clip_box(ax.bbox)

            """
            plot agenda setter
            """
            index = np.where(np.squeeze(self.voter_role_array[run] == 2))[0]
            ax.scatter(self.voter_position_array[index, run, 0], self.voter_position_array[index, run, 1],
                       s=self.visualization.agenda_setter_size, 
                       c=self.visualization.agenda_setter_maincolor, label="Agenda Setter", zorder=100)

            as_patch = Circle((
                self.voter_position_array[index, run, 0],
                self.voter_position_array[index, run, 1]),
                self.voter_radius_array[run, index],
                facecolor=self.visualization.agenda_setter_circlecolor, 
                edgecolor="black", linewidth=0.5, alpha=self.visualization.agenda_setter_opacity)

            ax.add_artist(as_patch)
            as_patch.set_clip_box(ax.bbox)

            """
            plot status quo and outcome
            """
            ax.scatter(self.statusquo[run, 0], self.statusquo[run, 1], s=35, c="#8c564b", label="Status Quo", zorder = 100)
            ax.scatter(self.outcomes[run, 0], self.outcomes[run, 1], s=30, c="#ff7f0e", label="Outcome", zorder = 100)

            """add precise winset patch"""
            if self.variables.method == "optimization" and self.winset_patches[run] is not None:
                if not fromUI:
                    ax.add_collection(self.winset_patches[run])
                else:
                    ui_winset_patch = copy.copy(self.winset_patches[run])
                    ui_winset_patch.axes = None
                    ui_winset_patch.figure = None
                    ui_winset_patch.set_transform(ax.transData)
                    ax.add_collection(ui_winset_patch)     
                    
            """pareto hull"""
            print("A")
            test =  np.where(np.squeeze(self.voter_role_array[run] == 1))[0]
            print("B")
            print(test)
            print(index, "C")
            full_ind = np.concatenate((index, np.where(np.squeeze(self.voter_role_array[run] == 1))[0])) if 1 in self.voter_role_array[run] else index
            considered = self.voter_position_array[full_ind, run]
            
            if len(considered) >= 3:
                hull = ConvexHull(considered)
                for s in hull.simplices:
                    ax.plot(considered[s, 0], considered[s, 1], c="black")
            elif len(considered) == 2:
                ax.plot(considered[:, 0], considered[:, 1], c="black")
            
            # trace status quo
            if self.visualization.trace_status_quo == "Yes":
                lines = [matplotlib.lines.Line2D([self.statusquo[run, 0], self.outcomes[run, 0]],
                                                 [self.statusquo[run, 1], self.outcomes[run, 1]],
                                                 linewidth=self.visualization.trace_linewidth,
                                                     color=self.visualization.trace_line_maincolor, alpha=1)]

                if run <= 4:
                    lines += [matplotlib.lines.Line2D([self.statusquo[run - i - 1, 0], self.statusquo[run - i, 0]],
                                                      [self.statusquo[run - i - 1, 1], self.statusquo[run - i, 1]],
                                                      linewidth=self.visualization.trace_linewidth,
                                                      color=self.visualization.trace_line_maincolor, alpha=(0.8 - i * .2)) for i in
                              range(run)]

                else:
                    lines += [matplotlib.lines.Line2D([self.statusquo[run - i - 1, 0], self.statusquo[run - i, 0]],
                                                      [self.statusquo[run - i - 1, 1], self.statusquo[run - i, 1]],
                                                      linewidth=self.visualization.trace_linewidth,
                                                      color=self.visualization.trace_line_maincolor, alpha=(0.8 - i * .2)) for i in
                              range(5)]

                [ax.add_line(line) for line in lines]

            ax.legend(scatterpoints=1, loc="upper center", shadow="True", bbox_to_anchor=(0.5, -0.05), ncol=3,
                      fancybox=True)

            ax.annotate("Run: " + str(run + 1), xy=(1, 1), xycoords="axes fraction")

    def visualize_animate(self, filenames):
        pass

    def save_results(self):
        """
        Save results to csv
        """
        payoffs = self.voter_radius_array - np.vstack((self.voter_radius_array[1:,:], 
                                                       tuple(0 for _ in range(self.variables.votercount))))
        colnames = [y for x in [
            ["Voter " + str(i + 1) + "-" + voter + "-ROLE"] +
            ["Voter " + str(i + 1) + "-" + voter + "-DIM-" + str(dim + 1) for dim in range(self.variables.dimensions)] +
            ["Voter " + str(i + 1) + "-" + voter + "-RADIUS"] +
            ["Voter " + str(i + 1) + "-" + voter + "-PAYOFF"] for i, voter in enumerate(self.variables.voter_names)] for
                    y in x] + \
                   ["Status Quo" + "-DIM " + str(dim + 1) for dim in range(self.variables.dimensions)] + \
                   ["Outcome" + "-DIM " + str(dim + 1) for dim in range(self.variables.dimensions)] + \
                   ["Aggregate Payoff"] +\
                   ["Total Euclidean Distance", "Total Manhattan Distance"] + \
                   ["Distance" + "-dim " + str(dim + 1) for dim in range(self.variables.dimensions)] + \
                   ["Number Veto Players", "Number Normal Voters"]

        data = np.column_stack([y for x in [[self.voter_role_array[:, i, None],
                                            self.voter_position_array[i],
                                            self.voter_radius_array[:, i, None],
                                            payoffs[:, i, None]] for i in range(self.variables.votercount)] for y in x] + \
                               [self.statusquo,
                                self.outcomes,
                                np.sum(payoffs, axis=1, keepdims=True),
                                self.total_pyth_distance,
                                self.total_manh_distance,
                                self.dimension_distance,
                                np.sum(self.voter_role_array == 1, axis=1, keepdims=True),
                                np.sum(self.voter_role_array == 0, axis=1, keepdims=True)])

        dataframe = DataFrame(data=data, columns=colnames)

        # setting up filename and folder
        timestr = time.strftime("%Y-%m-%d_%H%M")

        filename = "".join(("results", "-", str(self.variables.runs), "r-", str(self.variables.dimensions), "d-", "__",
                            timestr, ".csv"))

        csv_path = os.path.join(self.variables.directory, filename)

        dataframe.to_csv(csv_path)

        return filename

    def save_role_array(self):
        import json
        out = {"sequence": self.voter_role_array.tolist()}

        with open(os.path.join(self.variables.directory, "voter_sequence.txt"), "w") as outfile:
            json.dump(out, outfile)

    # ----------------------------------------------------------------------------------------------------#

    def set_vibration(self, size):
        """
        Return array with random numbers from specified distribution to add to SQ as vibration
        """
        if self.variables.sq_vibration_distribution == "normal":
            return np.random.normal(size=size)

        elif self.variables.sq_vibration_distribution == "uniform":
            return np.random.uniform(low=-1, high=1, size=size)

        elif self.variables.sq_vibration_distribution == "exponential":
            return np.random.exponential(size=size)

        elif self.variables.sq_vibration_distribution == "paretian":
            return np.random.pareto(size=size)

