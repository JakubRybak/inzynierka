import sys
import unittest
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parents[1] / "offline"), str(Path(__file__).resolve().parents[1] / "core")]
import phrase_bank  # noqa: E402


class PolishRows(unittest.TestCase):
    def test_forms_are_labelled_from_their_english_names(self):
        rows = phrase_bank.polish_rows(
            {"embroidery": dict(forms=["haft", "z haftem"], without=["bez haftu"]),
             "lace": dict(forms=["koronka", "z koronką"], without=["bez koronki"])},
            {"light red": dict(forms=["jasnoczerwona", "Jasnoczerwony"], without=[]),
             "lilac": dict(forms=["liliowa"], without=[])},
            {"light red": dict(hex="#F08080", family="Red", lightness="light")},
            known={"bez koronki", "haft"})
        by = {r["phrase"]: r for r in rows}
        self.assertEqual(sorted(by), ["haftu", "jasnoczerwona", "jasnoczerwony", "koronka", "koronki", "z haftem",
                                      "z koronka", "z koronką"])
        self.assertEqual((by["haftu"]["negated"], by["haftu"]["english"]), (False, "embroidery"))
        self.assertFalse(any(r["negated"] for r in rows))
        self.assertEqual((by["z koronka"]["kind"], by["z koronka"]["english"]), ("detail", "lace"))
        self.assertEqual(by["jasnoczerwony"], dict(phrase="jasnoczerwony", kind="shade", negated=False,
                                                   english="light red", concepts=[], queries=0, hex="#F08080",
                                                   family="Red", lightness="light"))


if __name__ == "__main__":
    unittest.main()
