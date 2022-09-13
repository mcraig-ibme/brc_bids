"""
BRC_BIDS: Code to run IDP extraction
"""
import logging
import os
import subprocess

LOG = logging.getLogger(__name__)

def run(subjdirs, outdir, cluster=False, dep_job=None):
    subjfile = os.path.join(outdir, "subjs.txt")
    with open(subjfile, "w") as f:
        for subjdir in subjdirs:
            f.write(f'{subjdir}')
    idpdir = os.path.join(outdir, 'idps')
    cmd = ['idp_extract.sh', '--in', subjfile, '--indir', outdir, '--outdir', idpdir]
    LOG.info(" ".join(cmd))
    #stdout = subprocess.check_output(cmd)
    #stdout = stdout.decode("UTF-8")
    #LOG.debug(stdout)
