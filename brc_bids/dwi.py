"""
BRC_BIDS: Code to run diffusion pipeline
"""
import logging
import subprocess

LOG = logging.getLogger(__name__)

from . import mappings

def run(subject, session, data_files, outdir):
    dwis = data_files.get("dwi", [])
    if not dwis:
        LOG.info("No DWI files found - will not run diffusion pipelie")
        return

    # Get the echo spacing and PE dir from the metadata
    options = [mappings.options_from_metadata(f.get_metadata(), "dwi") for f in dwis]
    echospacings = [float(o["echospacing"]) for o in options]
    pedirs = [o["pedir"] for o in options]

    # Check the PE direction is consistent and supported
    pe_dir = list(set([pedir.strip("-") for pedir in pedirs]))
    if len(pe_dir) != 1:
        raise ValueError(f"Inconsistent PE dirs for DWI scans: {pedirs}") 
    if pe_dir[0] == "x":
        pe_dir = "1"
    elif pe_dir[0] == "y":
        pe_dir = "2"
    else:
        raise ValueError(f"PE dir not supported: {pe_dir[0]}") 

    # Identify the forward and reverse scans
    fwd = [f for f, pedir in zip(dwis, pedirs) if "-" not in pedir]
    rev = [f for f, pedir in zip(dwis, pedirs) if "-" in pedir]
    fwd_fnames = "@".join([f.path for f in fwd])
    rev_fnames = "@".join([f.path for f in rev])

    # Check the echo spacing is consistent
    diff_echospacing = max(echospacings) - min(echospacings)
    if diff_echospacing > 0.00001:
        raise ValueError(f"Inconsistent echo spacings for DWI scans: {echospacings}") 
    mean_echospacing = sum(echospacings) / len(echospacings)

    cmd = [
        'dMRI_preproc.sh', 
        '--input', fwd_fnames, 
        '--path', outdir, 
        '--subject', f'{subject}_{session}', 
        '--echospacing', str(mean_echospacing),
        '--pe_dir', pe_dir,
        '--qc'
    ]
    if rev_fnames:
        cmd.extend(["--input_2", rev_fnames])

    LOG.info(" ".join(cmd))
    #stdout = subprocess.check_output(cmd)
    #stdout = stdout.decode("UTF-8")
    #LOG.debug(stdout)
