import unittest
import os
import shutil
import numpy as np
from your import Your

from psrtool.splittool import split_fil, split_fits


class TestSplitFil(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures."""
        self.outdir = "/tmp/test_split_fil"
        os.makedirs(self.outdir, exist_ok=True)

    def tearDown(self):
        """Clean up test files."""
        if os.path.exists(self.outdir):
            shutil.rmtree(self.outdir)

    def test_split_fil_invalid_split_time(self):
        """Test that invalid split_time raises ValueError."""
        filfile = "tests/testdata/combined.fil"
        with self.assertRaises(ValueError):
            split_fil(filfile, self.outdir, split_time_s=0)
        with self.assertRaises(ValueError):
            split_fil(filfile, self.outdir, split_time_s=-1)

    def test_split_fil_basic(self):
        """Test basic filterbank file splitting."""
        filfile = "tests/testdata/combined.fil"
        split_time_s = 50.0  # 5 seconds per chunk

        # Check that input file exists
        if not os.path.exists(filfile):
            self.skipTest(f"Test data file {filfile} not found")

        split_fil(filfile, self.outdir, split_time_s=split_time_s)

        # Check that output files were created
        output_files = sorted([f for f in os.listdir(self.outdir) if f.endswith('.fil')])
        self.assertGreater(len(output_files), 0, "No output files created")

        # Load original file to verify data consistency
        y_original = Your(filfile)
        original_data = y_original.get_data(0, y_original.your_header.nspectra, pol=0)
        total_original_samples = y_original.your_header.nspectra

        # Verify each chunk and reconstruct data
        reconstructed_data = []
        processed_samples = 0

        for output_file in output_files:
            chunk_path = os.path.join(self.outdir, output_file)
            y_chunk = Your(chunk_path)

            # Headers should match (except for nspectra and tstart)
            self.assertEqual(y_chunk.your_header.nchans, y_original.your_header.nchans)
            self.assertEqual(y_chunk.your_header.foff, y_original.your_header.foff)
            self.assertEqual(y_chunk.your_header.tsamp, y_original.your_header.tsamp)
            self.assertEqual(y_chunk.your_header.nbits, y_original.your_header.nbits)
            self.assertEqual(y_chunk.your_header.source_name, y_original.your_header.source_name)

            # Read chunk data
            chunk_data = y_chunk.get_data(0, y_chunk.your_header.nspectra, pol=0)
            reconstructed_data.append(chunk_data)
            processed_samples += y_chunk.your_header.nspectra

        # Verify that total samples match
        self.assertEqual(processed_samples, total_original_samples,
                         "Total samples after splitting do not match original")

        # Verify data consistency - concatenated chunks should match original
        if reconstructed_data:
            concatenated_data = np.concatenate(reconstructed_data, axis=0)
            np.testing.assert_array_equal(
                concatenated_data, original_data,
                err_msg="Reconstructed data does not match original data"
            )


if __name__ == "__main__":
    unittest.main()
