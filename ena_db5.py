# Purpose of this script
# ----------------------
#
# Calculates overhead line conductor ratings according to the formulas in
# the Electricity Supply Association of Australia (ESAA) document
# D(b)5 - 1988, "Current rating of Bare Overhead Line Conductors".
#
# Note ESAA became ENA, Energy Networks Australia, so this document
# may also be referred to as "ENA D(b)5 - 1988".
#
# This script is an improvement on a previous Excel spreadsheet I had
# developed, the improvement being that the Excel spreadsheet could only
# do one calculation at a time, while this script can potentially run
# calculations for many combinations of conductors and ambient conditions
# at once.
#
# About ENA D(b)5
# ---------------
#
# ENA D(b)5 is a withdrawn / superceded standard, which no longer appears
# to be available on the internet (from SAI Global or elsewhere) for
# download or purchase.
#
# Copies of ENA D(b)5 still exist in private (institutional or personal)
# reference libraries, which would appear to be the only way to get copies
# of this widely referenced document.
#
# Whether it is good and proper for this document to have disappeared from
# public view, and what role the for-profit Australian Standards publishing
# model / business model plays in this, is left as a thought experiment to
# the reader...
#
# To this author's knowledge, there is no official published Australian
# Standard replacing ENA D(b)5.
#
# TNSP Operational Line Ratings
# -----------------------------
#
# A commonly accepted modern equivalent to ENA D(b)5 is a document titled
# "TNSP Operational Line Ratings", dated March 2009. This document was published
# over the seals of multiple Australian utilities including Western Power,
# Transgrid, Powerlink, VENCorp, Transend, Electranet, and SP AusNet, representing
# the majority of Australian transmission authorities at the time.
#
# The contents of "TNSP Operational Line Ratings" include more modern (but more
# complex) equivalents to the formulas in ENA D(b)5, as well as some further
# information on theoretical and practical considerations, and modern practices
# for aerial conductor rating.
#
# "TNSP Operational Line Ratings" is a freely downloadable document.
# Refer: https://www.powerlink.com.au/sites/default/files/2018-01/TNSP%20Operational%20Line%20Ratings.pdf .
#
# Equivalent international standards
# ----------------------------------
#
# Outside of Australian practice, the IEEE standard IEEE 738-2012, "IEEE
# Standard for Calculating the Current-Temperature Relationship of Bare
# Overhead Conductors", would cover the same topics as ENA D(b)5.
#
# Some general notes on this calculation
# --------------------------------------
#
# The steady-state rating of a bare conductor in air is essentially a
# mechanical engineering problem, involving heat gain from internal
# sources (I²R heating), heat gain from external sources (sunlight),
# and heat losses to the environment (via air cooling and black-body
# radiation.)
#
# This is probably the only time an electrical engineer will get to
# legitimately apply fluid dynamics concepts (Reynolds Numbers,
# laminar vs. turbulent flow...) in an electrical engineering context.
#
# The same fundamental physics apply whether the conductor in air is
# a stranded flexible conductor (i.e. aerial OHL conductor) or a
# rigid tubular conductor (i.e. tubular busbar within switchyards.)
#
# So this calculation can also be used to determine steady-state
# current carrying capacity for rigid tubular busbar in air.
#
# L.A. Yip, liaung.yip@ieee.org, 2022-02-03.

from math import sqrt, sin, pi

# Example 1 from ENA D(b)5.
# Expected result: I_wind = 165 amps.
inputs = {
    "conductor_name": "Almond",
    "weathering": "rural",
    "time_of_day": "winter night",
    "t_a": 10,
    "t_c": 100,
    "R_dc": 0.975 * 10 ** -3,  # ohm/m
    "α": 0.00403,  # 1/K
    "D": 7.5 * 10 ** -3,  # m
    "v": 1.0, #m/s
    "conductor_type": "ACSR",
    "layer_construction": "6/1 (< 3.0mm)",
}

# Example 2 from ENA D(b)5.
# Expected result: I_wind = 732 amps.
inputs = {
    "conductor_name": "Saturn",
    "weathering": "industrial",
    "time_of_day": "summer noon",
    "t_a": 35,
    "t_c": 85,
    "R_dc": 0.1100 * 10 ** -3,  # ohm/m
    "α": 0.00403,  # 1/K
    "D": 21 * 10 ** -3,  # m
    "v": 1.0, # m/a
    "conductor_type": "AAC",
    "layer_construction": "37",
}


# a = solar absorption coefficient
# = 0.5 for rural weathered conductor
# = 0.85 for industrial weathered conductor
if inputs["weathering"] == "rural":
    a = 0.5
elif inputs["weathering"] == "industrial":
    a = 0.85
else:
    raise ValueError

# D = diameter of conductor (m)
D = inputs["D"]
if D > 0.0338:
    raise ValueError  # A conductor diameter greater than 33.8mm (the largest conductor in the Olex catalog) is probably an error.

# e = emissivity of conductor
#
# Note: seems to be same as "a".
if inputs["weathering"] == "rural":
    e = 0.5
elif inputs["weathering"] == "industrial":
    e = 0.85
else:
    raise ValueError

# F = Albedo (ground reflectance)

F = 0.2

# g = acceleration due to gravity, 9.81 m/s²
g = 9.81

# v = transverse wind velocity (m/s)
v = inputs["v"]
if v < 0.0 or v > 3.0:
    raise ValueError  # Wind speed should be between 0 m/s and 3 m/s typically

# α = Temperature coefficient of resistance at 20°C (units 1/K)
α = inputs["α"]

# σ = Stefan-Boltzmann constant = 5.67 * 10 ^ -8 (W/m² K^4)
σ = 5.67 * 10 ** -8

# ψ = Angle of attack of the wind relative to conductor axis (degrees)
#
# Note: Assume ψ = 90 degrees.
# As per ENA D(b)5 section 4.4 "Air Movement" - "... practice tends to indicate
# that current ratings based on transverse flow are satisfactory."

ψ = 90

# pi

π = pi

# t_a = ambient temperature (°C)
# 35°C for summer noon time
# 10°C for winter night time
#
# Note we take this as a input parameter (to allow various ambient temperatures - i.e. 45°C for North West Queensland.)

t_a = inputs["t_a"]
# TODO: Insert sanity check of ambient temperature vs summer noon / winter night conditions.

# t_c = Conductor maximum operating temperature (°C)
t_c = inputs["t_c"]
# TODO: Insert sanity check that max operating temperature is in a sensible range 75°C - 100°C.

# t_d = sky temperature (°C)
t_d = 0.0552 * (t_a + 273) ** 1.5 - 273

# t_g = ground temperature (°C)
# = t_a + 5°C for summer noon conditions
# = t_a - 5°C for winter night conditions

if inputs["time_of_day"] == "summer noon":
    t_g = t_a + 5
elif inputs["time_of_day"] == "winter night":
    t_g = t_a - 5

# ν_f = viscosity of the air film (m²/s)

ν_f = 1.32 * 10 ** -5 + 9.5 * 10 ** -8 * (t_c + t_a) / 2

# λ_f = thermal conductivity of the air film (W/m.K)

λ_f = 2.42 * 10 ** -2 + 7.2 * 10 ** -5 * (t_c + t_a) / 2

# Grashof number
Gr_numerator = D ** 3 * g * (t_c - t_a)
Gr_denominator = (((t_c + t_a) / 2) + 273) * ν_f ** 2
Gr = Gr_numerator / Gr_denominator

# Pr = Prantdl number
Pr = 0.715 - 2.5 * 10 ** -4 * (t_c + t_a) / 2

# Re = Reynolds Number
Re = v * D / ν_f

# A and m are constants dependent on the value of (Gr * Pr):
if Gr * Pr <= 10 ** 4:
    A = 0.850
    m = 0.188
else:
    A = 0.480
    m = 0.250

# B and n are constants dependent on the value of Re:
if Re <= 2650:
    B = 0.641
    n = 0.471
else:
    B = 0.048
    n = 0.800

# C and P are constants dependent on the angle:
# (angle ψ, in degrees)

if 0 <= ψ and ψ <= 24:
    C = 0.68
    P = 1.08
elif 24 < ψ and ψ <= 90:
    C = 0.58
    P = 0.90
else:
    raise ValueError

# I_dir = 1,000 W/m² for direct solar radiation intensity
# I_diff = 100 W/m² for diffuse solar radiation intensity
# I_dir and I_diff = 0 for night time conditions

if inputs["time_of_day"] == "summer noon":
    I_dir = 1000
    I_diff = 100
elif inputs["time_of_day"] == "winter night":
    I_dir = 0
    I_diff = 0
else:
    raise ValueError

# k = Factor allowing for effective increase in d.c. resistance due to the skin effect, hysteresis and eddy current losses

# k_s = skin effect ratio
#
# Notes from ENA D(b)5 section 4.6:
#
# "... The value of k_s is dependent on conductor size. For the purpose of the
# document the value of 1.015 is considered appropriate."
k_s = 1.015

# k_m = magnetic effect ratio
if "ACSR" in inputs["conductor_type"]:
    layer_constructions = {
        "4/3": 1.1,
        "3/4": 1.06,
        "6/7": 1.13,
        "6/1 (>= 3.0mm)": 1.10,
        "6/1 (< 3.0mm)": 1.07,
        "30/7": 1.00,
        "54/7": 1.06,
        "54/19": 1.07,
    }
    _l = inputs["layer_construction"]
    assert _l in layer_constructions.keys()
    k_m = layer_constructions[_l]
else:
    k_m = 1.00

k = k_s * k_m

# m = see "A"

# n = see "B"

# Nu = Nusselt number

Nu = A * (Gr * Pr) ** m

# P = see "C"

# PF = Power loss by forced convection (Watts/metre)
sin_ψ = sin(ψ * π / 180)  # note degrees -> radians conversion
PF = π * λ_f * (t_c - t_a) * B * (Re ** n) * (0.42 + C * (sin_ψ ** P))

# PN = Power loss by natural convection (Watts/metre)
PN = π * λ_f * (t_c - t_a) * Nu

# PR = Power loss by radiation (Watts/metre)
t_c_K = t_c + 273  # Celsius -> Kelvin
t_g_K = t_g + 273
t_d_K = t_d + 273
PR = π * D * σ * e * (t_c_K ** 4 - 0.5 * t_g_K ** 4 - 0.5 * t_d_K ** 4)

# PS = Power gain by solar heat input (Watts/metre)
PS = a * D * (I_dir * (1 + π / 2 * F) + π / 2 * I_diff * (1 + F))

# R_dc = Conductor d.c. resistance at 20°C (ohm/m)
R_dc = inputs["R_dc"]

# r_ac = effective a.c. resistance
r_ac = (k * R_dc * (1 + α * (t_c - 20)))

I_wind = sqrt((PR + PF - PS) / r_ac)

I_still = sqrt((PR + PN - PS) / r_ac)