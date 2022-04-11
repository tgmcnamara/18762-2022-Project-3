import numpy as np
from scipy.sparse import csc_matrix
from scipy.sparse.linalg import spsolve
from models.global_vars import global_vars

class PowerFlowFeasibility:

    def __init__(self,
                 case_name,
                 tol,
                 max_iters,
                 enable_limiting):
        """Initialize the PowerFlowFeasibility instance.

        Args:
            case_name (str): A string with the path to the test case.
            tol (float): The chosen NR tolerance.
            max_iters (int): The maximum number of NR iterations.
            enable_limiting (bool): A flag that indicates if we use voltage limiting or not in our solver.
        """
        # Clean up the case name string
        case_name = case_name.replace('.RAW', '')
        case_name = case_name.replace('testcases/', '')

        self.case_name = case_name
        self.tol = tol
        self.max_iters = max_iters
        self.enable_limiting = enable_limiting

    def solve(self, Y, J):
        return spsolve(Y, J)

    def apply_limiting(self, v, v_sol, v_inds, vmax, vmin, max_vstep):
        # limit step size
        dv = v_sol[v_inds] - v[v_inds]
        dv = np.minimum(dv, max_vstep)
        dv = np.maximum(dv, -max_vstep)
        v_sol[v_inds] = v[v_inds] + dv
        # clamp to vmin/vmax
        v_sol[v_inds] = np.minimum(v_sol[v_inds], vmax)
        v_sol[v_inds] = np.maximum(v_sol[v_inds], vmin)

    def check_error(self, v, v_sol):
        return np.amax(np.abs(v - v_sol))

    def stamp_linear(self, branch, transformer, shunt, slack, v_init):
        size_Y = v_init.shape[0]
        nnz = 100*size_Y
        Ylin_row = np.zeros(nnz, dtype=int)
        Ylin_col = np.zeros(nnz, dtype=int)
        Ylin_val = np.zeros(nnz, dtype=np.double)
        Jlin_row = np.zeros(4*size_Y, dtype=int)
        Jlin_val = np.zeros(4*size_Y, dtype=np.double)
        
        idx_Y = 0
        idx_J = 0

        for ele in branch:
            (idx_Y, idx_J) = ele.stamp(v_init, Ylin_val, Ylin_row, Ylin_col, Jlin_val, Jlin_row, idx_Y, idx_J)
        for ele in transformer:
            (idx_Y, idx_J) = ele.stamp(v_init, Ylin_val, Ylin_row, Ylin_col, Jlin_val, Jlin_row, idx_Y, idx_J)
        for ele in shunt:
            (idx_Y, idx_J) = ele.stamp(v_init, Ylin_val, Ylin_row, Ylin_col, Jlin_val, Jlin_row, idx_Y, idx_J)
        for ele in slack:
            (idx_Y, idx_J) = ele.stamp(v_init, Ylin_val, Ylin_row, Ylin_col, Jlin_val, Jlin_row, idx_Y, idx_J)
        
        nnz_indices = np.nonzero(Ylin_val)[0]
        Ylin = csc_matrix((Ylin_val[nnz_indices], (Ylin_row[nnz_indices], Ylin_col[nnz_indices])), shape=(size_Y, size_Y), dtype=np.float64)
        nnz_indices = np.nonzero(Jlin_val)[0]
        Jlin_col = np.zeros(Jlin_row.shape, dtype=np.int)
        Jlin = csc_matrix((Jlin_val, (Jlin_row, Jlin_col)), shape=(size_Y, 1), dtype=np.float64)
        return (Ylin, Jlin)

    def stamp_linear_dual(self,):
        # Generate the dual stamps for all your linear devices.
        # You should decide the necessary arguments.
        pass 

    def stamp_nonlinear(self, generator, load, v_init):
        size_Y = v_init.shape[0]
        nnz = 100*size_Y
        Ynlin_row = np.zeros(nnz, dtype=int)
        Ynlin_col = np.zeros(nnz, dtype=int)
        Ynlin_val = np.zeros(nnz, dtype=np.double)
        Jnlin_row = np.zeros(4*size_Y, dtype=int)
        Jnlin_val = np.zeros(4*size_Y, dtype=np.double)
        
        idx_Y = 0
        idx_J = 0

        for ele in generator:
            (idx_Y, idx_J) = ele.stamp(v_init, Ynlin_val, Ynlin_row, Ynlin_col, Jnlin_val, Jnlin_row, idx_Y, idx_J)
        for ele in load:
            (idx_Y, idx_J) = ele.stamp(v_init, Ynlin_val, Ynlin_row, Ynlin_col, Jnlin_val, Jnlin_row, idx_Y, idx_J)

        nnz_indices = np.nonzero(Ynlin_val)[0]
        Ynlin = csc_matrix((Ynlin_val[nnz_indices], (Ynlin_row[nnz_indices], Ynlin_col[nnz_indices])), shape=(size_Y, size_Y), dtype=np.float64)
        nnz_indices = np.nonzero(Jnlin_val)[0]
        Jlin_col = np.zeros(Jnlin_row.shape, dtype=np.int)
        Jnlin = csc_matrix((Jnlin_val, (Jnlin_row, Jlin_col)), shape=(size_Y, 1), dtype=np.float64)
        return (Ynlin, Jnlin)

    def stamp_nonlinear_dual(self,):
        # Generate the dual stamps for all your nonlinear devices.
        # You should decide the necessary arguments.
        pass 

    def calc_resid_primal(self, v, generator, load, slack, branch, transformer, shunt):
        # This calculates the residuals of your constraint equations.
        resid = np.zeros(v.shape)
        for ele in slack:
            ele.calc_residuals(resid, v)
        for ele in generator:
            ele.calc_residuals(resid, v)
        for ele in load:
            ele.calc_residuals(resid, v)
        for ele in branch:
            ele.calc_residuals(resid, v)
        for ele in transformer:
            ele.calc_residuals(resid, v)
        for ele in shunt:
            ele.calc_residuals(resid, v)
        return resid

    def calc_resid_dual(self,):
        # If you're feeling very ambitious, you can write a function to
        # check the residuals of the dual equations (i.e. the stationarity
        # conditions of KKT). This is not for the faint of heart.
        # You should decide the necessary arguments.
        pass
    

    def run_feas_analysis(self,
                          v_init,
                          bus,
                          slack,
                          generator,
                          transformer,
                          branch,
                          shunt,
                          load,
                          feasibility_sources):
        """Runs a feasibility analysis of the positive sequence power flow problem on this network
           using the Equivalent Circuit Formulation. Minimize the L2-norm of slack injections
           Required to satisfy KCL at each node in the split-circuit network.

        Args:
            v_init (np.array): The initial solution vector which has the same number of rows as the Y matrix.
            bus (list): Contains all the buses in the network as instances of the Buses class.
            slack (list): Contains all the slack generators in the network as instances of the Slack class.
            generator (list): Contains all the generators in the network as instances of the Generators class.
            transformer (list): Contains all the transformers in the network as instance of the Transformers class.
            branch (list): Contains all the branches in the network as instances of the Branches class.
            shunt (list): Contains all the shunts in the network as instances of the Shunts class.
            load (list): Contains all the loads in the network as instances of the Load class.
            feasibility_sources (list): Contains all the feasibility sources in the network as instances of the FeasibilitySource class.
        Returns:
            v(np.array): The final solution vector.

        """

        # # # Copy v_init into the Solution Vectors used during NR, v, and the final solution vector v_sol # # #
        v = np.copy(v_init)
        v_sol = np.copy(v)

        # if limiting methods are being used,
        # create a list of indices of only the voltage variables,
        # which is then used in the limiting function
        if self.enable_limiting:
            v_inds = []
            for ele in bus:
                v_inds.append(ele.node_Vr)
                v_inds.append(ele.node_Vi)
            if global_vars.xfmr_model == 1:
                for ele in transformer:
                    v_inds.append(ele.Vaux_r_node)
                    v_inds.append(ele.Vaux_i_node)
            vmax = 1.5
            vmin = -1.5
            max_vstep = 0.15
        else:
            v_inds = None
            vmax =  np.inf
            vmin = -np.inf
            max_vstep = np.inf

        # # # Stamp Linear Power Grid Elements into Y matrix # # #
        Ylin, Jlin = self.stamp_linear(branch, transformer, shunt, slack, v_init)

        # TODO: PART 1, STEP 2.1 - Complete the stamp_linear_dual function which create the dual stamps
        #  associated with all of the linear elements of the network.
        #  This function should call the stamp_dual function of each linear element and return a Y matrix of dual stamps.
        #  You need to decide the input arguments and return values.
        self.stamp_linear_dual()

        # # # Initialize While Loop (NR) Variables # # #
        # Feel free to change these if you'd like
        err_max = 10  # maximum error at the current NR iteration. Initialize to some large value.
        tol = self.tol  # chosen NR tolerance
        NR_count = 0  # current NR iteration
        check_for_zero_rows_cols = False # useful for debugging
        conveged = False
        # # # Begin Solving Via NR # # #
        # TODO: PART 1, STEP 2.2 - Complete the NR While Loop
        while NR_count < self.max_iters:

            # # # Stamp Nonlinear Power Grid Elements into Y matrix # # #
            (Ynlin, Jnlin) = self.stamp_nonlinear(generator, load, v)

            # # # Stamp Nonlinear Power Grid dual values into Y matrix # # #
            # TODO: PART 1, STEP 2.3 - Complete the stamp_nonlinear_dual function which creates the dual stamps for
            #  the nonlinear elements. This function should call a stamp_dual function of each nonlinear element and return
            #  an updated Y matrix. You need to decide the input arguments and return values.
            self.stamp_linear_dual()

            # # # Solve The System # # #
            # TODO: PART 1, STEP 2.4 - Complete the solve function which solves system of equations Yv = J. The
            #  function should return a new v_sol.
            #  You need to decide the input arguments and return values.
            Y = Ynlin + Ylin
            J = Jnlin + Jlin
            if check_for_zero_rows_cols:
                zero_rows = []
                zero_cols = []
                for i in range(Y.shape[0]):
                    if len(Y[i,:].data) == 0:
                        zero_rows.append(i)
                    if len(Y[:,i].data) == 0:
                        zero_cols.append(i)
                print("Rows of all zeros: ", zero_rows)
                print("Columns of all zeros: ", zero_rows)
            v_sol = self.solve(Y, J)
            NR_count += 1
            # # # Compute The Error at the current NR iteration # # #
            err_max = self.check_error(v, v_sol)
            print("Iter: %d, max error: %.3e" % (NR_count, err_max))
            if err_max < tol:
                converged = True
                break
            # Limit applicable variable values.
            # Feel free to change this function and its arguments as you wish
            # to account for the differences of feasibility analysis vs. powerflow
            if self.enable_limiting and err_max > tol:
                self.apply_limiting(v, v_sol, v_inds, vmax, vmin, max_vstep)
            else:
                v = np.copy(v_sol)

        if converged:
            primal_resid = self.calc_resid_primal(v_sol, generator, load, slack, branch, transformer, shunt)
            max_resid = np.amax(np.abs(primal_resid))
            print("Feasibility analysis converged in %d iterations" % (NR_count))
            print("Maximum primal residual in solution is %.3e" % (max_resid))
        else:
            print("Maximum iteration count reached before convergence.")

        return v
