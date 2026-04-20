import sys
import unittest
import math
from typing import *
from dataclasses import dataclass

sys.setrecursionlimit(10**6)


@dataclass(frozen=True)
class GlobeRect:
    lo_lat: float
    hi_lat: float
    west_long: float
    east_long: float
    # west_long may be greater than east_long if crossing the date line


@dataclass(frozen=True)
class Region:
    rect: GlobeRect
    name: str
    terrain: str


@dataclass(frozen=True)
class RegionCondition:
    region: Region
    year: int
    pop: int
    ghg_rate: float


# Example regions
tokyo = Region(GlobeRect(35.5, 36.1, 139.4, 140.1), "Tokyo", "other")
lagos = Region(GlobeRect(6.2, 6.8, 3.0, 3.7), "Lagos", "other")
gulf_of_mexico = Region(
    GlobeRect(18.0, 30.0, -98.0, -81.0), "Gulf of Mexico", "ocean"
)
central_coast = Region(
    GlobeRect(34.5, 36.5, -121.5, -119.0), "Central Coast of California", "other"
)

# Example conditions
R1 = RegionCondition(tokyo, 2023, 37194000, 5.6e7)
R2 = RegionCondition(lagos, 2015, 23173000, 2.0e7)
R3 = RegionCondition(gulf_of_mexico, 2008, 56000000, 3.0e8)
R4 = RegionCondition(central_coast, 2012, 14000000, 7.0e6)

region_conditions = [R1, R2, R3, R4]


def emissions_per_capita(rc: RegionCondition) -> float:
    """
    Return the greenhouse gas emissions per person for the given region condition.
    If the population is zero, return 0.0 to avoid division by zero.
    """
    if rc.pop == 0:
        return 0.0
    return rc.ghg_rate / rc.pop


def area(gr: GlobeRect) -> float:
    """
    Return the estimated surface area (in square kilometers) of the given globe rectangle
    using a spherical Earth model. Handles longitude wraparound at the international date line.
    """
    r = 6378.1

    phi1 = math.radians(gr.lo_lat)
    phi2 = math.radians(gr.hi_lat)
    lam1 = math.radians(gr.west_long)
    lam2 = math.radians(gr.east_long)

    delta_lambda = lam2 - lam1
    if delta_lambda < 0:
        delta_lambda += 2 * math.pi

    return (r ** 2) * abs(delta_lambda) * abs(math.sin(phi2) - math.sin(phi1))


def emissions_per_square_km(rc: RegionCondition) -> float:
    """
    Return the greenhouse gas emissions per square kilometer for the given region condition.
    If the region area is zero, return 0.0.
    """
    region_area = area(rc.region.rect)
    if region_area == 0:
        return 0.0
    return rc.ghg_rate / region_area


def population_density(rc: RegionCondition) -> float:
    """
    Return the population density (people per square kilometer) for the given region condition.
    If the region area is zero, return 0.0.
    """
    region_area = area(rc.region.rect)
    if region_area == 0:
        return 0.0
    return rc.pop / region_area


def find_region_condition(rc_list: List[RegionCondition], name: str) -> RegionCondition:
    """
    Return the RegionCondition in rc_list whose region name matches the given name.
    Assumes the name exists in the list.
    """
    if rc_list[0].region.name == name:
        return rc_list[0]
    return find_region_condition(rc_list[1:], name)


def densest(rc_list: List[RegionCondition]) -> str:
    """
    Return the name of the region with the highest population density
    from the given list of RegionCondition values.
    This function is implemented recursively.
    """
    if len(rc_list) == 1:
        return rc_list[0].region.name

    first = rc_list[0]
    best_of_rest_name = densest(rc_list[1:])
    best_of_rest = find_region_condition(rc_list[1:], best_of_rest_name)

    if population_density(first) >= population_density(best_of_rest):
        return first.region.name
    return best_of_rest.region.name


def growth_rate(terrain: str) -> float:
    """
    Return the annual population growth rate associated with the given terrain type.
    """
    if terrain == "ocean":
        return 0.0001
    elif terrain == "mountains":
        return 0.0005
    elif terrain == "forest":
        return -0.00001
    else:
        return 0.0003


def project_condition(rc: RegionCondition, years: int) -> RegionCondition:
    """
    Return a new RegionCondition representing the projected state after a given number of years.
    Population grows annually based on terrain-specific growth rates (compounded),
    and emissions scale proportionally with population.
    """
    rate = growth_rate(rc.region.terrain)
    new_pop = int(rc.pop * ((1 + rate) ** years))

    if rc.pop == 0:
        new_ghg = 0.0
    else:
        new_ghg = rc.ghg_rate * (new_pop / rc.pop)

    return RegionCondition(
        rc.region,
        rc.year + years,
        new_pop,
        new_ghg
    )