from __future__ import division
from itertools import count
from scripts.global_vars import global_vars
from models.Buses import Buses
from scripts.stamp_helpers import *
from models.global_vars import global_vars

class Generators:
    _ids = count(0)
    RemoteBusGens = dict()
    RemoteBusRMPCT = dict()
    gen_bus_key_ = {}
    total_P = 0

    def __init__(self,
                 Bus,
                 P,
                 Vset,
                 Qmax,
                 Qmin,
                 Pmax,
                 Pmin,
                 Qinit,
                 RemoteBus,
                 RMPCT,
                 gen_type):
        """Initialize an instance of a generator in the power grid.

        Args:
            Bus (int): the bus number where the generator is located.
            P (float): the current amount of active power the generator is providing.
            Vset (float): the voltage setpoint that the generator must remain fixed at.
            Qmax (float): maximum reactive power
            Qmin (float): minimum reactive power
            Pmax (float): maximum active power
            Pmin (float): minimum active power
            Qinit (float): the initial amount of reactive power that the generator is supplying or absorbing.
            RemoteBus (int): the remote bus that the generator is controlling
            RMPCT (float): the percent of total MVAR required to hand the voltage at the controlled bus
            gen_type (str): the type of generator
        """

        self.Bus = Bus
        self.P_MW = P
        self.Vset = Vset
        self.Qmax_MVAR = Qmax
        self.Qmin_MVAR = Qmin
        self.Pmax_MW = Pmax
        self.Pmin_MW = Pmin
        self.Qinit_MVAR = Qinit
        self.RemoteBus = RemoteBus
        self.RMPCT = RMPCT
        self.gen_type = gen_type
        # convert P/Q to pu
        self.P = P/global_vars.base_MVA
        self.Vset = Vset
        self.Qmax = Qmax/global_vars.base_MVA
        self.Qmin = Qmin/global_vars.base_MVA
        self.Qinit = Qinit/global_vars.base_MVA
        self.Pmax = Pmax/global_vars.base_MVA
        self.Pmin = Pmin/global_vars.base_MVA

        self.id = self._ids.__next__()

    def assign_indexes(self, bus):
        # Nodes shared by generators on the same bus
        self.Vr_node = bus[Buses.bus_key_[self.Bus]].node_Vr
        self.Vi_node = bus[Buses.bus_key_[self.Bus]].node_Vi
        # run check to make sure the bus actually has a Q node
        self.Q_node = bus[Buses.bus_key_[self.Bus]].node_Q
        # check something about gen_type??
        self.Lr_node = bus[Buses.bus_key_[self.Bus]].node_Lr
        self.Li_node = bus[Buses.bus_key_[self.Bus]].node_Li
        self.LQ_node = bus[Buses.bus_key_[self.Bus]].node_LQ

    def stamp(self, V, Y_val, Y_row, Y_col, J_val, J_row, idx_Y, idx_J):
        P = -self.P
        Vr = V[self.Vr_node]
        Vi = V[self.Vi_node]
        Q = V[self.Q_node]

        Irg_hist = (P*Vr+Q*Vi)/(Vr**2+Vi**2)
        dIrgdVr = (P*(Vi**2-Vr**2) - 2*Q*Vr*Vi)/(Vr**2+Vi**2)**2
        dIrgdVi = (Q*(Vr**2-Vi**2) - 2*P*Vr*Vi)/(Vr**2+Vi**2)**2
        dIrgdQ = (Vi)/(Vr**2+Vi**2)
        Vr_J_stamp = -Irg_hist + dIrgdVr*Vr + dIrgdVi*Vi + dIrgdQ*Q

        idx_Y = stampY(self.Vr_node, self.Vr_node, dIrgdVr, Y_val, Y_row, Y_col, idx_Y)
        idx_Y = stampY(self.Vr_node, self.Vi_node, dIrgdVi, Y_val, Y_row, Y_col, idx_Y)
        idx_Y = stampY(self.Vr_node, self.Q_node, dIrgdQ, Y_val, Y_row, Y_col, idx_Y)
        idx_J = stampJ(self.Vr_node, Vr_J_stamp, J_val, J_row, idx_J)

        Iig_hist = (P*Vi-Q*Vr)/(Vr**2+Vi**2)
        dIigdVi = -dIrgdVr
        dIigdVr = dIrgdVi
        dIigdQ = -(Vr)/(Vr**2+Vi**2)
        Vi_J_stamp = -Iig_hist + dIigdVr*Vr + dIigdVi*Vi + dIigdQ*Q

        idx_Y = stampY(self.Vi_node, self.Vr_node, dIigdVr, Y_val, Y_row, Y_col, idx_Y)
        idx_Y = stampY(self.Vi_node, self.Vi_node, dIigdVi, Y_val, Y_row, Y_col, idx_Y)
        idx_Y = stampY(self.Vi_node, self.Q_node, dIigdQ, Y_val, Y_row, Y_col, idx_Y)
        idx_J = stampJ(self.Vi_node, Vi_J_stamp, J_val, J_row, idx_J)

        Vset_hist = self.Vset**2 - Vr**2 - Vi**2
        dVset_dVr = -2*Vr
        dVset_dVi = -2*Vi
        Vset_J_stamp = -Vset_hist + dVset_dVr*Vr + dVset_dVi*Vi

        idx_Y = stampY(self.Q_node, self.Vr_node, dVset_dVr, Y_val, Y_row, Y_col, idx_Y)
        idx_Y = stampY(self.Q_node, self.Vi_node, dVset_dVi, Y_val, Y_row, Y_col, idx_Y)
        idx_J = stampJ(self.Q_node, Vset_J_stamp, J_val, J_row, idx_J)

        return (idx_Y, idx_J)

    def stamp_dual(self, V, Y_val, Y_row, Y_col, J_val, J_row, idx_Y, idx_J):
        P = self.P
        Vr = V[self.Vr_node]
        Vi = V[self.Vi_node]
        Q = V[self.Q_node]
        Lr = V[self.Lr_node]
        Li = V[self.Li_node]
        LQ = V[self.LQ_node]

        dLrgdLr = (P*(Vr**2-Vi**2) - 2*Q*Vr*Vi)/(Vr**2+Vi**2)**2
        dLrgdLi = (-Q*(Vi**2-Vr**2) + 2*P*Vr*Vi)/(Vr**2+Vi**2)**2

        dLigdLi = -dLrgdLr
        dLigdLr = dLrgdLi

        dIrgdQ = (Vi)/(Vr**2+Vi**2)
        dIigdQ = -(Vr)/(Vr**2+Vi**2)

        dVset_dVr = -2*Vr
        dVset_dVi = -2*Vi


        idx_Y = stampY(self.Lr_node, self.Lr_node, dLrgdLr, Y_val, Y_row, Y_col, idx_Y)
        idx_Y = stampY(self.Lr_node, self.Li_node, dLrgdLi, Y_val, Y_row, Y_col, idx_Y)

        idx_Y = stampY(self.Li_node, self.Lr_node, dLigdLr, Y_val, Y_row, Y_col, idx_Y)
        idx_Y = stampY(self.Li_node, self.Li_node, dLigdLi, Y_val, Y_row, Y_col, idx_Y)

        idx_Y = stampY(self.LQ_node, self.Lr_node, dIrgdQ, Y_val, Y_row, Y_col, idx_Y)
        idx_Y = stampY(self.LQ_node, self.Li_node, dIigdQ, Y_val, Y_row, Y_col, idx_Y)

        idx_Y = stampY(self.Lr_node, self.LQ_node, dVset_dVr, Y_val, Y_row, Y_col, idx_Y)
        idx_Y = stampY(self.Li_node, self.LQ_node, dVset_dVi, Y_val, Y_row, Y_col, idx_Y)

        low = (Vr**2+Vi**2)
        lowsq = low**2

        dLrgdVr = (Lr*(lowsq*(2*P*Vr+2*Q*Vi)-2*Vr*low*(P*(Vr**2-Vi**2) + 2*Q*Vr*Vi)) + Li*(lowsq*(-2*Q*Vr+2*P*Vi)-2*Vr*low*(Q*(Vi**2-Vr**2) + 2*P*Vr*Vi)))/(lowsq**2)
        dLrgdVi = (Lr*(lowsq*(-2*P*Vi+2*Q*Vr)-2*Vi*low*(P*(Vr**2-Vi**2) + 2*Q*Vr*Vi)) + Li*(lowsq*(2*Q*Vi+2*P*Vr)-2*Vi*low*(Q*(Vi**2-Vr**2) + 2*P*Vr*Vi)))/(lowsq**2)
        dLrgdQ = (Lr*2*Vr*Vi + Li*(Vi**2 - Vr**2))/lowsq

        dLigdVr = (Lr*(lowsq*(2*Q*Vr-2*P*Vi)-2*Vr*low*(Q*(Vr**2-Vi**2) - 2*P*Vr*Vi)) + Li*(lowsq*(2*P*Vr+2*Q*Vi)-2*Vr*low*(P*(Vr**2-Vi**2) + 2*Q*Vr*Vi)))/(lowsq**2)
        dLigdVi = (Lr*(lowsq*(-2*Q*Vi-2*P*Vr)-2*Vi*low*(Q*(Vr**2-Vi**2) - 2*P*Vr*Vi)) + Li*(lowsq*(-2*P*Vi+2*Q*Vr)-2*Vi*low*(P*(Vr**2-Vi**2) + 2*Q*Vr*Vi)))/(lowsq**2)
        dLigdQ = (Lr*(Vi**2 - Vr**2) - Li*2*Vi*Vr)/lowsq

        dLQgdVi = Lr
        dLQgdVr = -Li

        idx_Y = stampY(self.Lr_node, self.Vr_node, dLrgdVr, Y_val, Y_row, Y_col, idx_Y)
        idx_Y = stampY(self.Lr_node, self.Vi_node, dLrgdVi, Y_val, Y_row, Y_col, idx_Y)
        idx_Y = stampY(self.Lr_node, self.Q_node, dLrgdQ, Y_val, Y_row, Y_col, idx_Y)

        idx_Y = stampY(self.Li_node, self.Vr_node, dLigdVr, Y_val, Y_row, Y_col, idx_Y)
        idx_Y = stampY(self.Li_node, self.Vi_node, dLigdVi, Y_val, Y_row, Y_col, idx_Y)
        idx_Y = stampY(self.Li_node, self.Q_node, dLigdQ, Y_val, Y_row, Y_col, idx_Y)

        idx_Y = stampY(self.LQ_node, self.Vr_node, dLQgdVr, Y_val, Y_row, Y_col, idx_Y)
        idx_Y = stampY(self.LQ_node, self.Vi_node, dLQgdVi, Y_val, Y_row, Y_col, idx_Y)

        Iig_hist = Li*dLigdLi + Lr*dLigdLr
        Vi_J_stamp = -Iig_hist + dLigdLi*Li + dLigdLr*Lr + dLigdVr*Vr + dLigdVi*Vi + dLigdQ*Q

        Irg_hist = Li*dLrgdLi + Lr*dLrgdLr
        Vr_J_stamp = -Irg_hist + dLrgdLr*Lr + dLrgdLi*Li + dLrgdVr*Vr + dLrgdVi*Vi + dLrgdQ*Q

        idx_J = stampJ(self.Li_node, Vi_J_stamp, J_val, J_row, idx_J)
        idx_J = stampJ(self.Lr_node, Vr_J_stamp, J_val, J_row, idx_J)

        return (idx_Y, idx_J)

    def calc_residuals(self, resid, V):
        P = -self.P
        Vr = V[self.Vr_node]
        Vi = V[self.Vi_node]
        Q = V[self.Q_node]
        resid[self.Vr_node] += (P*Vr+Q*Vi)/(Vr**2+Vi**2)
        resid[self.Vi_node] += (P*Vi-Q*Vr)/(Vr**2+Vi**2)
        resid[self.Q_node] += self.Vset**2 - Vr**2 - Vi**2
