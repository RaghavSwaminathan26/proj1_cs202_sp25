import unittest
from proj1 import *


class TestRegionFunctions(unittest.TestCase):

    def setUp(self):
        self.r1 = R1
        self.r2 = R2
        self.r3 = R3
        self.r4 = R4

    def test_tokyo_population(self):
        self.assertEqual(self.r1.pop, 37194000)

    def test_lagos_year(self):
        self.assertEqual(self.r2.year, 2015)

    def test_gulf_terrain(self):
        self.assertEqual(self.r3.region.terrain, "ocean")

    def test_tokyo_name(self):
        self.assertEqual(self.r1.region.name, "Tokyo")

    def test_emissions_per_capita(self):
        self.assertAlmostEqual(
            emissions_per_capita(self.r1),
            self.r1.ghg_rate / self.r1.pop,
            places=6
        )

    def test_emissions_per_capita_zero_pop(self):
        rc = RegionCondition(self.r1.region, 2023, 0, 1000.0)
        self.assertEqual(emissions_per_capita(rc), 0.0)

    def test_area_positive(self):
        self.assertTrue(area(self.r1.region.rect) > 0)

    def test_area_wraparound(self):
        gr = GlobeRect(10.0, 20.0, 170.0, -170.0)
        self.assertTrue(area(gr) > 0)

    def test_emissions_per_square_km(self):
        self.assertAlmostEqual(
            emissions_per_square_km(self.r1),
            self.r1.ghg_rate / area(self.r1.region.rect),
            places=6
        )

    def test_densest(self):
        self.assertEqual(densest(region_conditions), "Tokyo")

    def test_project_condition_year(self):
        projected = project_condition(self.r3, 10)
        self.assertEqual(projected.year, self.r3.year + 10)

    def test_project_condition_region_same(self):
        projected = project_condition(self.r2, 5)
        self.assertEqual(projected.region, self.r2.region)

    def test_project_condition_population(self):
        projected = project_condition(self.r3, 10)
        expected = int(self.r3.pop * ((1 + 0.0001) ** 10))
        self.assertEqual(projected.pop, expected)


if __name__ == "__main__":
    unittest.main()