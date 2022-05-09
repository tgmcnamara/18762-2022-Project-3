from __future__ import division
from itertools import count
from models.Buses import Buses
from scripts.stamp_helpers import *
from models.global_vars import global_vars

class Loads:
    _ids = count(0)

    def __init__(self,
                 Bus,
                 P,
                 Q,
                 IP,
                 IQ,
                 ZP,
                 ZQ,
                 area,
                 status):
        """Initialize an instance of a PQ or ZIP load in the power grid.

        Args:
            Bus (int): the bus where the load is located
            self.P (float): the active power of a constant power (PQ) load.
            Q (float): the reactive power of a constant power (PQ) load.
            IP (float): the active power component of a constant current load.
            IQ (float): the reactive power component of a constant current load.
            ZP (float): the active power component of a constant admittance load.
            ZQ (float): the reactive power component of a constant admittance load.
            area (int): location where the load is assigned to.
            status (bool): indicates if the load is in-service or out-of-service.
        """
        self.Bus = Bus
        self.P_MW = P
        self.Q_MVA = Q
        self.IP_MW = IP
        self.IQ_MVA = IQ
        self.ZP_MW = ZP
        self.ZQ_MVA = ZQ
        self.area = area
        self.status = status
        self.id = Loads._ids.__next__()

        self.P = P/global_vars.base_MVA
        self.Q = Q/global_vars.base_MVA
        self.IP = IP/global_vars.base_MVA
        self.IQ = IQ/global_vars.base_MVA
        self.ZP = ZP/global_vars.base_MVA
        self.ZQ = ZQ/global_vars.base_MVA

    def assign_indexes(self, bus):
        # Nodes shared by generators on the same bus
        self.Vr_node = bus[Buses.bus_key_[self.Bus]].node_Vr
        self.Vi_node = bus[Buses.bus_key_[self.Bus]].node_Vi
        # check something about gen_type??
        self.Lr_node = bus[Buses.bus_key_[self.Bus]].node_Lr
        self.Li_node = bus[Buses.bus_key_[self.Bus]].node_Li

    def stamp(self, V, Y_val, Y_row, Y_col, J_val, J_row, idx_Y, idx_J):
        Vr = V[self.Vr_node]
        Vi = V[self.Vi_node]

        Irg_hist = (self.P*Vr+self.Q*Vi)/(Vr**2+Vi**2)
        dIrldVr = (self.P*(Vi**2-Vr**2) - 2*self.Q*Vr*Vi)/(Vr**2+Vi**2)**2
        dIrldVi = (self.Q*(Vr**2-Vi**2) - 2*self.P*Vr*Vi)/(Vr**2+Vi**2)**2
        Vr_J_stamp = -Irg_hist + dIrldVr*Vr + dIrldVi*Vi

        idx_Y = stampY(self.Vr_node, self.Vr_node, dIrldVr, Y_val, Y_row, Y_col, idx_Y)
        idx_Y = stampY(self.Vr_node, self.Vi_node, dIrldVi, Y_val, Y_row, Y_col, idx_Y)
        idx_J = stampJ(self.Vr_node, Vr_J_stamp, J_val, J_row, idx_J)

        Iig_hist = (self.P*Vi-self.Q*Vr)/(Vr**2+Vi**2)
        dIildVi = -dIrldVr
        dIildVr = dIrldVi
        Vi_J_stamp = -Iig_hist + dIildVr*Vr + dIildVi*Vi

        idx_Y = stampY(self.Vi_node, self.Vr_node, dIildVr, Y_val, Y_row, Y_col, idx_Y)
        idx_Y = stampY(self.Vi_node, self.Vi_node, dIildVi, Y_val, Y_row, Y_col, idx_Y)
        idx_J = stampJ(self.Vi_node, Vi_J_stamp, J_val, J_row, idx_J)

        return (idx_Y, idx_J)

    def stamp_dual(self, V, Y_val, Y_row, Y_col, J_val, J_row, idx_Y, idx_J):
        # You need to implement this.
        Vr = V[self.Vr_node]
        Vi = V[self.Vi_node]
        Lr = V[self.Lr_node]
        Li = V[self.Li_node]

        dLrldLr = (self.P*(Vi**2-Vr**2) - 2*self.Q*Vr*Vi)/(Vr**2+Vi**2)**2
        dLrldLi = (self.Q*(Vr**2-Vi**2) - 2*self.P*Vr*Vi)/(Vr**2+Vi**2)**2

        idx_Y = stampY(self.Lr_node, self.Lr_node, dLrldLr, Y_val, Y_row, Y_col, idx_Y)
        idx_Y = stampY(self.Lr_node, self.Li_node, dLrldLi, Y_val, Y_row, Y_col, idx_Y)

        dLildLi = -dLrldLr
        dLildLr = dLrldLi

        idx_Y = stampY(self.Li_node, self.Lr_node, dLildLr, Y_val, Y_row, Y_col, idx_Y)
        idx_Y = stampY(self.Li_node, self.Li_node, dLildLi, Y_val, Y_row, Y_col, idx_Y)

        low = (Vr**2+Vi**2)
        lowsq = low**2
        P = self.P
        Q = self.Q

        dLrldVr = (Lr*(lowsq*(-2*P*Vr-2*Q*Vi)-2*Vr*low*(P*(Vi**2-Vr**2) - 2*Q*Vr*Vi)) + Li*(lowsq*(2*Q*Vr-2*P*Vi)-2*Vr*low*(Q*(Vr**2-Vi**2) - 2*P*Vr*Vi)))/(lowsq**2)
        dLrldVi = (Lr*(lowsq*(2*P*Vi-2*Q*Vr)-2*Vi*low*(P*(Vi**2-Vr**2) - 2*Q*Vr*Vi)) + Li*(lowsq*(-2*Q*Vi-2*P*Vr)-2*Vi*low*(Q*(Vr**2-Vi**2) - 2*P*Vr*Vi)))/(lowsq**2)

        dLildVr = (Lr*(lowsq*(2*Q*Vr-2*P*Vi)-2*Vr*low*(Q*(Vr**2-Vi**2) - 2*P*Vr*Vi)) + Li*(lowsq*(2*P*Vr+2*Q*Vi)-2*Vr*low*(P*(Vr**2-Vi**2) + 2*Q*Vr*Vi)))/(lowsq**2)
        dLildVi = (Lr*(lowsq*(-2*Q*Vi-2*P*Vr)-2*Vi*low*(Q*(Vr**2-Vi**2) - 2*P*Vr*Vi)) + Li*(lowsq*(-2*P*Vi+2*Q*Vr)-2*Vi*low*(P*(Vr**2-Vi**2) + 2*Q*Vr*Vi)))/(lowsq**2)

        idx_Y = stampY(self.Lr_node, self.Vr_node, dLrldVr, Y_val, Y_row, Y_col, idx_Y)
        idx_Y = stampY(self.Lr_node, self.Vi_node, dLrldVi, Y_val, Y_row, Y_col, idx_Y)
        idx_Y = stampY(self.Li_node, self.Vr_node, dLildVr, Y_val, Y_row, Y_col, idx_Y)
        idx_Y = stampY(self.Li_node, self.Vi_node, dLildVi, Y_val, Y_row, Y_col, idx_Y)

        Iig_hist = Li*dLildLi + Lr*dLildLr
        Vi_J_stamp = -Iig_hist + dLildLi*Li + dLildLr*Lr + dLildVr*Vr + dLildVi*Vi

        Irg_hist = Li*dLrldLi + Lr*dLrldLr
        Vr_J_stamp = -Irg_hist + dLrldLr*Lr + dLrldLi*Li + dLrldVr*Vr + dLrldVi*Vi

        idx_J = stampJ(self.Li_node, Vi_J_stamp, J_val, J_row, idx_J)
        idx_J = stampJ(self.Lr_node, Vr_J_stamp, J_val, J_row, idx_J)

        return (idx_Y, idx_J)

    def calc_residuals(self, resid, V):
        P = self.P
        Vr = V[self.Vr_node]
        Vi = V[self.Vi_node]
        Q = self.Q
        resid[self.Vr_node] += (P*Vr+Q*Vi)/(Vr**2+Vi**2)
        resid[self.Vi_node] += (P*Vi-Q*Vr)/(Vr**2+Vi**2)
