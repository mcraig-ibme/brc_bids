"""
OXASL_BIDS: Miscellaneous utilities
"""
import json
import os
import logging
import subprocess

import nibabel as nib

LOG = logging.getLogger(__name__)

def get_job_id(stdout):
    """
    Get last job ID submitted by a command
    """
    last_id = None
    for line in stdout.splitlines():
        if "jobid" in line.lower():
            last_id = line.split(":")[1].strip()
    return last_id

def submit_cmd(cmd, cluster, dep_job, minutes=5, ram=None):
    if cluster:
        sub_cmd = ["fsl_sub", "-T", str(minutes)]
        if dep_job:
            LOG.info(f"Dep job={dep_job}")
            sub_cmd.extend(["-j", dep_job])
        if ram:
            LOG.info(f"RAM={ram} Mb")
            sub_cmd.extend(["-R", str(ram)])

        sub_cmd.extend(cmd)
        LOG.info(" ".join(sub_cmd))
        stdout = subprocess.check_output(sub_cmd)
        stdout = stdout.decode("UTF-8")
        LOG.debug(stdout)
        return stdout.strip()
    else:
        LOG.info(" ".join(cmd))
        stdout = subprocess.check_output(cmd)
        stdout = stdout.decode("UTF-8")
        LOG.debug(stdout)
        return get_job_id(stdout)

def bids_filename(suffix, subject, session, labeldict=None):
    """
    Get a BIDS style filename
    
    :param suffix: The image type suffix, e.g. T1w
    :param subject: Subject ID
    :param session: Session ID
    :param labeldict: Dictionary of labels to be embedded in the filename
    """
    fname = f"sub-{subject}"
    if session:
        fname += f"_ses-%{session}"
    if labeldict:
        for key, value in labeldict.items():
            fname += f"_{key}-{value}"
    fname += f"_{suffix}"
    return fname

def find_img(fname):
    """
    Find an image from a filename without an extension

    :return: Tuple of full filename, extension (including .) or None, None if not found
    """
    for ext in (".nii.gz", ".nii"):
        if os.path.exists(fname + ext):
            return fname + ext, ext
    return None, None

def load_img(fname):
    """
    Load an image

    :return: Tuple of nii structure, JSON metadata dictionary
    """
    nii = nib.load(fname)
    json_filename = fname[:fname.index(".nii")] + ".json"
    with open(json_filename, "r") as f:
        metadata = json.load(f)
    metadata["img_shape"] = nii.shape

    return nii, metadata
