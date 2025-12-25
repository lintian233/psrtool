
import unittest
import numpy as np
from unittest.mock import patch

from psrtool.psrfits import read_fits_header, get_header_time_info, is_time_contiguous, get_stokesi_data, downsample_data


class TestIsTimeContiguous(unittest.TestCase):

    @patch("psrtool.psrfits.get_header_time_info")
    @patch("psrtool.psrfits.read_fits_header")
    def test_is_time_contiguous_true(self, mock_read, mock_timeinfo):
        mock_read.side_effect = [(object(), object()), (object(), object())]

        start1 = 100.0
        dur1 = 10.0
        start2 = start1 + dur1 / 86400.0

        mock_timeinfo.side_effect = [(start1, dur1), (start2, 0.0)]

        result = is_time_contiguous("a.fits", "b.fits")
        self.assertIs(result, True) 

        self.assertEqual(mock_read.call_count, 2)
        self.assertEqual(mock_timeinfo.call_count, 2)

    @patch("psrtool.psrfits.get_header_time_info")
    @patch("psrtool.psrfits.read_fits_header")
    def test_is_time_contiguous_false(self, mock_read, mock_timeinfo):
        mock_read.side_effect = [(object(), object()), (object(), object())]

        start1 = 100.0
        dur1 = 10.0
        start2 = start1 + (dur1 + 5.0) / 86400.0  # not contiguous

        mock_timeinfo.side_effect = [(start1, dur1), (start2, 0.0)]

        result = is_time_contiguous("a.fits", "b.fits")
        self.assertIs(result, False)

    @patch("psrtool.psrfits.read_fits_header")
    def test_is_time_contiguous_raises(self, mock_read):
        mock_read.side_effect = FileNotFoundError("missing fits")

        with self.assertRaises(FileNotFoundError):
            is_time_contiguous("a.fits", "b.fits")



class TestPsrFits(unittest.TestCase):
    testdata: str = "tests/testdata/test1.fits"

    def test_read_fits_header(self):

        header0, header1 = read_fits_header(self.testdata)
        self.assertIsNotNone(header0)
        self.assertIsNotNone(header1)
    

    def test_get_header_time_info(self):

        header0, header1 = read_fits_header(self.testdata)
        start_time, duration = get_header_time_info(header0, header1)

        self.assertIsInstance(start_time, float)
        self.assertIsInstance(duration, float)


    def test_get_stokesi_data(self):

        data = get_stokesi_data(self.testdata)
        self.assertIsInstance(data, np.ndarray)
        self.assertEqual(data.ndim, 2)  # Assuming Stokes I data is 2D (time, frequency)


    def test_downsample_data(self):

        data = get_stokesi_data(self.testdata)
        dchan_factor = 2
        dt_factor = 2

        downsampled_data = downsample_data(data, dchan_factor=dchan_factor, dt_factor=dt_factor)

        expected_shape = (
            data.shape[0] // dt_factor,
            data.shape[1] // dchan_factor
        )

        self.assertEqual(downsampled_data.shape, expected_shape)