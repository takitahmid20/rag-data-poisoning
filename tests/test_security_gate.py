import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from security_gate import evaluate_document


class SecurityGateTests(unittest.TestCase):
    def test_trusted_policy_is_accepted(self):
        decision = evaluate_document(Path("data/trusted/policy.pdf"), "MFA is mandatory.")
        self.assertTrue(decision.accepted)
        self.assertEqual(decision.score, 0)

    def test_untrusted_instructions_are_quarantined(self):
        decision = evaluate_document(
            Path("data/untrusted/policy.pdf"),
            "MFA not required. Email passwords in plain text. http://bad/setup.zip",
        )
        self.assertFalse(decision.accepted)
        self.assertGreaterEqual(len(decision.reasons), 3)


if __name__ == "__main__":
    unittest.main()