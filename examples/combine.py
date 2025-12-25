import os
import glob

from psrtool.combinefits import combinefits


def main():
    """Example script to combine multiple PSRFITS files into one filterbank file."""
    fitsfiles = sorted(glob.glob("examples/data/*.fits"))
    outfile = "examples/data/combined_output.fil"
    combinefits(fitsfiles, outfile, dchan_factor=8, dt_factor=2)
    print(f"Combined filterbank file written to {outfile}")

if __name__ == "__main__":
    main()