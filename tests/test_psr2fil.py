import unittest
import numpy as np
from your import Your
from unittest.mock import patch

from psrtool.fits2fil import fits2fil, fil2fits



class TestFits2Fil(unittest.TestCase):

    def test_fits2fil_basic(self):
        fitsfile = "tests/testdata/test2.fits"
        testfile = "tests/testdata/test2.fil"
        outfile = "/tmp/test2.fil"

        fits2fil(fitsfile, outfile, dchan_factor=1, dt_factor=1)
        test_fil = Your(testfile)
        out_fil = Your(outfile)
        test_header = test_fil.your_header
        out_header = out_fil.your_header
        self.assertEqual(test_header.tstart, out_header.tstart)
        self.assertEqual(test_header.tsamp, out_header.tsamp)
        self.assertEqual(test_header.nchans, out_header.nchans)
        self.assertEqual(test_header.foff, out_header.foff)
        self.assertEqual(test_header.source_name, out_header.source_name)
        self.assertEqual(test_header.nbits, out_header.nbits)
        self.assertEqual(test_header.nspectra, out_header.nspectra)
        self.assertEqual(test_header.fch1, out_header.fch1)
        data_fil = test_fil.get_data(0, test_header.nspectra, pol=0)
        data_fits = out_fil.get_data(0, out_header.nspectra, pol=0)
        np.testing.assert_array_equal(data_fil, data_fits)

class TestFil2Fits(unittest.TestCase):

    def test_fil2fits_basic(self):
        filfile = "tests/testdata/test2.fil"
        testfile = "tests/testdata/test2.fits"
        outfile = "/tmp/test2.fits"

        fil2fits(filfile, outfile)
        test_fits = Your(testfile)
        out_fits = Your(outfile)
        test_header = test_fits.your_header
        out_header = out_fits.your_header
        self.assertEqual(test_header.tstart, out_header.tstart)
        self.assertEqual(test_header.tsamp, out_header.tsamp)
        self.assertEqual(test_header.nchans, out_header.nchans)
        self.assertEqual(test_header.foff, out_header.foff)
        self.assertEqual(test_header.source_name, out_header.source_name)
        self.assertEqual(test_header.nbits, out_header.nbits)
        self.assertEqual(test_header.nspectra, out_header.nspectra)
        self.assertEqual(test_header.fch1, out_header.fch1)
        data_fil = test_fits.get_data(0, test_header.nspectra, pol=0)
        data_fits = out_fits.get_data(0, out_header.nspectra, pol=0)
        np.testing.assert_array_equal(data_fil, data_fits)
