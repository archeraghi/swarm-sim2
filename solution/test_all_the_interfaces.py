"""
This solution tests all the interfaces that are provided from swarm-sim MAX Round must be at least 41
"""

import logging
from locale import str
import random

NE = 0
E = 1
SE = 2
SW = 3
W = 4
NW = 5


direction = [NE, E, SE, SW, W, NW]

def solution(sim, world):

    if sim.get_actual_round() == 1:
        print ("Scanning for locations, tiles and particles")
        logging.info("Scanning for locations, tiles and particles")
        all_matters_list = world.get_particle_map_coords()[(0, 0)].scan_for_matter_within()
        for list in all_matters_list:
            if list.type == 'particle':
                print("particle at", list.coords)
            elif list.type == 'tile':
                print("tile", list.coords)
            elif list.type == 'location':
                print("location", list.coords)
        print ("Testing Interface: Take Drop Tiles and Particles")
        logging.info("Testing Interface: Take Drop Tiles and Particles")

    elif sim.get_actual_round() == 2 :
        world.get_particle_list()[0].take_tile_in(E)
    elif sim.get_actual_round() == 3 :
        world.get_particle_list()[0].take_particle_in(E)
    elif sim.get_actual_round() == 4 :
        world.get_particle_list()[0].drop_tile_in(E)
        print("Tiles coords ", world.get_tiles_list()[0].coords[0], world.get_tiles_list()[0].coords[1])
    elif sim.get_actual_round() == 5:
        print("Tiles coords ", world.get_tiles_list()[0].coords[0], world.get_tiles_list()[0].coords[1])
        world.get_particle_list()[0].take_particle_in(W)
    elif sim.get_actual_round() == 6:
        world.get_particle_list()[0].drop_particle_in(W)
        world.get_particle_list()[0].take_tile_in(E)
    elif sim.get_actual_round() == 7:
        world.get_particle_list()[0].drop_tile()
        world.get_particle_list()[0].take_tile()
    elif sim.get_actual_round() == 8:
        world.get_particle_list()[0].drop_particle_in(W)
        world.get_particle_list()[0].take_particle_in(W)
    elif sim.get_actual_round() == 9:
        world.get_particle_list()[0].drop_particle()
    elif sim.get_actual_round() == 10:
        if len(world.get_particle_list()) > 1:
            world.get_particle_list()[0].take_particle_with(world.get_particle_list()[1].get_id())
    elif sim.get_actual_round() == 11:
        world.get_particle_list()[0].drop_particle()
        if len(world.get_tiles_list()) > 0:
            world.get_particle_list()[0].take_tile_with(world.get_tiles_list()[0].get_id())
    elif sim.get_actual_round() == 12:
        world.get_particle_list()[0].drop_tile()
        world.get_particle_list()[0].take_tile_on(0,0)
    elif sim.get_actual_round() == 13:
        world.get_particle_list()[0].drop_tile_on(7,0)
    elif sim.get_actual_round() == 14:
        world.get_particle_list()[0].take_particle()
    elif sim.get_actual_round() == 15:
        world.get_particle_list()[0].drop_particle_on(-7, 0)

    elif sim.get_actual_round() == 16:
        logging.info("Testing Read and Write")
        print("Testing Read and Write")
        logging.info("Start Writing ")
        print("Start Writing")

        world.get_particle_list()[0].write_to_with(world.locations[0], "K1", "Location Data")
        world.get_particle_list()[0].write_to_with(world.tiles[0], "K1", "Tile Data")
        world.get_particle_list()[0].write_to_with(world.get_particle_list()[1], "K1", "Particle Data")
    elif sim.get_actual_round() == 17:
        logging.info("Start Reading")
        print("Start Reading")
        loc_data = world.get_particle_list()[0].read_from_with(world.locations[0], "K1")
        tile_data = world.get_particle_list()[0].read_from_with(world.tiles[0], "K1")
        part_data = world.get_particle_list()[0].read_from_with(world.get_particle_list()[1], "K1")

        if loc_data != 0:
            print(loc_data)
        if tile_data != 0:
            print(tile_data)
        if part_data != 0:
            print(part_data)

    elif sim.get_actual_round() > 20:
        for particle in world.get_particle_list():
            particle.move_to(random.choice(direction))
            if particle.coords in world.get_tile_map_coords():
                print("Found Tile")
                particle.take_tile()
                particle.carried_tile.set_color(3)
                world.csv_round_writer.success()
    if sim.get_actual_round() == 24:
        world.get_particle_list()[1].create_tile()
        world.get_particle_list()[2].create_location()
        world.get_particle_list()[3].create_particle()

    if sim.get_actual_round() == 40:
        world.get_particle_list()[4].create_tile()
        world.get_particle_list()[5].create_location()
        world.get_particle_list()[6].create_particle()



        #world.get_particle_list()[0].take_tile_in(E)
    #    world.get_particle_list()[0].drop_particle_in(W)
    #   world.get_particle_list()[0].drop_particle_in(E)

    #elif sim.get_actual_round() == 5 :
