import numpy as np
import math
# from numba import njit

# @njit
def calc_depth(
        base: float,
        slope: float,
        volume: float) -> float:
    """From DAMCAT v5"""

    # use vol pyramid = 1/3 * AreaBase * Height
    bottom_depth = (base / 2) / slope
    
    # botVol = (1# / 3#) * (dBase * dBase) * botDep
    bottom_volume = 0.3333333333 * (base * base) * bottom_depth

    full_volume = volume + bottom_volume
    
    # fullDep = (fullVol / ((4# / 3#) * dSlope * dSlope)) ^ (1# / 3#)
    full_depth = (full_volume / (1.33333333 * slope * slope)) ** 0.33333333
     
    depth = full_depth - bottom_depth

    return depth


# @njit
def calc_surface_area(
        base: float,
        slope: float,
        depth: float) -> float:
    """From DAMCAT v5"""

    top_length = 2 * (depth * slope) + base

    surface_area = top_length * top_length

    return surface_area


def calc_water_in_lake_surface_area(
    base: float,
    slope: float,
    depth: float
) -> float:
    """Compute the surface area of water touching dam sides and base.
    
    This is used to compute leakage at each time step."""
    top_length = 2 * (depth * slope) + base
    
    # lateral surface area of a truncated pyramid
    L = (top_length + base) * math.sqrt(((top_length - base) * (top_length - base)) + (4 * (depth * depth)))

    # base area of truncated pyramid
    base_area = base * base

    return L + base_area


# @njit
def daily_sim(daily_met, lake_config, leaky_lake, evap_factor) -> list:
    """Run a daily lake simulation.
    
    Parameters
    ----------
    daily_met : ndarray
        NumPy ndarray with tabular like structure. 
        Axis 0 represent rows of daily data. 
        Axis 1 represents columns of variables: 
            column 0 is daily rainfall in m, 
            column 1 is daily evaporation in m,
            column 2 is daily inflows from the roaded catchment, 
            column 3 is daily outflows due to farm management.
    
    lake_config : dict
        Lake simulation dictionary object with key:value pairs
        for the lake volume (`lake_volume`), initial lake water
        volume (`init_water_volume`), slope (`slope`), and
        base length (`base`).
    
    leaky_lake : bool
        If a leaky lake, 5 mm per m2 is lost per-day. 

    evap_factor : float
        % reduction in evaporation due to evaporation treatment.
    
    Returns
    -------
    output_arr : list
        NumPy array output with rows (axis 0) corresponding to days
        and columns (axis 1) corresponding to date (day index),
        start of day volume, end of day volume, level, surface area,
        inflows, evaporation, and outflows. The NumPy array is 
        converted to a list object for JSON encoding.
    """
    
    ndays = daily_met.shape[0]
    init_lake_volume = lake_config["lake_volume"]
    init_water_volume = lake_config["init_water_volume"]
    slope = lake_config["slope"]
    base = lake_config["base"]


    # output array to fill with each iteration
    # column 0: date (day index)
    # column 1: start volume m3
    # column 2: end volume m3
    # columnn 3: level m
    # column 4: surface area m2
    # column 5: inflows m3
    # column 6: evap m3
    # column 7: outflows m3
    output_arr = np.zeros((ndays, 8))

    tmp_volume = init_water_volume

    for day in range(0, ndays):
        
        # set date and start volume in output array
        output_arr[day, 0] = day
        output_arr[day, 1] = tmp_volume

        # get water depth
        tmp_depth = calc_depth(base, slope, tmp_volume)

        # get surface area
        tmp_surface_area = calc_surface_area(base, slope, tmp_depth)

        # compute evaporation
        tmp_evap = tmp_surface_area * daily_met[day, 1] * (1 - (evap_factor / 100))

        # inflows (runoff from roaded catchment)
        tmp_inflows = daily_met[day, 2]

        # outflows (livestock drinking and other uses)
        tmp_outflows = daily_met[day, 3]

        # direct rain on the lake
        tmp_direct_rain = tmp_surface_area * daily_met[day, 0]

        if leaky_lake:
            water_area_touching_dam = calc_water_in_lake_surface_area(base, slope, tmp_depth)
            tmp_volume = tmp_volume - (5 * 0.001 * water_area_touching_dam) #  5 mm lost per day in m^3

        tmp_volume = tmp_volume - tmp_evap - tmp_outflows + tmp_inflows + tmp_direct_rain

        if tmp_volume < 0:
            tmp_volume = 0
            tmp_depth = 0
            tmp_surface_area = 0
        
        if tmp_volume > init_lake_volume:
            tmp_volume = init_lake_volume
            tmp_depth = calc_depth(base, slope, tmp_volume)
            tmp_surface_area = calc_surface_area(base, slope, tmp_depth)

        # write outputs
        # column 2: end volume m3
        # columnn 3: level m
        # column 4: surface area m2
        # column 5: inflows m3
        # column 6: evap m3
        # column 7: outflows m3
        output_arr[day, 2] = tmp_volume
        output_arr[day, 3] = tmp_depth
        output_arr[day, 4] = tmp_surface_area
        output_arr[day, 5] = tmp_inflows
        output_arr[day, 6] = tmp_evap
        output_arr[day, 7] = tmp_outflows

    return output_arr.tolist()


