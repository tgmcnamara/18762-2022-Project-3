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
        
        self.Ir_init = 0
        self.Ii_init = 0
        

    def assign_nodes(self, ):
        """Assign the additional slack bus nodes for a slack bus.
        Args:
            You decide :)
        Returns:
            None
        """
        # TODO: You decide how to implement variables for the feasibility injections
        pass

    def stamp(self, V, Y_val, Y_row, Y_col, J_val, J_row, idx_Y, idx_J):
        # You need to implement this.
        return (idx_Y, idx_J)

    def stamp_dual(self):
        # You need to implement this.
        pass
