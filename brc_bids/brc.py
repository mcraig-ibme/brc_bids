"""
BRC_BIDS: Script to run the BRC pipeline from a BIDS dataset
"""
import logging
import os

import bids

LOG = logging.getLogger(__name__)

from . import struc, idps, dwi, mriqc

def get_image_files(layout):
    """
    Get structure describing all relevant image files found in a BIDS dataset

    :param layout: BIDSLayout structure

    :return dict mapping subjects to a group of sessions. The session group is a dict mapping
            session ID to session dict. Each session is a dict mapping file suffixes asl, m0scan, 
            T1w, T2w and dwi to lists of corresponding BIDSImageFile instances
    """
    data_files = {}
    for subj in layout.get_subjects():
        data_files[subj] = {}
        sessions = layout.get_sessions(subject=subj)
        if not sessions:
            # Deal with case where there is no session level
            sessions = [None]
        for sess in sessions:
            LOG.info(f"Getting BIDS images for subject {subj} in session {sess}")
            data_files[subj][sess] = {}
            for suffix in ("asl", "m0scan", "T1w", "T2w", "dwi"):
                data_files[subj][sess][suffix] = []
                for fobj in layout.get(subject=subj, session=sess, suffix=suffix):
                    if isinstance(fobj, bids.layout.models.BIDSImageFile):
                        LOG.debug(f"Found {suffix.upper()} image: {fobj.filename} {fobj.entities['suffix']}")
                        data_files[subj][sess][suffix].append(fobj)

    return data_files

def run(args):
    LOG.info("BRC-BIDS")
    LOG.info(f"Cluster mode: {args.cluster}")
    layout = bids.BIDSLayout(args.bidsdir)

    if args.mriqc:
        # MRIQC is a BIDS application independent of the rest of the BRC pipeline
        LOG.info(f"Running MRIQC on dataset")
        mriqc.run(args.bidsdir, args.output, cluster=args.cluster)

    image_files = get_image_files(layout)
    subjdirs, last_job = [], None
    for subject, sessions in image_files.items():
        for session, data_files in sessions.items():

            # Note structural pipeline will throw exception if no T1 image available - this is fine because structural
            # processing is required for the rest of the pipeline
            last_job = struc.run(subject, session, data_files, args.output, cluster=args.cluster)
            #last_job = dwi.run(subject, session, data_files, output, cluster=args.cluster, dep_job=struc_job)
            #perf.run(subject, session, data_files, output)
            subjdirs.append(f"{subject}_{session}")

    #idps.run(subjdirs, output, cluster=cluster, dep_job=last_job)
    #qc.run(subjdirs, output)
