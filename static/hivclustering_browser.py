import hivclustering.networkbuild
from hivclustering import *

# TODO: Discuss auto-profile - only goes to stdout, can't be redirected to file
# PAIRWISE_DIST_FILE_NAME is a constant defined in the javascript code 
hivclustering.networkbuild.sys.argv = ['', '--input', PAIRWISE_DIST_FILE_NAME, '--format', 'plain', '--auto-profile', '0']
hivclustering.networkbuild.build_a_network()