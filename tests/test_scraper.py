import unittest

from scraper import build_search_url


class BuildSearchUrlTest(unittest.TestCase):
    def test_encodes_keywords_and_location(self):
        url = build_search_url('desenvolvedor python', 'Sao Paulo')
        self.assertIn('keywords=desenvolvedor+python', url)
        self.assertIn('location=Sao+Paulo', url)
        self.assertTrue(url.startswith('https://www.linkedin.com/jobs/search/?'))


if __name__ == '__main__':
    unittest.main()
