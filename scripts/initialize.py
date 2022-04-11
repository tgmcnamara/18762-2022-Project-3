import numpy as np

def initialize(size_Y, bus, generator, slack, flat_start=False):
    V_init = np.zeros(size_Y, dtype=np.float)
    if flat_start:
        for ele in bus:
            V_init[ele.node_Vr] = 1
            V_init[ele.node_Vi] = 0
            # TODO: You'll want to initialize all the lambda values as well...
            # HINT: A very small, positive number usually works well
        for ele in generator:
            V_init[ele.Q_node] += (ele.Qmax+ele.Qmin)/2
            # TODO: initialize the lambda associated with the Vset equation
        for ele in slack:
            # TODO: Initialize all the slack current injections
            pass
    else:
        for ele in bus:
            V_init[ele.node_Vr] = ele.Vr_init
            V_init[ele.node_Vi] = ele.Vi_init
            # TODO: You'll want to initialize all the lambda values as well...
            # HINT: A very small, positive number usually works well
        for ele in generator:
            V_init[ele.Q_node] += -ele.Qinit
            # TODO: initialize the lambda associated with the Vset equation
        for ele in slack:
            V_init[ele.Slack_Ir_node] = ele.Ir_init
            V_init[ele.Slack_Ii_node] = ele.Ii_init
        for ele in slack:
            # TODO: Initialize all the slack current injections
            pass

    return V_init