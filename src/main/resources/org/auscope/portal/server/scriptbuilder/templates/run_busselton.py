"""Script for running a tsunami inundation scenario for Cairns, QLD Australia.

Source data such as elevation and boundary data is assumed to be available in
directories specified by project.py
The output sww file is stored in directory named after the scenario, i.e
slide or fixed_wave.

The scenario is defined by a triangular mesh created from project.polygon,
the elevation data and a tsunami wave generated by a submarine mass failure.

Geoscience Australia, 2004-present
"""

"""ANUGA modelling using busselton netCDF data"""


#------------------------------------------------------------------------------
# Import necessary modules
#------------------------------------------------------------------------------
# Standard modules
import os
import time
import sys
from math import sin, pi, exp
import numpy as np
import VHIRL_conversions
import subprocess

# Related major packages
import anuga

######################################################
####### Do not change anything above this line #######

# Definition of file names and polygons
""" Common filenames and locations for topographic data, meshes and outputs.
    This file defines the parameters of the scenario you wish to run.
"""

# Filename for input data (NetCDF format)
dataset = '${input_dataset}'

#from anuga.utilities.system_tools import get_user_name, get_host_name
from time import localtime, strftime, gmtime
from os.path import join, exists


#------------------------------------------------------------------------------
# Runtime parameters
#------------------------------------------------------------------------------
v_cache = False
v_verbose = True

#------------------------------------------------------------------------------
# Define scenario as either slide or fixed_wave. Choose one.
#------------------------------------------------------------------------------
scenario = 'fixed_wave' # Huge wave applied at the boundary

periodT=785
heightH=3.047
scaleF=2.06
AA=heightH/2
BB=2*np.pi/(periodT)
DD=2400

WaveForm=lambda t: [AA*(1/np.exp(-periodT/scaleF/DD))*np.sin(BB*t)*np.exp(-t/DD), 0, 0]

#------------------------------------------------------------------------------
# Filenames
#------------------------------------------------------------------------------
name_stem = scenario_name = '${name_stem}'
event_number =  'T' + str(periodT)
rp = 10000

meshname = name_stem + '.msh'

# Filename for locations where timeseries are to be produced
gauge_filename = 'gauges_busselton.csv'

#------------------------------------------------------------------------------
# Domain definitions
#------------------------------------------------------------------------------
# bounding polygon for study area
bounding_polygon = anuga.read_polygon('busselton_extent_edit.csv')

A = anuga.polygon_area(bounding_polygon) / 1000000.0
print 'Area of bounding polygon = %.2f km^2' % A

#------------------------------------------------------------------------------
# Interior region definitions
#------------------------------------------------------------------------------
# Read interior polygons
poly_1 = anuga.read_polygon('busselton_1km.csv')
poly_2 = anuga.read_polygon('bunbury_1km_extend.csv')
poly_3 = anuga.read_polygon('busselton_20m.csv')
#poly_island2 = anuga.read_polygon('islands2.csv')
#poly_island3 = anuga.read_polygon('islands3.csv')
#poly_shallow = anuga.read_polygon('shallow.csv')

# Optionally plot points making up these polygons
#plot_polygons([bounding_polygon, poly_cairns, poly_island0, poly_island1,
#               poly_island2, poly_island3, poly_shallow],
#               style='boundingpoly', verbose=False)

# Define resolutions (max area per triangle) for each polygon
# Make these numbers larger to reduce the number of triangles in the model,
# and hence speed up the simulation

# bigger base_scale == less triangles
just_fitting = False
#base_scale = 2000 # 635763 # 112sec fit
#base_scale = 50000 # 321403 # 69sec fit
#base_scale = 100000 # 162170 triangles # 45sec fit
#base_scale = 400000 # 42093
base_scale = ${base_scale}
default_res = 25 * base_scale   # Background resolution
zoom1_res = base_scale *10
zoom2_res = base_scale /4

# Define list of interior regions with associated resolutions
interior_regions = [[poly_1,  zoom2_res],
                    [poly_2, zoom2_res],
                    [poly_3, zoom1_res]]

#------------------------------------------------------------------------------
# Data for exporting ascii grid
#------------------------------------------------------------------------------
eastingmin = 286174
eastingmax = 392955
northingmin = 6267810
northingmax = 6456235

# Smaller area for export
eastingmin = 333700
eastingmax = 380800
northingmin = 6272000
northingmax = 6317000

#------------------------------------------------------------------------------
# Data for Tides
#------------------------------------------------------------------------------
#v_tide = 0.0
v_tide = ${tide}


#alpha = 0.1             # smoothing parameter for mesh
#friction=0.01           # manning's friction coefficient
#starttime=0             # start time for simulation
#finaltime=80000         # final time for simulation


####### Do not change anything below this line #######
######################################################

time00 = time.time()
#------------------------------------------------------------------------------
# Preparation of topographic data
# Convert GEOTIFF to NC to ASC 2 DEM 2 PTS using source data and store result in source data
#------------------------------------------------------------------------------


# Create nc from geotif data
VHIRL_conversions.geotif2nc(dataset, '/tmp/'+name_stem)

# Create ASC from nc data
VHIRL_conversions.nc2asc('/tmp/'+name_stem, name_stem)

# Create DEM from asc data
anuga.asc2dem(name_stem+'.asc', use_cache=v_cache, verbose=v_verbose)

# Create pts file for onshore DEM
anuga.dem2pts(name_stem+'.dem', use_cache=v_cache, verbose=v_verbose)

#------------------------------------------------------------------------------
# Create the triangular mesh and domain based on
# overall clipping polygon with a tagged
# boundary and interior regions as defined in project.py
#------------------------------------------------------------------------------
domain = anuga.create_domain_from_regions(bounding_polygon,
                                    boundary_tags={'land_sse': [0],
                                                   'land_s': [1],
                                                   'bottom': [2],
                                                   'ocean_wsw': [3],
                                                   'ocean_w': [4],
                                                   'ocean_wnw': [5],
                                                   'top': [6],
                                                   'land_nne': [7],
                                                   'land_ese': [8],
                                                   'land_se': [9]},
                                    maximum_triangle_area=default_res,
                                    mesh_filename=meshname,
                                    interior_regions=interior_regions,
                                    use_cache=v_cache,
                                    verbose=v_verbose)

# Print some stats about mesh and domain
print 'Number of triangles = ', len(domain)
print 'The extent is ', domain.get_extent()
print domain.statistics()

#------------------------------------------------------------------------------
# Setup parameters of computational domain
#------------------------------------------------------------------------------
domain.set_name('busselton_' + scenario) 	  # Name of sww file
domain.set_datadir('.')                       # Store sww output here
domain.set_minimum_storable_height(0.01)      # Store only depth > 1cm
domain.set_flow_algorithm('tsunami')



#------------------------------------------------------------------------------
# Setup initial conditions
#------------------------------------------------------------------------------
tide = v_tide
domain.set_quantity('stage', tide)
domain.set_quantity('friction', 0.0)


domain.set_quantity('elevation',
                    filename=name_stem + '.pts',
                    use_cache=v_cache,
                    verbose=v_verbose,
                    alpha=0.1)


time01 = time.time()
print 'That took %.2f seconds to fit data' %(time01-time00)

if just_fitting:
    import sys
    sys.exit()

#------------------------------------------------------------------------------
# Setup boundary conditions
#------------------------------------------------------------------------------
print 'Available boundary tags', domain.get_boundary_tags()

Bd = anuga.Dirichlet_boundary([tide, 0, 0]) # Mean water level
Bs = anuga.Transmissive_stage_zero_momentum_boundary(domain) # Neutral boundary

if scenario == 'fixed_wave':
    # Define tsunami wave (in metres and seconds).
    Bw = anuga.Time_boundary(
                        domain=domain,
                        function=lambda t: [(20*np.sin(t*np.pi/(60*10)))*np.exp(-t/600), 0, 0])

    domain.set_boundary({'land_sse': Bs,
                        'land_s': Bs,
                        'bottom': Bs,
                        'ocean_wsw': Bw,
                        'ocean_w': Bw,
                        'ocean_wnw': Bw,
                        'top': Bs,
                        'land_nne': Bs,
                        'land_ese': Bs,
                        'land_se': Bs})


#------------------------------------------------------------------------------
# Evolve system through time
#------------------------------------------------------------------------------
import time
t0 = time.time()

from numpy import allclose


if scenario == 'fixed_wave':
    # Save every two mins leading up to wave approaching land
    for t in domain.evolve(yieldstep=2*60, finaltime=5000):
        print domain.timestepping_statistics()
        print domain.boundary_statistics(tags='ocean_wnw')

    # Save every 30 secs as wave starts inundating ashore
    for t in domain.evolve(yieldstep=60*0.5, finaltime=7000,
                           skip_initial_step=True):
        print domain.timestepping_statistics()
        print domain.boundary_statistics(tags='ocean_wnw')

print 'That took %.2f seconds' %(time.time()-t0)

print 'Total time: %.2f seconds' %(time.time()-time00)


#------------------------------------------------------------------------------
# Upload Result Files to Cloud Storage
#------------------------------------------------------------------------------
def cloudUpload(inFilePath, cloudKey):
    cloudBucket = os.environ["STORAGE_BUCKET"]
    cloudDir = os.environ["STORAGE_BASE_KEY_PATH"]
    queryPath = (cloudBucket + "/" + cloudDir + "/" + cloudKey).replace("//", "/")
    retcode = subprocess.call(["cloud", "upload", cloudKey, inFilePath, "--set-acl=public-read"])
    print ("cloudUpload: " + inFilePath + " to " + queryPath + " returned " + str(retcode))


# Upload results
print 'Uploading result files'
cloudUpload("${name_stem}_UTM.nc", "${name_stem}_UTM.nc")
cloudUpload("${name_stem}.asc", "${name_stem}.asc")
cloudUpload("${name_stem}.prj", "${name_stem}.prj")
cloudUpload("${name_stem}.dem", "${name_stem}.dem")
cloudUpload("${name_stem}.pts", "${name_stem}.pts")
cloudUpload("${name_stem}.msh", "${name_stem}.msh")
cloudUpload("${name_stem}_fixed_wave.sww", "${name_stem}_fixed_wave.sww")