"""
BRC_BIDS: Defines mapping of BIDS metadata keys to pipeline options
"""

import logging

LOG = logging.getLogger(__name__)

def _is_casl(js_dict, options):
    label_type = js_dict.get('LabelingType', js_dict['ArterialSpinLabelingType'])
    if label_type != 'PASL': 
        return True

def _calc_bolus(js_dict, options):
    if not options.get("casl", False) and "BolusCutOffTImingSequence" in js_dict:
        return js_dict['BolusCutOffTimingSequence']
    elif 'LabelingDuration' in js_dict:
        return js_dict['LabelingDuration']

def _calc_slicedt(js_dict, options):
    if "SliceTiming" in js_dict:
        times = js_dict['SliceTiming']
        dts = [ pair[0]-pair[1] for pair in zip(times[1:], times[:-1]) ] 
        return sum(dts) / len(dts)

def _interpret_pedir(js_dict, options):
    dir_map = {"i" : "x", "j" : "y", "k" : "z"}
    pedir = js_dict['PhaseEncodingDirection']
    oxasl_pedir = dir_map[pedir.strip("-")]
    if pedir.count('-'):
        oxasl_pedir = '-' + oxasl_pedir
    return oxasl_pedir

def _postproc_asl(metadata, options):
    # Find out what field we're using for timings based on whether it's PCASL or PASL
    if options.get('casl', False):
        ttype, otype = 'plds', 'tis'
    else:
        ttype, otype = 'tis', 'plds'

    # Remove unused timings field and make sure it is a list
    options.pop(otype, None)
    if isinstance(options[ttype], (int, float)):
        options[ttype] = [options[ttype]]

def _postproc_cblip(metadata, options):
    if "totalreadouttime" in options:
        # We need the effective echo spacing instead
        readouttime = options.pop("totalreadouttime")
        pedir = options.get("pedir", None)
        if not pedir:
            LOG.warn("Found total readout time for cblip image but no PE dir - cannot calculate effective echo spacing")
        else:
            img_dims = metadata["img_shape"]
            if "x" in pedir:
                size = img_dims[0]
            elif "y" in pedir:
                size = img_dims[1]
            elif "z" in pedir:
                size = img_dims[2]
            # FIXME what if pedir invalid
            options["echospacing"] = readouttime / (size-1)

METADATA_MAPPINGS = {

    "asl" : [
        # ASL options
        ('order', None),
        ('tis', 'InitialPostLabelDelay'),
        ('tis', 'PostLabelingDelay'),
        ('plds', 'InitialPostLabelDelay'),
        ('plds', 'PostLabelingDelay'),
        ('tes', 'EchoTime'),
        ('ntis', None),
        ('nplds', None),
        ('rpts', None),
        ('nphases', None),
        ('nenc', None),
        ('casl', _is_casl),
        ('bolus', _calc_bolus),
        ('slicedt', _calc_slicedt),
        ('sliceband', None),
        ('artsupp', 'VascularCrushing'),
        (None, _postproc_asl),
    ],

    "struct" : [
        # Structural options
        ('struc', None), 
        ('fsl_anat', None), 
    ],

    "calib" : [
        # Calibration options 
        ('calib-alpha', None),
        ('tr', "RepetitionTimePreparation"),
        ('tr', "RepetitionTime"),
        ('te', 'EchoTime'),
    ],

    "cblip" : [
        # Distortion correction options
        ('echospacing', "EffectiveEchoSpacing"),
        ('totalreadouttime', "TotalReadoutTime"),
        ('pedir', _interpret_pedir),
        (None, _postproc_cblip),
    ],

    "dwi" : [
        # DWI data options
        ('echospacing', "EffectiveEchoSpacing"),
        ('pedir', _interpret_pedir),
    ]
}

def options_from_metadata(metadata, filetype, **extra_metadata):
    """
    Get the relevant options from JSON metadata
    
    :param metadata: Metadata dictionary
    :param filetype: Type of file metadata describes: asl, calib, cblip, struct, dwi
    :param extra_metadata: Keyword arguments to override metadata from JSON file
    """
    config = {}
    metadata = dict(metadata)
    metadata.update(extra_metadata)

    for option_key, md_key in METADATA_MAPPINGS[filetype]:
        val = None
        if type(md_key) is str and md_key in metadata:
            val = metadata.get(md_key)
        elif callable(md_key):
            val = md_key(metadata, config)

        if val is not None:
            config[option_key] = val

    return config
