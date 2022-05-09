from __future__ import division
import numpy as np
from models.Buses import Buses
from models.Buses import Buses
from scripts.stamp_helpers import *
from models.global_vars import global_vars

class FeasibilitySource:

    def __init__(self,
                 Bus):
        """Initialize slack bus in the power grid.

        Args:
            Bus (int): the bus number corresponding to this set of feasibility currents
        """
        self.Bus = Bus

        self.Ir_init = 0.0001
        self.Ii_init = 0.0001


    def assign_nodes(self, bus):
        """Assign the additional slack bus nodes for a slack bus.
        Args:
            You decide :)i
        Returns:
            None
        """
        # TODO: You decide how to implement variables for the feasibility injections
        self.Vr_node = bus[Buses.bus_key_[self.Bus]].node_Vr
        self.Vi_node = bus[Buses.bus_key_[self.Bus]].node_Vi
        #check something about gen_type??
        self.Lr_node = bus[Buses.bus_key_[self.Bus]].node_Lr
        self.Li_node = bus[Buses.bus_key_[self.Bus]].node_Li

    def stamp(self, V, Y_val, Y_row, Y_col, J_val, J_row, idx_Y, idx_J):
        # You need to implement this.
        idx_Y = stampY(self.Vr_node, self.Lr_node, -1, Y_val, Y_row, Y_col, idx_Y)
        idx_Y = stampY(self.Vi_node, self.Li_node, -1, Y_val, Y_row, Y_col, idx_Y)
        return (idx_Y, idx_J)

    def stamp_dual(self):
        # You need to implement this.
        pass
