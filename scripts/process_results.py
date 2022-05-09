import numpy as np

def process_results(v, bus, slack, generator):
    print("BUS VOLTAGES:")
    ifmax = np.zeros(3)
    rfmax = np.zeros(3)
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

        if(abs(v[ele.node_Lr]) > np.amin(np.absolute(rfmax))):
            if(abs(v[ele.node_Lr]) > abs(rfmax[0])):
                rfmax[2] = rfmax[1]
                rfmax[1] = rfmax[0]
                rfmax[0] = v[ele.node_Lr]
            elif(abs(v[ele.node_Lr]) > abs(rfmax[1])):
                rfmax[2] = rfmax[1]
                rfmax[1] = v[ele.node_Lr]
            else:
                rfmax[2] = v[ele.node_Lr]

        if(abs(v[ele.node_Li]) > np.amin(np.absolute(ifmax))):
            if(abs(v[ele.node_Li]) > abs(ifmax[0])):
                ifmax[2] = ifmax[1]
                ifmax[1] = ifmax[0]
                ifmax[0] = v[ele.node_Li]
            elif(abs(v[ele.node_Li]) > abs(ifmax[1])):
                ifmax[2] = ifmax[1]
                ifmax[1] = v[ele.node_Li]
            else:
                ifmax[2] = v[ele.node_Li]

        print("Feasibility: %d, Real %.3f , Imag %.3f" % (ele.Bus, v[ele.node_Lr], v[ele.node_Li]))

    if((np.amax(np.absolute(rfmax)) < 0.000000001) and (np.amax(np.absolute(ifmax)) < 0.00000001)):
        print("The circuit is feasible")

    else:
        print("The circuit is infeasible")
        print("Largest real ifs: %.3f , %.3f , %.3f " % (rfmax[0], rfmax[1], rfmax[2]))
        print("Largest imag ifs: %.3f , %.3f , %.3f " % (ifmax[0], ifmax[1], ifmax[2]))

