from __future__ import division
from itertools import count
import numpy as np


class Buses:
    _idsActiveBuses = count(1)
    _idsAllBuses = count(1)

    _node_index = count(0)
    bus_key_ = {}
    all_bus_key_ = {}

    def __init__(self,
                 Bus,
                 Type,
                 Vm_init,
                 Va_init,
                 Area):
        """Initialize an instance of the Buses class.

        Args:
            Bus (int): The bus number.
            Type (int): The type of bus (e.g., PV, PQ, of Slack)
            Vm_init (float): The initial voltage magnitude at the bus.
            Va_init (float): The initial voltage angle at the bus.
            Area (int): The zone that the bus is in.
        """

        self.Bus = Bus
        self.Type = Type
        self.Vm_init = Vm_init
        self.Va_init = Va_init
        self.Vr_init = Vm_init*np.cos(Va_init*np.pi/180)
        self.Vi_init = Vm_init*np.sin(Va_init*np.pi/180)

        # initialize all nodes
        self.node_Vr = None  # real voltage node at a bus
        self.node_Vi = None  # imaginary voltage node at a bus
        self.node_Q = None  # reactive power or voltage contstraint node at a bus

        # initialize dual nodes
        # TODO - you can name them as you please
        self.node_Lr = None
        self.node_Li = None
        self.node_LQ = None

        # initialize the bus key
        self.idAllBuses = self._idsAllBuses.__next__()
        Buses.all_bus_key_[self.Bus] = self.idAllBuses - 1


    def __str__(self):
        return_string = 'The bus number is : {} with Vr node as: {} and Vi node as {} '.format(self.Bus,
                                                                                               self.node_Vr,
                                                                                               self.node_Vi)
        return return_string

    def assign_primal_nodes(self):
        """Assign nodes for primal variables based on the bus type.

        Returns:
            None
        """
        # If Slack or PQ Bus
        if self.Type == 1 or self.Type == 3:
            self.node_Vr = self._node_index.__next__()
            self.node_Vi = self._node_index.__next__()

        # If PV Bus
        elif self.Type == 2:
            self.node_Vr = self._node_index.__next__()
            self.node_Vi = self._node_index.__next__()
            self.node_Q = self._node_index.__next__()

    def assign_dual_nodes(self):
        """Assign nodes for the dual variables (lambdas)

        Returns:
            None
        """
        # TODO
        # You need to do this
        # Remember, every equality constraint in your system needs a lambda variable.
        self.node_Lr = self._node_index.__next__()
        self.node_Li = self._node_index.__next__()

        if self.Type == 2:
            self.node_LQ = self._node_index.__next__()

    def calc_Vphasor(self, V_sol):
        Vr = V_sol[self.node_Vr]
        Vi = V_sol[self.node_Vi]
        Vmag = np.sqrt(Vr**2 + Vi**2)
        Vth_deg = np.arctan2(Vi, Vr)*180/np.pi
        return (Vmag, Vth_deg)
