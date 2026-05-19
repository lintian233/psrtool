#!/usr/bin/env python3
"""
Example usage of the splittool module.

This script demonstrates how to split filterbank and PSRFITS files
into time chunks.
"""

from psrtool.splittool import split_fil, split_fits


def example_split_filterbank():
    """Example: Split a filterbank file into 64-second chunks."""
    filfile = "path/to/your/file.fil"
    outdir = "output/splits"
    split_time_s = 64.0  # 64 seconds per chunk
    
    print(f"Splitting {filfile} into {split_time_s}s chunks...")
    split_fil(filfile, outdir, split_time_s=split_time_s)
    print(f"Output files saved to {outdir}")


def example_split_psrfits():
    """Example: Split a PSRFITS file into 64-second chunks as filterbank."""
    fitsfile = "path/to/your/file.fits"
    outdir = "output/splits"
    split_time_s = 64.0  # 64 seconds per chunk
    
    print(f"Splitting {fitsfile} into {split_time_s}s chunks...")
    split_fits(
        fitsfile,
        outdir,
        split_time_s=split_time_s,
        dchan_factor=1,
        dt_factor=1,
    )
    print(f"Output files saved to {outdir}")


def example_split_psrfits_with_downsampling():
    """Example: Split a PSRFITS file with downsampling factors."""
    fitsfile = "path/to/your/file.fits"
    outdir = "output/splits_downsampled"
    split_time_s = 64.0
    dchan_factor = 2  # Downsample frequency by 2
    dt_factor = 4     # Downsample time by 4
    
    print(f"Splitting {fitsfile} into {split_time_s}s chunks with downsampling...")
    split_fits(
        fitsfile,
        outdir,
        split_time_s=split_time_s,
        dchan_factor=dchan_factor,
        dt_factor=dt_factor,
    )
    print(f"Output files saved to {outdir}")


if __name__ == "__main__":
    # Uncomment the example you want to run
    # example_split_filterbank()
    # example_split_psrfits()
    # example_split_psrfits_with_downsampling()
    
    print("This is an example script. Please uncomment the example you want to run.")
