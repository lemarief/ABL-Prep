import json
import numpy as np
from netCDF4 import Dataset

def init_target_grid(jpka, hmax, hc, theta_s, force_z1=False, z1=None, tol=1e-12, maxiter=1000):
    """
    Initialize the vertical grid (equivalent to Fortran init_target_grid)
    
    Parameters
    ----------
    jpka : int
        Number of vertical levels
    hmax : float
        Maximum height of the grid (m)
    hc : float
        Surface stretching parameter (m)
    theta_s : float
        Stretching parameter
    force_z1 : bool
        If True, force the first vertical level to z1
    z1 : float
        Value of the first level (if force_z1=True)
    tol : float
        Tolerance for Newton iteration
    maxiter : int
        Maximum number of iterations
    
    Returns
    -------
    ght, ghw, e3t, e3w, theta_s : np.ndarray
        Grid center heights, grid edge heights, layer thickness at centers, layer thickness at edges, updated theta_s
    """
    # Allocate arrays
    ght = np.zeros(jpka+1, dtype=float)
    ghw = np.zeros(jpka+1, dtype=float)
    e3t = np.zeros(jpka+1, dtype=float)
    e3w = np.zeros(jpka+1, dtype=float)
    # If first level is forced, perform Newton iteration to adjust theta_s
    if force_z1:
        if z1 < 10.0:
            raise ValueError("z1 < first ECMWF level height (~10 m)")
        x = theta_s
        ds = 1.0 / jpka
        sc_r = (1.0 - 0.5) / jpka
        alpha = (z1 - hc*sc_r) / (hmax - hc)
        for jiter in range(maxiter):
            fx = (np.sinh(sc_r*x)/np.sinh(x)) - alpha
            fxp = (sc_r*np.cosh(sc_r*x) - np.sinh(sc_r*x)*np.cosh(x)/np.sinh(x)) / np.sinh(x)
            if abs(fx) < tol:
                break
            x -= fx / fxp
        theta_s = x
        print('*** Updated grid parameters')
        print('theta_s =', theta_s, 'hc =', hc, 'hmax =', hmax)
    
    # Compute grid spacing
    ds = 1.0 / jpka
    cff = (hmax - hc) / np.sinh(theta_s)
    
    # Compute grid edges and centers
    for jk in range(jpka, 0, -1):
        sc_w = ds*jk
        ghw[jk] = hc*sc_w + cff*np.sinh(theta_s*sc_w)
        sc_r = ds*(jk - 0.5)
        ght[jk] = hc*sc_r + cff*np.sinh(theta_s*sc_r)
    
    # Bottom boundary
    ghw[0] = 0.0
    ght[0] = 0.0
    e3t[0] = 0.0
    
    # Compute layer thickness at centers
    for jk in range(1, jpka+1):
        e3t[jk] = ghw[jk] - ghw[jk-1]
    
    # Compute layer thickness at edges
    for jk in range(jpka):
        e3w[jk] = ght[jk+1] - ght[jk]
    e3w[jpka] = ghw[jpka] - ght[jpka]
    
    return ght, ghw, e3t, e3w, theta_s

def write_grid_file(jpka, ght, ghw, e3t, e3w, filename):
    """
    Write the grid to a NetCDF file (equivalent to Fortran Write_Grid_File)
    
    Parameters
    ----------
    jpka : int
        Number of vertical levels
    ght, ghw : np.ndarray
        Grid center and edge heights
    e3t, e3w : np.ndarray
        Layer thickness at centers and edges
    filename : str
        Output NetCDF file name
    """
    with Dataset(filename, 'w', format='NETCDF4') as nc:
        # Create vertical dimension
        nc.createDimension('jpka', jpka+1)
        
        # Create variables
        ghw_var = nc.createVariable('ghw', 'f8', ('jpka',))
        ghw_var.units = 'm'
        ghw_var.long_name = 'Height at grid cell edges above surface'

        ght_var = nc.createVariable('ght', 'f8', ('jpka',))
        ght_var.units = 'm'
        ght_var.long_name = 'Height at grid cell centers above surface'

        e3t_var = nc.createVariable('e3t', 'f8', ('jpka',))
        e3t_var.units = 'm'
        e3t_var.long_name = 'Layer thickness at cell centers'

        e3w_var = nc.createVariable('e3w', 'f8', ('jpka',))
        e3w_var.units = 'm'
        e3w_var.long_name = 'Layer thickness at cell edges'

        # Write data
        ghw_var[:] = ghw
        ght_var[:] = ght
        e3t_var[:] = e3t
        e3w_var[:] = e3w
        # Global attributes
        nc.title = "ABL model vertical grid"
        nc.history = "Created using Python CF-compliant script"
# ------------------------------
# Example usage
# ------------------------------
if __name__ == "__main__":
    config_file = "Abl_vgrid_config.json"
    with open(config_file, "r") as f:
        config = json.load(f)

    ght, ghw, e3t, e3w, theta_s = init_target_grid(
        config["jpka"],
        config["hmax"],
        config["hc"],
        config["theta_s"],
        config["force_z1"],
        config["z1"]
    )
    write_grid_file(config["jpka"], ght, ghw, e3t, e3w, config["outfile"])
    print(f"NetCDF grid file created: {config['outfile']}")

