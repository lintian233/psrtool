#!/usr/bin/env python3

import os
import argparse

from psrtool.combinefits import combinefits
from psrtool.fits2fil import fits2fil, fil2fits


def combinefitscli():
    parser = argparse.ArgumentParser(
        description="Combine multiple PSRFITS files into a single filterbank file."
    )
    parser.add_argument(
        "fitsfiles",
        nargs="+",
        help="Input PSRFITS files to combine.",
    )
    parser.add_argument(
        "-o",
        "--outfile",
        required=True,
        help="Output filterbank file name.",
    )
    parser.add_argument(
        "-c",
        "--dchan-factor",
        type=int,
        default=1,
        help="Frequency channel downsampling factor.",
    )
    parser.add_argument(
        "-t",
        "--dt-factor",
        type=int,
        default=1,
        help="Time sample downsampling factor.",
    )

    args = parser.parse_args()

    combinefits(
        args.fitsfiles,
        args.outfile,
        dchan_factor=args.dchan_factor,
        dt_factor=args.dt_factor,
    )


def fits2filcli():
    parser = argparse.ArgumentParser(
        description="Convert a PSRFITS file to a filterbank (.fil) file."
    )
    parser.add_argument(
        "fitsfile",
        help="Input PSRFITS file.",
    )
    parser.add_argument(
        "-o",
        "--outfile",
        required=True,
        help="Output filterbank file name.",
    )
    parser.add_argument(
        "-c",
        "--dchan-factor",
        type=int,
        default=1,
        help="Frequency channel downsampling factor.",
    )
    parser.add_argument(
        "-t",
        "--dt-factor",
        type=int,
        default=1,
        help="Time sample downsampling factor.",
    )

    args = parser.parse_args()

    fits2fil(
        args.fitsfile,
        args.outfile,
        dchan_factor=args.dchan_factor,
        dt_factor=args.dt_factor,
    )


def fil2fitscli():
    parser = argparse.ArgumentParser(
        description="Convert a filterbank (.fil) file to a PSRFITS file."
    )
    parser.add_argument(
        "filfile",
        help="Input filterbank file.",
    )
    parser.add_argument(
        "-o",
        "--outfile",
        required=True,
        help="Output PSRFITS file name.",
    )

    args = parser.parse_args()

    fil2fits(
        args.filfile,
        args.outfile,
    )
