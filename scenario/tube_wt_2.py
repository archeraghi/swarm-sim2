from scenario.particleGroups import *

def scenario(world):
	#create_matter_in_line(world, (3.0, 0.0, 0.0), (-1.0, 0.0, 0.0), 1)
	#world.config_data.seed_value = 2
	hexagon(world, (3.0-world.config_data.seed_value, 0.0, 0.0), world.config_data.seed_value)
	# around37(world)
	# star50(world)
	#block100(world)
	world.add_tile((8.5, 1.0, 0), color=(0.3, 0.3, 0.8, 1.0))
	world.add_tile((7.5, 1.0, 0), color=(0.3, 0.3, 0.8, 1.0))
	world.add_tile((7.0, 0.0, 0), color=(0.3, 0.3, 0.8, 1.0))
	world.add_tile((7.5, -1.0, 0), color=(0.3, 0.3, 0.8, 1.0))
	world.add_tile((8.0, -2.0, 0), color=(0.3, 0.3, 0.8, 1.0))
	world.add_tile((9.0, -0.0, 0), color=(0.3, 0.3, 0.8, 1.0))
	world.add_tile((9.5, -1.0, 0), color=(0.3, 0.3, 0.8, 1.0))
