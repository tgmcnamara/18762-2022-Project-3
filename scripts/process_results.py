import numpy as np

def process_results(v, bus, slack, generator):
    print("BUS VOLTAGES:")
    for ele in bus:
        # PQ bus
        if ele.Type == 1:
            Vr = v[ele.node_Vr]
            Vi = v[ele.node_Vi]
            Vmag = np.sqrt(Vr**2 + Vi**2)
            Vth = np.arctan2(Vi, Vr) * 180/np.pi
            print("%d, Vmag: %.3f p.u., Vth: %.3f deg" % (ele.Bus, Vmag, Vth))
        # PV bus
        elif ele.Type == 2:
            Vr = v[ele.node_Vr]
            Vi = v[ele.node_Vi]
            Vmag = np.sqrt(Vr**2 + Vi**2)
            Vth = np.arctan2(Vi, Vr) * 180.0/np.pi
            Qg = v[ele.node_Q]*100
            print("%d: Vmag: %.3f p.u., Vth: %.3f deg, Qg: %.3f MVAr" % (ele.Bus, Vmag, Vth, Qg))
        elif ele.Type == 3:
            Vr = v[ele.node_Vr]
            Vi = v[ele.node_Vi]
            Vmag = np.sqrt(Vr**2 + Vi**2)
            Vth = np.arctan2(Vi, Vr) * 180/np.pi
            Pg, Qg = slack[0].calc_slack_PQ(v)
            print("SLACK: %d, Vmag: %.3f p.u., Vth: %.3f deg, Pg: %.3f MW, Qg: %.3f MVar" % (ele.Bus, Vmag, Vth, Pg*100, Qg*100))