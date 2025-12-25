
import unittest
import numpy as np
from your import Your
from unittest.mock import patch

from psrtool.combinefits import combinefits

class TestCombineFits(unittest.TestCase):

    def test_combinefits_basic(self):
        fitsfiles = [
            "tests/testdata/test1.fits",
            "tests/testdata/test2.fits"
        ]
        testfile = "tests/testdata/combined.fil"
        outfile = "/tmp/combined.fil"

        combinefits(fitsfiles, outfile, dchan_factor=1, dt_factor=1)
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
        
