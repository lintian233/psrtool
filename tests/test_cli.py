import sys
import unittest
from unittest.mock import patch

from psrtool import cli


class TestCLI(unittest.TestCase):
    @patch("psrtool.cli.combinefits")
    def test_combinefitscli_calls_impl(self, mock_combine):
        argv = ["prog", "a.fits", "b.fits", "-o", "out.fil", "-c", "4", "-t", "2"]
        with patch.object(sys, "argv", argv):
            cli.combinefitscli()

        mock_combine.assert_called_once_with(
            ["a.fits", "b.fits"], "out.fil", dchan_factor=4, dt_factor=2
        )

    @patch("psrtool.cli.fits2fil")
    def test_fits2filcli_calls_impl(self, mock_fits2fil):
        argv = ["prog", "input.fits", "-o", "out.fil", "-c", "4", "-t", "2"]
        with patch.object(sys, "argv", argv):
            cli.fits2filcli()

        mock_fits2fil.assert_called_once_with(
            "input.fits", "out.fil", dchan_factor=4, dt_factor=2
        )

    @patch("psrtool.cli.fil2fits")
    def test_fil2fitscli_calls_impl(self, mock_fil2fits):
        argv = ["prog", "input.fil", "-o", "out.fits"]
        with patch.object(sys, "argv", argv):
            cli.fil2fitscli()

        mock_fil2fits.assert_called_once_with("input.fil", "out.fits")


if __name__ == "__main__":
    unittest.main()
