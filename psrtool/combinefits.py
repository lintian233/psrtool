
import time
import your
import numpy as np

from typing import Optional
from astropy.io import fits
from your.formats.filwriter import make_sigproc_object

from .psrfits import read_fits_header, get_header_time_info, is_time_contiguous, get_stokesi_data, downsample_data


def combinefits(fitsfiles: list[str], outfile: str, dchan_factor: int = 1, dt_factor: int = 1) -> None:
    """Combine multiple PSRFITS files into a single PSRFITS file.

    Parameters
    ----------
    fitsfiles : list[str]
        List of input PSRFITS file paths to combine.
    outfile : str
        Output filterbank file path.
    dchan_factor : int
        Factor by which to downsample frequency channels.
    dt_factor : int
        Factor by which to downsample time samples.
    """

    sorted_files = sorted(fitsfiles)
    combined_data = []
    for i, fitsfile in enumerate(sorted_files):
        if i > 0:
            if not is_time_contiguous(sorted_files[i - 1], fitsfile):
                raise ValueError(f"Files {sorted_files[i - 1]} and {fitsfile} are not time contiguous.")

    for fitsfile in sorted_files:
        data = get_stokesi_data(fitsfile)
        if dchan_factor > 1 or dt_factor > 1:
            data = downsample_data(data, dchan_factor=dchan_factor, dt_factor=dt_factor)
        combined_data.append(data)
    
    combined_data_array = np.vstack(combined_data)

    # Write combined data to new PSRFITS file
    baseheader0, baseheader1 = read_fits_header(sorted_files[0])
    ntime, nchan = combined_data_array.shape
    nbit = baseheader1["NBITS"]
    bw = baseheader0["OBSBW"]
    centerfreq = baseheader0["OBSFREQ"]
    foff = baseheader1["CHAN_BW"] * dchan_factor #type: ignore
    fch1 = centerfreq - (bw / 2) if foff > 0 else centerfreq + (bw / 2)  #type: ignore
    tsamp = baseheader1["TBIN"] * dt_factor  #type: ignore
    ra_deg, dec_deg = baseheader0["RA"], baseheader0["DEC"]
    mjd_start = baseheader0["STT_IMJD"] + baseheader0["STT_SMJD"] / 86400.0 + baseheader0["STT_OFFS"] / 86400.0  #type: ignore

    sig = make_sigproc_object(
        rawdatafile=outfile,
        source_name=baseheader0["SRC_NAME"], #type: ignore
        nchans=nchan,
        foff=foff,
        fch1=fch1,
        tsamp=tsamp,
        tstart=mjd_start,
        nbits=nbit, #type: ignore
        nifs=1,
    )
    sig.write_header(outfile)
    sig.append_spectra(combined_data_array, outfile)
    # print(f"[OK] Combined PSRFITS written to {outfile}")



