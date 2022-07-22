"""
BRC_BIDS: Script to run the BRC pipeline from a BIDS dataset
"""
import logging

import bids

LOG = logging.getLogger(__name__)

from . import struc, idps, dwi

def get_image_files(layout):
    """
    Get structure describing all relevant image files found in a BIDS dataset

    :param layout: BIDSLayout structure

    :return dict mapping subjects to a group of sessions. The session group is a dict mapping
            session ID to session dict. Each session is a dict mapping file suffixes asl, m0scan, 
            and T1w to lists of corresponding BIDSImageFile instances
    """
    data_files = {}
    for subj in layout.get_subjects():
        data_files[subj] = {}
        sessions = layout.get_sessions(subject=subj)
        if not sessions:
            # Deal with case where there is no session level
            sessions = [None]
        for sess in sessions:
            LOG.info("Getting ASL data for subject %s in session %s" % (subj, sess))
            data_files[subj][sess] = {}
            for suffix in ("asl", "m0scan", "T1w", "T2w", "dwi"):
                data_files[subj][sess][suffix] = []
                for fobj in layout.get(subject=subj, session=sess, suffix=suffix):
                    if isinstance(fobj, bids.layout.models.BIDSImageFile):
                        LOG.debug("Found %s image: %s %s" % (suffix.upper(), fobj.filename, fobj.entities["suffix"]))
                        data_files[subj][sess][suffix].append(fobj)

    return data_files

def run(bidsdir, outdir):
    layout = bids.BIDSLayout(bidsdir)
    image_files = get_image_files(layout)

    subjdirs = []
    for subject, sessions in image_files.items():
        for session, data_files in sessions.items():

            # Note structural pipeline will throw exception if no T1 image available - this is fine because structural
            # processing is required for the rest of the pipeline
            struc.run(subject, session, data_files, outdir)
            dwi.run(subject, session, data_files, outdir)
            #perf.run(subject, session, data_files, outdir)
            subjdirs.append(f"{subject}_{session}")
    idps.run(subjdirs, outdir)
    #run_qc_extract(subjdirs, outdir)

