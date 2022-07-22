"""
oxasl_bids: BIDS interface for the oxasl pipeline

Usage:
oxasl_bids bids --bidsdir <bids_directory> [... additional oxasl arguments]
oxasl_bids img --img <img file> --img-type <type>
oxasl_bids bidsout --oxasl-output <output folder>

'bids' outputs commands to run oxasl on a BIDS data set
'img' output a command to run oxasl on a single ASL image with JSON metadata
'bidsout' converts an oxasl output directory to BIDS format
"""

import argparse
import logging
import sys

from . import brc

LOG = logging.getLogger(__name__)

def _parse_args(args):
    # FIXME not used at present
    ret = {}
    skip = False
    for idx, arg in enumerate(args):
        if skip:
            skip = False
            continue

        if arg.startswith("-"):
            arg = arg.strip("-")
            parts = arg.split("=", 1)
            if len(parts) == 2:
                k, v = parts
            elif idx < len(args)-1 and not args[idx+1].startswith("-"):
                k = parts[0]
                v = args[idx+1]
                skip = True
            else:
                k = parts[0]
                v = ""
            ret[k.strip()] = v.strip()
        else:
            raise RuntimeError("Invalid argument: %s (does not start with -)" % arg)
    return ret

class ArgumentParser(argparse.ArgumentParser):
    def __init__(self, **kwargs):
        argparse.ArgumentParser.__init__(self, prog="brc_bids", add_help=True, **kwargs)
        self.add_argument('--bidsdir', help="Path to BIDS data set")
        self.add_argument('-o', '--output', help="Path to output directory. Subject directory will be created here")
        self.add_argument('--overwrite', help="Overwrite output directory if already exists")
        self.add_argument('--debug', help="Enable debug logging", action='store_true')

def main():
    parser = ArgumentParser()
    args, remainder = parser.parse_known_args()
    #custom_args = _parse_args(remainder)

    _setup_logging(args)
    brc.run(args.bidsdir, args.output)

def _setup_logging(args):
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.WARN)

    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logging.getLogger().addHandler(handler)

if __name__ == "__main__":
    main()
