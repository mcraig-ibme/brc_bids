"""
BRC_BIDS: Code to run structural pipeline
"""
import logging
import subprocess

LOG = logging.getLogger(__name__)

from . import utils

SINGULARITY_IMAGE="/software/imaging/singularity_images/poldracklab_mriqc-2021-01-30-767af1135fae.simg"

def run(bidsdir, outdir, cluster=False, dep_job=None):
    cmd = ['singularity', 'run', '--cleanenv', SINGULARITY_IMAGE, bidsdir, outdir, 'participant', '--no-sub']
    return utils.submit_cmd(cmd, cluster, dep_job, minutes=600, ram=64000)
