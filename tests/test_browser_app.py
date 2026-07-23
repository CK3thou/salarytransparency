import unittest

import pandas as pd

import main


class BrowserAppTests(unittest.TestCase):
    def test_dashboard_contains_form_and_summary(self):
        df = pd.DataFrame(
            {
                "Role": ["Developer"],
                "Company location": ["Lusaka"],
                "Monthly Gross Salary": [5000],
            }
        )

        html = main.build_dashboard_html(df, message="Saved")

        self.assertIn("Salary Transparency Platform", html)
        self.assertIn("Submit salary data", html)
        self.assertIn("Name / role", html)
        self.assertIn("Monthly Gross Salary", html)
        self.assertIn("Developer", html)


if __name__ == "__main__":
    unittest.main()
