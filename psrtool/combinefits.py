
import os
import numpy as np

from concurrent.futures import ThreadPoolExecutor
from typing import Optional
from astropy.io import fits
from tqdm import tqdm
from your.formats.filwriter import make_sigproc_object


from .psrfits import (
    read_fits_header,
    get_header_time_info,
    is_time_contiguous,
    get_stokesi_data,
    downsample_data,
    get_header_string,
    sigproc_safe_string,
    sigproc_safe_path,
)


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
    for i, fitsfile in enumerate(sorted_files):
        if i > 0:
            if not is_time_contiguous(sorted_files[i - 1], fitsfile):
                raise ValueError(f"Files {sorted_files[i - 1]} and {fitsfile} are not time contiguous.")

    # Base metadata from the first file (after downsampling factors applied)
    baseheader0, baseheader1 = read_fits_header(sorted_files[0])
    bw = abs(baseheader0["OBSBW"])
    centerfreq = baseheader0["OBSFREQ"]
    chan_bw = baseheader1["CHAN_BW"]  # type: ignore
    need_flip = chan_bw > 0
    foff = -abs(chan_bw) * dchan_factor  # type: ignore
    fch1 = centerfreq + (bw / 2)  # type: ignore
    tsamp = baseheader1["TBIN"] * dt_factor  # type: ignore
    nchan = int(baseheader1["NCHAN"]) // dchan_factor  # type: ignore
    nbit = baseheader1["NBITS"]
    ra_deg, dec_deg = baseheader0["RA"], baseheader0["DEC"]
    mjd_start = baseheader0["STT_IMJD"] + baseheader0["STT_SMJD"] / 86400.0 + baseheader0["STT_OFFS"] / 86400.0  # type: ignore

    # Pre-compute total time samples to preallocate output
    total_time = 0
    for fitsfile in sorted_files:
        _, header1 = read_fits_header(fitsfile)
        ntime_file = int(header1["NSBLK"] * header1["NAXIS2"])  # type: ignore
        ntime_file //= dt_factor
        total_time += ntime_file

    combined_data_array: Optional[np.ndarray] = None
    write_idx = 0

    def _load_and_downsample(path: str) -> np.ndarray:
        data = get_stokesi_data(path)
        if dchan_factor > 1 or dt_factor > 1:
            data = downsample_data(data, dchan_factor=dchan_factor, dt_factor=dt_factor)
        if need_flip:
            data = data[:, ::-1]
        return data

    max_workers = min(8, len(sorted_files)) if len(sorted_files) > 1 else 1
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(_load_and_downsample, f) for f in sorted_files]
        for fut in tqdm(futures, desc="Combining PSRFITS files"):
            data = fut.result()
            if combined_data_array is None:
                combined_data_array = np.empty((total_time, data.shape[1]), dtype=data.dtype)
            nrows = data.shape[0]
            combined_data_array[write_idx:write_idx + nrows] = data # type: ignore
            write_idx += nrows

    if combined_data_array is None:
        raise ValueError("No data found to combine.")

    # Write combined data to new PSRFITS file
    ntime, nchan = combined_data_array.shape
    source_name = sigproc_safe_string(
        get_header_string(baseheader0, "SRC_NAME", default="Unknown"),
        default="Unknown",
    )
    rawdatafile = sigproc_safe_path(outfile, default=os.path.basename(outfile) or outfile)
    sig = make_sigproc_object(
        rawdatafile=rawdatafile,
        source_name=source_name,
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
