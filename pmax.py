import talib as ta
import numpy as np
import math
import pandas as pd

def moving_average(x, n, type='simple'):
    # use talib
    return ta.SMA(x, n)


def calculate_pmax(var_array, close_array, high_array, low_array, atr_period, atr_multiplier):

    try:
        atr = ta.ATR(high_array, low_array, close_array, atr_period)
    except Exception as exp:
        print('exception in atr:', str(exp), flush=True)
        return []

    previous_final_upperband = 0
    previous_final_lowerband = 0
    final_upperband = 0
    final_lowerband = 0
    previous_var = 0
    previous_pmax = 0
    pmax = []
    pmaxc = 0

    for i in range(0, len(close_array)):
        if pd.isnull(close_array[i]):
            pass
        else:
            atrc = atr[i]
            varc = var_array[i]

            if math.isnan(atrc):
                atrc = 0

            basic_upperband = varc + atr_multiplier * atrc
            basic_lowerband = varc - atr_multiplier * atrc

            if basic_upperband < previous_final_upperband or previous_var > previous_final_upperband:
                final_upperband = basic_upperband
            else:
                final_upperband = previous_final_upperband

            if basic_lowerband > previous_final_lowerband or previous_var < previous_final_lowerband:
                final_lowerband = basic_lowerband
            else:
                final_lowerband = previous_final_lowerband

            if previous_pmax == previous_final_upperband and varc <= final_upperband:
                pmaxc = final_upperband
            else:
                if previous_pmax == previous_final_upperband and varc >= final_upperband:
                    pmaxc = final_lowerband
                else:
                    if previous_pmax == previous_final_lowerband and varc >= final_lowerband:
                        pmaxc = final_lowerband
                    elif previous_pmax == previous_final_lowerband and varc <= final_lowerband:
                        pmaxc = final_upperband
            
            pmax.append(pmaxc)
            previous_var = varc
            previous_final_upperband = final_upperband
            previous_final_lowerband = final_lowerband
            previous_pmax = pmaxc

    for i in range(0, len(pmax)):
        if (pmax[i] == 0):
            pmax[i] = np.NaN

    return pmax