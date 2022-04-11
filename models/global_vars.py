
class global_vars:
    def __init__(self):
        pass

    base_MVA = 100
    enforce_Qlim = False
    # xfmr models:
    # 0: ABCD model from Andersonn (no extra nodes)
    # 1: Amrit's VCCS/CCCS model (4 extra nodes per xfmr)
    xfmr_model = 1