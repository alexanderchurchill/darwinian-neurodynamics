"""
All parameters for an evolutionary run
are stored in here
"""

#####################
# GA parameters
#####################
pop_size = 10
mutation_rate = 0.05
crossover_rate = 0.05

#####################
# Simulation parameters
#####################
time_step_length = 0.001
time_steps_per_evaluation = 100

#####################
# Atom parameters
#####################

min_message_delay = 1
max_message_delay = 10

min_time_active = 1
max_time_active = 50

min_sensors_in_s_atom = 1
max_sensors_in_s_atom = 3
min_motors_in_m_atom = 1
max_motors_in_m_atom = 4

#####################
# Robot parameters
#####################

robot_port = 9560