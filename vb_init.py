# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 16:26:48 2017

@author: Frederik
"""

import vb_var as var
import numpy as np

class Voter(object):
    def __init__(self, name, position, agenda_setter, veto_player, drift):
        self.name = name
        self.agenda_setter = agenda_setter
        self.veto_player = veto_player
        self.position = np.array([position])
        self.original_position = position
        self.drift = np.array([drift])

class setVars(object):
    def __init__(self):
        self.figs = []
        self.save_results = var.saveResults
        self.visualize = var.visualize
        self.directory = var.directory

        self.runs = var.runs
        self.number_dimensions = var.number_dimensions

        self.distance_type = var.distance_type
        self.distribution_type = var.distribution

        self.alter_status_quo = var.alter_status_quo
        self.alter_preferences = var.alterPreferences
        
        self.drift_status_quo = np.array(var.driftStatusQuo)
        
        self.breaks = var.breaks
        
        self.model_number = var.model_number

        self.voters = [Voter(var.voters['voter_names'][i],
                             var.voters['voter_positions'][i], 
                             var.voters['voter_agendasetter'][i], 
                             var.voters['voter_vetoplayer'][i],
                             var.voters['voter_drift'][i])
                             for i in range(len(var.voters['voter_names']))]
        
          
        self.veto_players  = [voter for voter in self.voters if voter.veto_player is True]
        self.agenda_setter = [voter for voter in self.voters if voter.agenda_setter is True][0]
        self.normal_voters = [voter for voter in self.voters if not voter.agenda_setter and not voter.veto_player]

        self.status_quo = np.array(var.status_quo)
        
        self.animate = var.animate
        
        self.drawWinset = var.drawWinset
        
        self.trace = var.trace
        
        self.custom_sequence = var.custom_sequence
        
        self.custom_role_array = var.custom_role_array
        
        self.role_array = var.role_array
        
        self.save_sequence = var.save_sequence

        self.randomize_veto = var.randomize_veto
        
        self.randomize_as = var.randomize_as