import os
import numpy as np

from astropy.io import fits
from your import Your
from your.formats.filwriter import make_sigproc_object
from tqdm import tqdm

from .psrfits import (
    read_fits_header,
    get_stokesi_data,
    downsample_data,
    get_header_string,
    sigproc_safe_string,
    sigproc_safe_path,
)


def split_fil(filfile: str, outdir: str, split_time_s: float) -> None:
    """Split a filterbank file into chunks based on time duration.
    
    Parameters
    ----------
    filfile : str
        Path to the input filterbank file.
    outdir : str
        Output directory for the split files.
    split_time_s : float
        Time duration in seconds for each chunk.
    
    Raises
    ------
    ValueError
        If split_time_s is not positive.
    """
    if split_time_s <= 0:
        raise ValueError("split_time_s must be positive")
    
    os.makedirs(outdir, exist_ok=True)
    
    # Load filterbank file using Your
    y = Your(filfile)
    
    # Get header information
    nchans = y.your_header.nchans
    foff = y.your_header.foff
    fch1 = y.your_header.fch1
    tsamp = y.your_header.tsamp
    tstart = y.your_header.tstart
    nbits = y.your_header.nbits
    source_name = y.your_header.source_name
    
    # Calculate samples per chunk
    samples_per_chunk = int(split_time_s / tsamp)
    total_samples = y.your_header.nspectra
    
    # Generate output filename base
    base_name = os.path.splitext(os.path.basename(filfile))[0]
    
    # Process data in chunks
    chunk_idx = 0
    current_time = tstart
    processed_samples = 0
    
    with tqdm(total=total_samples, desc="Splitting filterbank") as pbar:
        while processed_samples < total_samples:
            # Determine chunk size (may be smaller for last chunk)
            remaining_samples = total_samples - processed_samples
            current_chunk_size = min(samples_per_chunk, remaining_samples)
            
            # Read chunk data
            data = y.get_data(processed_samples, current_chunk_size, pol=0)
            
            # Create output filename with chunk index and time range
            chunk_duration = current_chunk_size * tsamp
            end_time_s = split_time_s if current_chunk_size == samples_per_chunk else chunk_duration
            outfile = os.path.join(
                outdir, 
                f"{base_name}_chunk_{chunk_idx:04d}.fil"
            )
            
            # Create sigproc object for this chunk
            sig = make_sigproc_object(
                rawdatafile=os.path.basename(outfile),
                source_name=source_name,
                nchans=nchans,
                foff=foff,
                fch1=fch1,
                tsamp=tsamp,
                tstart=current_time,
                nbits=nbits,
                nifs=1,
            )
            
            # Write header and data
            sig.write_header(outfile)
            sig.append_spectra(data, outfile)
            
            # Update counters and time
            processed_samples += current_chunk_size
            current_time += chunk_duration / 86400.0  # Convert to days (MJD)
            chunk_idx += 1
            pbar.update(current_chunk_size)


def split_fits(fitsfile: str, outdir: str, split_time_s: float, 
               dchan_factor: int = 1, dt_factor: int = 1) -> None:
    """Split a PSRFITS file into chunks and save as filterbank files.
    
    Parameters
    ----------
    fitsfile : str
        Path to the input PSRFITS file.
    outdir : str
        Output directory for the split filterbank files.
    split_time_s : float
        Time duration in seconds for each chunk.
    dchan_factor : int
        Factor by which to downsample frequency channels.
    dt_factor : int
        Factor by which to downsample time samples.
    
    Raises
    ------
    ValueError
        If split_time_s is not positive or downsampling factors are invalid.
    """
    if split_time_s <= 0:
        raise ValueError("split_time_s must be positive")
    if dchan_factor < 1 or dt_factor < 1:
        raise ValueError("dchan_factor and dt_factor must be >= 1")
    
    os.makedirs(outdir, exist_ok=True)
    
    # Read FITS headers
    header0, header1 = read_fits_header(fitsfile)
    
    # Extract header information
    bw = abs(header0["OBSBW"])
    centerfreq = header0["OBSFREQ"]
    chan_bw = header1["CHAN_BW"]  # type: ignore
    need_flip = chan_bw > 0
    foff = -abs(chan_bw) * dchan_factor  # type: ignore
    fch1 = centerfreq + (bw / 2)  # type: ignore
    tsamp = header1["TBIN"] * dt_factor  # type: ignore
    nchan = int(header1["NCHAN"]) // dchan_factor  # type: ignore
    nbit = int(header1["NBITS"])  # type: ignore
    
    # Calculate time information
    mjd_start = (
        header0["STT_IMJD"]  # type: ignore
        + header0["STT_SMJD"] / 86400.0  # type: ignore
        + header0["STT_OFFS"] / 86400.0  # type: ignore
    )
    
    tbin = header1["TBIN"]  # type: ignore
    nsblk = int(header1["NSBLK"])  # type: ignore
    naxis2 = int(header1["NAXIS2"])  # type: ignore
    total_samples = nsblk * naxis2
    
    # Calculate samples per chunk
    samples_per_chunk = int(split_time_s / tbin / dt_factor)
    
    # Generate output filename base
    base_name = os.path.splitext(os.path.basename(fitsfile))[0]
    source_name = sigproc_safe_string(
        get_header_string(header0, "SRC_NAME", default="Unknown"),
        default="Unknown",
    )
    
    # Load all data once (or in batches if too large)
    all_data = get_stokesi_data(fitsfile)
    if dchan_factor > 1 or dt_factor > 1:
        all_data = downsample_data(all_data, dchan_factor=dchan_factor, dt_factor=dt_factor)
    if need_flip:
        all_data = all_data[:, ::-1]
    
    # Process data in chunks
    chunk_idx = 0
    current_time = mjd_start
    processed_samples = 0
    total_samples_after_downsampling = all_data.shape[0]
    
    with tqdm(total=total_samples_after_downsampling, desc="Splitting PSRFITS") as pbar:
        while processed_samples < total_samples_after_downsampling:
            # Determine chunk size (may be smaller for last chunk)
            remaining_samples = total_samples_after_downsampling - processed_samples
            current_chunk_size = min(samples_per_chunk, remaining_samples)
            
            # Extract chunk data
            chunk_data = all_data[processed_samples:processed_samples + current_chunk_size, :]
            
            # Create output filename
            outfile = os.path.join(
                outdir,
                f"{base_name}_chunk_{chunk_idx:04d}.fil"
            )
            
            # Create sigproc object for this chunk
            rawdatafile = sigproc_safe_path(outfile, default=os.path.basename(outfile) or outfile)
            sig = make_sigproc_object(
                rawdatafile=rawdatafile,
                source_name=source_name,
                nchans=nchan,
                foff=foff,
                fch1=fch1,
                tsamp=tsamp,
                tstart=current_time,
                nbits=nbit,
                nifs=1,
            )
            
            # Write header and data
            sig.write_header(outfile)
            sig.append_spectra(chunk_data, outfile)
            
            # Update counters and time
            chunk_duration = current_chunk_size * tsamp
            processed_samples += current_chunk_size
            current_time += chunk_duration / 86400.0  # Convert to days (MJD)
            chunk_idx += 1
            pbar.update(current_chunk_size)
