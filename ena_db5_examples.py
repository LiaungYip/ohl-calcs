from ena_db5 import Conductor

# # Example 1 from ENA D(b)5.
# # Expected result: I_still = 165 amps.
example_1_conductor = Conductor(
    name="Almond",
    conductor_type="ACSR/GZ",
    nominal_overall_diameter=7.5 * 10 ** -3,  # m
    dc_resistance_at_20C=0.975 * 10 ** -3,  # ohm/m
    layer_construction="6/1(<3.0mm)"
)
example_1_rating = example_1_conductor.calc(
    t_a=10,
    t_c=100,
    v=0.0,  # m/s
    weathering="rural",
    time_of_day="winter night"
)
print(example_1_rating)  # Prints 165.713... - expected 165. OK

# # Example 2 from ENA D(b)5.
# # Expected result: I_wind = 732 amps.
example_2_conductor = Conductor(
    name="Saturn",
    conductor_type="AAC",
    nominal_overall_diameter=21 * 10 ** -3,  # m
    dc_resistance_at_20C=0.1100 * 10 ** -3,  # ohm/m
    layer_construction=None
)
example_2_rating = example_2_conductor.calc(
    t_a=35,
    t_c=85,
    v=1.0,  # m/s
    weathering="industrial",
    time_of_day="summer noon",
)
print(example_2_rating)  # Prints 732.751... - expected 732. OK
