

def stampY(i, j, val, Y_val, Y_row, Y_col, idx):
    if val == 0.:
        return idx
    Y_val[idx] = val
    Y_row[idx] = i
    Y_col[idx] = j
    idx += 1
    return idx

def stampJ(i, val, J_val, J_row, idx):
    if val == 0.:
        return idx
    J_val[idx] = val
    J_row[idx] = i
    idx += 1
    return idx
