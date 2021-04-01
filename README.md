# rtk-pointnshoot
Calculates the location of a point based on an origin point, distance, and compass bearing.

# Maths used
## Calculate grid convergence:
γ = arctan [tan (λ - λ0) × sin φ]
γ = grid convergence
λ0 = longitude of UTM zone's central meridian
φ = yPoint = POI northing (in grid)
λ = xPoint = POI easting (in grid)

Adapted from https://gis.stackexchange.com/questions/115531/how-to-calculate-grid-convergence-true-north-to-grid-north

## Calculate grid convergence in arcpy
arcpy.CalculateGridConvergenceAngle_cartography(inFeatures, angleField,
                                                rotationMethod,
                                                coordSystemField)

## Convert magnetic azimuth to true (geographic) azimuth:
true azimuth = magnetic azimuth + magnetic declination

## Convert true azimuth to grid azimuth:
grid azimuth = true azimuth + grid convergence

## Convert magnectic azimuth to grid azimuth:
grid azimuth = (magnetic azimuth + magnetic declination) + grid convergence

from https://geomagnetism.ga.gov.au/agrf-calculations/agrf-form

## Calculate new point location from heading and distance
Xb = Sin(Rad(Heading))*Distance+Xa
Yb = Cos(Rad(Heading))*Distance+Ya
