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

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon
from matplotlib.collections import PatchCollection
import matplotlib.lines

from shapely.geometry import Point, LinearRing
from scipy.spatial import distance as dist
import copy


# logging.basicConfig(filename = "vblog.log", level = logging.DEBUG)

class Simulation:
    def __init__(self, variables, parent=None):
        self.parent = parent
        #self.parent.logWidget.log.append("log3")

        self.variables = variables

        self.variables.custom_role_array = False  # TODO implement this

        """Initialize Voter Arrays"""
        self.voter_position_array = np.zeros(
            (self.variables.votercount, self.variables.runs, self.variables.dimensions))

        if not self.variables.alter_preferences == "drift":
            for i, voter in enumerate(self.variables.voter_positions):
                self.voter_position_array[i] = voter
        else:
            self.voter_position_array[:, 0, :] = self.variables.voter_positions

        self.voter_radius_array = np.zeros((self.variables.votercount, self.variables.runs, 1))

        if self.variables.custom_role_array:
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
            self.stop = []

        """if shapely, initialize shapely objects for each voter"""
        if self.variables.method == "optimization":
            self.winset_patches = []

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
            self.voter_radius_array[agenda_setter_index, run] = self.determine_distance(
                self.voter_position_array[agenda_setter_index, run],
                self.statusquo[[run]], self.variables.distance_type)

            if veto_player_index.any():
                self.voter_radius_array[veto_player_index, run, 0] = self.determine_distance(
                    self.statusquo[[run]], self.voter_position_array[veto_player_index, run], self.variables.distance_type)

            if normal_player_index.any():
                self.voter_radius_array[normal_player_index, run, 0] = self.determine_distance(
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
            print("possible coal", possible_coalitions)
            # TODO from coalition grid search to function
            possible_outcomes = []

            """grid search"""
            if self.variables.method == "grid" or self.variables.method == "random grid":
                """grid index to make grid a square around agenda setter radius"""
                grid_index = [[self.voter_position_array[agenda_setter_index, run].item(dim) - self.voter_radius_array[
                    agenda_setter_index, run].item(0) for
                               dim in range(self.variables.dimensions)],
                              [self.voter_position_array[agenda_setter_index, run].item(dim) +
                               self.voter_radius_array[agenda_setter_index, run].item(0) for dim in
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
                print("optimize")
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

                closest_points = []

                for winset in winsets:
                    if winset.area != 0:
                        pol_ext = LinearRing(winset.exterior.coords)
                        #                    d = polExt.project(voter_points[agendaSetterIndex])
                        d = pol_ext.project([voter_points[index] for index in agenda_setter_index][0])
                        p = pol_ext.interpolate(d)
                        closest_point = p.coords[0]
                        closest_points.append(closest_point)

                    else:
                        closest_points.append(self.statusquo[run].tolist())

                closest_points_distances = [
                    self.determine_distance(self.voter_position_array[agenda_setter_index, run], np.array([point])) for
                    point
                    in closest_points]
                min_index = np.argmin(closest_points_distances)
                self.outcomes[run] = closest_points[min_index]

                if self.variables.visualize:
                    if np.all(self.outcomes[run] != self.statusquo[run]):
                        self.winset_patches.append(
                            PatchCollection([Polygon(winsets[min_index].exterior)], facecolor="red", linewidth=.5,
                                            alpha=.7))
                    else:
                        self.winset_patches.append(None)

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
                self.alter_player_preferences(run)

                #        if self.Variables.visualize:
                #            self.visualizeResults()

        if self.variables.save:
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
        #        if point1.ndim == 1:
        #            point1 = point1[None, :]
        #
        #        if point2.ndim == 1:
        #            point2 = point2[None, :]

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
            print("no points in inp")
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
        print("called vis init")
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
            self.visualize_limits[0] = ((self.voter_position_array - self.voter_radius_array)[:, :, 0].min(),
                                        (self.voter_position_array + self.voter_radius_array)[:, :, 0].max())
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
                self.visualize_limits[dim] = ((self.voter_position_array - self.voter_radius_array).min(),
                                              (self.voter_position_array + self.voter_radius_array).max())

            if save is True:
                self.variables.trace_total_change = False
                if self.variables.trace_total_change is True:
                    fig, (ax, ax1) = plt.subplots(2, 1, gridspec_kw={"height_ratios": [4, 1]})
                    fig.set_size_inches(10, 10)
                    fig.set_dpi(80)
                    ax1.plot(range(self.variables.runs), self.total_pyth_distance, c="#1f77b4")
                    ax1.scatter(range(self.variables.runs), self.total_pyth_distance, c="#d62728", s=40, clip_on=False)

                else:
                    fig = plt.figure(figsize=(18.5, 10.5))
                    ax = fig.add_subplot(111, aspect="equal")

                for run in range(self.variables.runs):
                    self.visualize_draw_on_axis(2, ax, run, self.visualize_limits)

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
                           s=70, c="black", label="Voters", clip_on=False)

                norm_patches = [Circle((xx, 0), rr) for xx, rr in
                                zip(self.voter_position_array[index, run], self.voter_radius_array[index, run])]

                norm_collection = PatchCollection(norm_patches, facecolors="grey", edgecolors="black", linewidths=0.5,
                                                  alpha=0.2)

                ax.add_collection(norm_collection)
                norm_collection.set_clip_box(ax.bbox)

            if 2 in self.voter_role_array[run]:
                index = np.where(np.squeeze(np.isin(self.voter_role_array[run], 1)))[0]

                ax.scatter(self.voter_position_array[index, run], [0 for _ in index], s=60, c="red",
                           label="Veto Players",
                           clip_on=False)

                veto_patches = [Circle((xx, 0), rr) for xx, rr in
                                zip(self.voter_position_array[index, run], self.voter_radius_array[index, run])]

                veto_collection = PatchCollection(veto_patches, facecolors="red", edgecolors="black", linewidths=0.5,
                                                  alpha=0.2)

                ax.add_collection(veto_collection)
                veto_collection.set_clip_box(ax.bbox)

            index = np.where(np.squeeze(np.isin(self.voter_role_array[run], 2)))[0]

            ax.scatter(self.voter_position_array[index, run], 0, s=60, c="lightblue", label="Agenda Setter",
                       clip_on=False)

            as_patch = Circle((self.voter_position_array[index, run], 0), self.voter_radius_array[index, run],
                              facecolor="blue", edgecolor="black", linewidth=0.5, alpha=0.2)

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

                ax.scatter(self.voter_position_array[index, run, 0], self.voter_position_array[index, run, 1], s=30,
                           c="#7f7f7f", label="Voters")

                norm_patches = [Circle((xx, yy), rr) for xx, yy, rr in zip(self.voter_position_array[index, run, 0],
                                                                           self.voter_position_array[index, run, 1],
                                                                           self.voter_radius_array[index, run])]

                norm_collection = PatchCollection(norm_patches, facecolors="#7f7f7f", edgecolors="black",
                                                  linewidths=0.5, alpha=0.2)

                ax.add_collection(norm_collection)
                norm_collection.set_clip_box(ax.bbox)

            if 1 in self.voter_role_array[run]:
                """
                plot veto players
                """
                index = np.where(np.squeeze(self.voter_role_array[run] == 1))[0]

                ax.scatter(self.voter_position_array[index, run, 0], self.voter_position_array[index, run, 1],
                           s=30, c="#d62728", label="Veto Players")

                veto_patches = [Circle((xx, yy), rr) for xx, yy, rr in zip(
                    self.voter_position_array[index, run, 0],
                    self.voter_position_array[index, run, 1],
                    self.voter_radius_array[index, run])]

                veto_collection = PatchCollection(veto_patches, facecolors="#d62728",
                                                  alpha=0.2, linewidths=0.5, edgecolors="black")

                ax.add_collection(veto_collection)
                veto_collection.set_clip_box(ax.bbox)

            """
            plot agenda setter
            """
            index = np.where(np.squeeze(self.voter_role_array[run] == 2))[0]
            ax.scatter(self.voter_position_array[index, run, 0], self.voter_position_array[index, run, 1],
                       s=30, c="#1f77b4", label="Agenda Setter")

            as_patch = Circle((
                self.voter_position_array[index, run, 0],
                self.voter_position_array[index, run, 1]),
                self.voter_radius_array[index, run],
                facecolor="#1f77b4", edgecolor="black", linewidth=0.5, alpha=0.2)

            ax.add_artist(as_patch)
            as_patch.set_clip_box(ax.bbox)

            """
            plot status quo and outcome
            """
            ax.scatter(self.statusquo[run, 0], self.statusquo[run, 1], s=35, c="#8c564b", label="Status Quo")
            ax.scatter(self.outcomes[run, 0], self.outcomes[run, 1], s=30, c="#ff7f0e", label="Outcome")

            """add precise winset patch"""
            if self.variables.method == "optimization" and self.winset_patches[run] is not None:
                print("add winset patch")
                if not fromUI:
                    ax.add_collection(self.winset_patches[run])
                else:
                    ui_winset_patch = copy.copy(self.winset_patches[run])
                    ui_winset_patch.axes = None
                    ui_winset_patch.figure = None
                    ui_winset_patch.set_transform(ax.transData)
                    ax.add_collection(ui_winset_patch)

            # trace status quo
            if self.variables.trace is True:
                lines = [matplotlib.lines.Line2D([self.statusquo[run, 0], self.outcomes[run, 0]],
                                                 [self.statusquo[run, 1], self.outcomes[run, 1]],
                                                 linewidth=2, color="#2ca02c", alpha=1)]

                if run <= 4:
                    lines += [matplotlib.lines.Line2D([self.statusquo[run - i - 1, 0], self.statusquo[run - i, 0]],
                                                      [self.statusquo[run - i - 1, 1], self.statusquo[run - i, 1]],
                                                      linewidth=2, color="#2ca02c", alpha=(0.8 - i * .2)) for i in
                              range(run)]

                else:
                    lines += [matplotlib.lines.Line2D([self.statusquo[run - i - 1, 0], self.statusquo[run - i, 0]],
                                                      [self.statusquo[run - i - 1, 1], self.statusquo[run - i, 1]],
                                                      linewidth=2, color="#2ca02c", alpha=(0.8 - i * .2)) for i in
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
        colnames = [y for x in [
            ["Voter " + str(i + 1) + "-" + voter + "-ROLE"] +
            ["Voter " + str(i + 1) + "-" + voter + "-DIM-" + str(dim + 1) for dim in range(self.variables.dimensions)] +
            ["Voter " + str(i + 1) + "-" + voter + "-RADIUS"] for i, voter in enumerate(self.variables.voter_names)] for
                    y in x] + \
                   ["Status Quo" + "-DIM " + str(dim + 1) for dim in range(self.variables.dimensions)] + \
                   ["Outcome" + "-DIM " + str(dim + 1) for dim in range(self.variables.dimensions)] + \
                   ["Total Euclidean Distance", "Total Manhattan Distance"] + \
                   ["Distance" + "-dim " + str(dim + 1) for dim in range(self.variables.dimensions)] + \
                   ["Number Veto Players", "Number Normal Voters"]

        # data

        data = np.column_stack([self.voter_role_array] + \
                               [np.column_stack((self.voter_position_array[i],
                                                 self.voter_radius_array[i])) for
                                i in range(self.variables.votercount)] + \
                               [self.statusquo,
                                self.outcomes,
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

