"""
BRC_BIDS: Code to run structural pipeline
"""
import logging
import subprocess

LOG = logging.getLogger(__name__)

def run_struc(subject, session, data_files, outdir):
    t1s = data_files["T1w"]
    t2s = data_files["T2w"]
    if len(t1s) == 0:
        raise RuntimeError(f"Cannot run structural pipeline for subject {subject} session {session} - no T1w image found")
    if len(t1s) > 1:
        LOG.warn(f"More than one T1w image found for subject {subject} session {session}: {t1s} - using first")
    t1 = t1s[0]

    if len(t2s) == 0:
        t2s = [None]
    elif len(t2s) > 1:
        LOG.warn(f"More than one T2w image found for subject {subject} session {session}: {t2s} - using first")
    t2 = t2s[0]

    cmd = ['struc_preproc.sh', '--input', t1, '--path', outdir, '--subject', f'{subject}_{session}']
    if t2:
        cmd += ['--t2', t2]
    LOG.info(" ".join(cmd))
    stdout = subprocess.check_output(cmd)
    stdout = stdout.decode("UTF-8")
    LOG.debug(stdout)
