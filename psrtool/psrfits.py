import time
import numpy as np

from typing import Optional
from astropy.io import fits


# def timeit(func):
#     """Decorator to measure the execution time of a function."""
#     def wrapper(*args, **kwargs):
#         start_time = time.time()
#         result = func(*args, **kwargs)
#         end_time = time.time()
#         print(f"Function {func.__name__} took {end_time - start_time:.4f} seconds")
#         return result
#     return wrapper

# @timeit

def read_fits_header(fitsfile: str) -> tuple[fits.Header, fits.Header]:
    """Read the header of a PSRFITS file.

    Parameters
    ----------
    fitsfile : str
        Path to the PSRFITS file.

    Returns
    -------
    fits.Header
        The header of the PSRFITS file.
    """
    with fits.open(fitsfile, memmap=True) as hdul:
        header0 = hdul[0].header  #type: ignore
        header1 = hdul[1].header  #type: ignore
    return header0, header1

def get_header_time_info(header0: fits.Header, header1: fits.Header) -> tuple[float, float]:
    """Extract time-related information from PSRFITS headers.

    Parameters
    ----------
    header0 : fits.Header
        Primary header of the PSRFITS file.
    header1 : fits.Header
        Secondary header of the PSRFITS file.

    Returns
    -------
    tuple[float, float]
        Tuple containing (start_time, duration).
    """
    start_time = header0['STT_IMJD'] + header0['STT_SMJD'] / 86400.0 + header0['STT_OFFS'] / 86400.0 #type: ignore
    duration = header1['TBIN']  * header1['NSBLK'] * header1['NAXIS2'] #type: ignore
    return start_time, duration

def is_time_contiguous(fitsfile1: str, fitsfile2: str) -> bool:
    """Check if two PSRFITS files are contiguous in time.

    Parameters
    ----------
    fitsfile1 : str
        Path to the first PSRFITS file.
    fitsfile2 : str
        Path to the second PSRFITS file.

    Returns
    -------
    bool
        True if the files are contiguous, False otherwise.
    """
    header0_1, header1_1 = read_fits_header(fitsfile1)
    header0_2, header1_2 = read_fits_header(fitsfile2)

    start_time_1, duration_1 = get_header_time_info(header0_1, header1_1)
    start_time_2, _ = get_header_time_info(header0_2, header1_2)

    end_time_1 = start_time_1 + duration_1 / 86400.0  # convert duration to days
    # print(f"End time of file 1: {end_time_1}, Start time of file 2: {start_time_2}")
    # print(f"Difference: {(start_time_2 - end_time_1)*86400.0} seconds")
    return bool(np.isclose(end_time_1, start_time_2, rtol=0.0, atol=1e-10))


def get_stokesi_data(fitsfile: str) -> np.ndarray:
    """Extract Stokes I data from a PSRFITS file.

    Parameters
    ----------
    fitsfile : str
        Path to the PSRFITS file.
    
    Returns
    -------
    np.ndarray
        Array containing Stokes I data.

    """

    with fits.open(fitsfile, memmap=True) as hdul:
        data = hdul[1].data  #type: ignore
        # Assuming data has shape (nsubints, nchan, npol)
        # Stokes I is usually the sum of the first two polarizations (e.g., XX + YY)    
        header1 = hdul[1].header  #type: ignore
        # print(f"NPOL: {header1['NPOL']}, POL_TYPE: {header1['POL_TYPE']}")
        nchan = header1["NCHAN"]
        dtype = data["DATA"].dtype
        data = data["DATA"].reshape(-1, header1["NPOL"], nchan)
        if header1["NPOL"] == 1:
            # data_ = data["DATA"][:, :, 0, :, 0]
            data_ = data[:, 0, :]  # shape (ntime, nchan)
        elif header1["NPOL"] >= 2:
            # data_ = ((data["DATA"][:, :, 0, :, 0] + data["DATA"][:, :, 1, :, 0]) / 2).astype(data["DATA"].dtype)
            data_ = ((data[:, 0, :] + data[:, 1, :]) / 2).astype(dtype)
        else:
            raise ValueError(f"Unsupported NPOL value: {header1['NPOL']}, POL_TYPE: {header1['POL_TYPE']}")
        
        return data_.reshape(-1, nchan)  # shape (ntime, nchan)


def downsample_data(data: np.ndarray, dchan_factor: int = 1, dt_factor: int = 1) -> np.ndarray:
    """Downsample data in frequency and time.

    Parameters
    ----------
    data : np.ndarray
        Input data array with shape (ntime, nchan).
    dchan_factor : int
        Factor by which to downsample frequency channels.
    dt_factor : int
        Factor by which to downsample time samples.

    Returns
    -------
    np.ndarray
        Downsampled data array.
    """
    dtype = data.dtype
    # Downsample frequency channels
    if dchan_factor > 1:
        ntime, nchan = data.shape
        nchan_ds = nchan // dchan_factor
        data = data[:, :nchan_ds * dchan_factor].reshape(ntime, nchan_ds, dchan_factor).mean(axis=2)

    # Downsample time samples
    if dt_factor > 1:
        ntime, nchan = data.shape
        ntime_ds = ntime // dt_factor
        data = data[:ntime_ds * dt_factor, :].reshape(ntime_ds, dt_factor, nchan).mean(axis=1)

    return data.astype(dtype)