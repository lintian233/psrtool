import os
import numpy as np

from your import Your
from your.formats.filwriter import make_sigproc_object
from your.writer import Writer

from .psrfits import read_fits_header, get_stokesi_data, downsample_data


def fits2fil(fitsfile: str, outfile: str, dchan_factor: int = 1, dt_factor: int = 1) -> None:
    """Convert a PSRFITS file to a filterbank (.fil) file, optionally downsampling."""
    if dchan_factor < 1 or dt_factor < 1:
        raise ValueError("dchan_factor and dt_factor must be >= 1")

    outdir = os.path.dirname(outfile)
    if outdir:
        os.makedirs(outdir, exist_ok=True)

    header0, header1 = read_fits_header(fitsfile)
    bw = header0["OBSBW"]
    centerfreq = header0["OBSFREQ"]
    foff = header1["CHAN_BW"] * dchan_factor  # type: ignore
    fch1 = centerfreq - (bw / 2) if foff > 0 else centerfreq + (bw / 2) # type: ignore
    tsamp = header1["TBIN"] * dt_factor  # type: ignore
    nchan = int(header1["NCHAN"]) // dchan_factor # type: ignore
    nbit = int(header1["NBITS"]) # type: ignore
    mjd_start = (
        header0["STT_IMJD"]  # type: ignore
        + header0["STT_SMJD"] / 86400.0  # type: ignore
        + header0["STT_OFFS"] / 86400.0  # type: ignore
    )

    sig = make_sigproc_object(
        rawdatafile=outfile,
        source_name=header0["SRC_NAME"], # type: ignore
        nchans=nchan,
        foff=foff,
        fch1=fch1,
        tsamp=tsamp,
        tstart=mjd_start,
        nbits=nbit,
        nifs=1,
    )
    sig.write_header(outfile)

    data = get_stokesi_data(fitsfile)
    if dchan_factor > 1 or dt_factor > 1:
        data = downsample_data(data, dchan_factor=dchan_factor, dt_factor=dt_factor)

    sig.append_spectra(data, outfile)


def fil2fits(filfile: str, outfile: str) -> None:
    """Convert filterbank file to a PSRFITS file."""

    y = Your(filfile)
    outdir, filename = os.path.split(outfile)
    outdir = outdir.rstrip("/") or "."
    os.makedirs(outdir, exist_ok=True)

    outname, _ = os.path.splitext(filename)
    if not outname:
        outname = os.path.splitext(os.path.basename(filfile))[0]

    npsub = getattr(y, "native_nspectra", None) or y.your_header.nspectra
    writer = Writer(your_object=y, outdir=outdir, outname=outname, nsamp=npsub)
    writer.to_fits(npsub=1024)
