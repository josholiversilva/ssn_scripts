import unittest
import pairings

names_and_emails = ["ryan,ryanjamesaquino@gmail.com", 
        "josh,akingjosh101@gmail.com", 
        "iris,irisyee8@gmail.com",
        "ana,agbayaniana@gmail.com",
        "eric,Ericliu2244@gmail.com",
        "brian,brianwi007@gmail.com",
        "bryan,ngynbryan@gmail.com",
        "vincent,vincentho0129@gmail.com",
        "melissa,meli26salamat@gmail.com",
        "shawn,shawnbnat@gmail.com",
        "victoria,victoriatrnn@gmail.com",
        "jen,jkim8626@gmail.com"]

class TestPairings(unittest.TestCase):
    def test_create_pairings_ssn_unique(self):
        result = pairings.create_pairings(names_and_emails)
        self.assertTrue(len(set(list(result.keys()))) == len(names_and_emails))

    def test_create_pairings_receivers_unique(self):
        result = pairings.create_pairings(names_and_emails)
        self.assertTrue(len(set(list(result.values()))) == len(names_and_emails))

if __name__ == '__main__':
    unittest.main()