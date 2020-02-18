import lib.swarm_sim_header as header
from copy import deepcopy


NE = 0
E = 1
SE = 2
SW = 3
W = 4
NW = 5
S = 6  # S for stop and not south

def solution(world):
    global leader
    if world.get_actual_round() == 1:
        handle_first_round(world)
        ##sim.get_particle_map_id()[leader]
    else:
        if leader.state == "scanning":
            handle_scanning(leader)
        elif leader.state == "caving":
            handle_caving(leader)
        elif leader.state == "toTile":
            handle_to_tile(leader)
        elif leader.state == "taking":
            handle_taking(leader)
        elif leader.state == "dropping":
            handle_dropping(leader)
        elif leader.state == "in_cave":
            handle_in_cave(leader)
        elif leader.state == "checking":
            handle_checking(leader)


def handle_first_round(world):
    global leader
    leader, distance, closest_tile_coordinates = getIdOfNearestParticleToIsland(world)
    leader.set_color((0.0, 1, 0.0, 1.0))
    setattr(leader, "directions_list", world.grid.get_directions_list())
    setattr(leader, "coating_locations", [])
    setattr(leader, "caving_locations", [])
    setattr(leader, "starting_location", ())
    setattr(leader, "active_matters", world.particles.copy())
    leader.active_matters.remove(leader)
    setattr(leader, "am_distances", get_sorted_list_of_particles_distances(leader))
    setattr(leader, "aim", ())
    setattr(leader, "prev_aim", leader.aim)
    setattr(leader, "aim_path", [])
    setattr(leader, "path_list", [])
    setattr(leader, "neighbors", {})
    setattr(leader, "obstacle_dir", False)
    setattr(leader, "cave_entrance", [])
    setattr(leader, "cave_exit", [])
    setattr(leader, "in_cave", False)
    setattr(leader, "first_level", True)
    setattr(leader, "scanning", True)

    if distance == 1:
        leader.starting_location = leader.coordinates
        if get_an_adjacent_obstacle_directions_scanning(leader):
            dire = obstacles_free_direction(leader)
        leader.coating_locations.append(leader.coordinates)
        leader.prev_aim =  leader.coordinates
        leader.move_to(dire)
        setattr(leader, "state", "scanning")
        print("Start with scanning")
    else:
        setattr(leader, "state", "toTile")
        leader.aim = closest_tile_coordinates
        leader.aim_path = findWayToAim(leader.coordinates,  closest_tile_coordinates, leader.world)
        print("Start with going to Tile")


def cave_entrance(leader):
    if leader.obstacle_dir:
        index_dir, neighbors_string = scan_adjacent_locations(leader)
        dire = None
        if len(leader.neighbors) == 2:
            dire, dire_exit = handle_two_matters(dire, index_dir, leader, neighbors_string)
        elif len(leader.neighbors) == 3:
            dire = handle_three_matters(dire, index_dir, leader, neighbors_string)
        if dire is not None and dire_exit is not None:
            if leader.prev_aim != leader.world.grid.get_coordinates_in_direction(leader.coordinates, dire):
                cave_entrance_tmp = leader.world.grid.get_coordinates_in_direction(leader.coordinates, dire)
                cave_exit_tmp = leader.world.grid.get_coordinates_in_direction(leader.coordinates, dire_exit)
                if (leader.coordinates not in leader.cave_entrance and cave_entrance_tmp not in leader.cave_exit)\
                        and (cave_entrance_tmp not in leader.cave_entrance and leader.coordinates  not in leader.cave_exit):
                    leader.cave_entrance.append(cave_entrance_tmp)
                    leader.cave_exit.append(cave_exit_tmp)
                    leader.caving_locations.append(leader.prev_aim)
                    leader.caving_locations.append(cave_entrance_tmp)

                    print(" Check Found Cave")
                    return True
    return False


def scan_adjacent_locations(leader):
    index_dir = leader.directions_list.index(leader.obstacle_dir)
    neighbors_string = ""
    for idx in range(len(leader.directions_list)):
        dire = leader.directions_list[(idx + index_dir) % len(leader.directions_list)]
        if leader.matter_in(dire) is True:
            neighbors_string = neighbors_string + "M"
        else:
            neighbors_string = neighbors_string + "L"
    return index_dir, neighbors_string


def handle_three_matters(dire, index_dir, leader, neighbors_string):
    if neighbors_string == "MMLMLL":
        dire = leader.directions_list[(2 + index_dir) % len(leader.directions_list)]
    elif neighbors_string == "MLMMLL" or neighbors_string == "MLMLLM":
        print(" Check Found 3 Cave")
        dire = leader.directions_list[(1 + index_dir) % len(leader.directions_list)]
    elif neighbors_string == "MLLMML":
        dire = leader.directions_list[(5 + index_dir) % len(leader.directions_list)]
    return dire


def handle_two_matters(dire, index_dir, leader, neighbors_string):
    dire_exit = None
    if neighbors_string == "MLLLML":
        dire = leader.directions_list[(5 + index_dir) % len(leader.directions_list)]
        dire_exit = leader.directions_list[(1 + index_dir) % len(leader.directions_list)]
        if leader.prev_aim == leader.world.grid.get_coordinates_in_direction(leader.coordinates, dire_exit):
            dire_exit = leader.directions_list[(3 + index_dir) % len(leader.directions_list)]
        print("Found Cave MLLL and entrance in ", dire, leader.coordinates)
    elif neighbors_string == "MLMLLL":
        dire = leader.directions_list[(1 + index_dir) % len(leader.directions_list)]
        dire_exit = leader.directions_list[(3 + index_dir) % len(leader.directions_list)]
        if leader.prev_aim == leader.world.grid.get_coordinates_in_direction(leader.coordinates, dire_exit):
            dire_exit = leader.directions_list[(5 + index_dir) % len(leader.directions_list)]
        print("Found Cave and entrance in ", dire, leader.coordinates)
    elif neighbors_string == "MLLMLL":
        for idx in range(len(leader.directions_list)):
            dire = leader.directions_list[(idx + index_dir) % len(leader.directions_list)]
            if leader.matter_in(dire) is False and leader.prev_aim == leader.world.grid.get_coordinates_in_direction(
                    leader.coordinates, dire):
                if idx < 3:
                    dire = leader.directions_list[(4 + index_dir) % len(leader.directions_list)]
                else:
                    dire = leader.directions_list[(1 + index_dir) % len(leader.directions_list)]
                if not leader.matter_in(leader.directions_list[(idx - 1 + index_dir) % len(leader.directions_list)]):
                    dire_exit = leader.directions_list[(idx - 1 + index_dir) % len(leader.directions_list)]
                else:
                    dire_exit = leader.directions_list[(idx + 1 + index_dir) % len(leader.directions_list)]
    return dire, dire_exit


def get_neighbors(leader):
    leader.neighbors = {}
    leader.obstacle_dir = None
    for dir in leader.directions_list:
        if leader.matter_in(dir):
            leader.neighbors[dir] = leader.get_matter_in(dir)
            leader.obstacle_dir = dir
    return


def handle_caving(leader):
    get_neighbors(leader)
    if len(leader.neighbors) == 5:
        leader.aim = leader.cave_exit[0]
        leader.aim_path = findWayToAim(leader.coordinates, leader.aim, leader.world)
        print("from caving --> in_cave")
        leader.state = "in_cave"
        return
    if get_an_adjacent_obstacle_directions_scanning(leader):
        dire = obstacles_free_direction(leader)
        if get_an_adjacent_tile_directions_scanning(leader):  # and leader.coordinates not in leader.cave_entrance
            leader.coating_locations.append(leader.coordinates)
            leader.caving_locations.append(leader.coordinates)
        leader.prev_aim = leader.coordinates
        if leader.world.grid.get_coordinates_in_direction(leader.coordinates, dire) in leader.cave_exit:
            print("from caving --> scanning")
            leader.state = "scanning"
            return
        leader.move_to(dire)
    if leader.coordinates not in leader.caving_locations:
        return
    else:

        # leader.move_to(leader.world.grid.get_nearest_direction(leader.coordinates, leader.prev_aim))
        # if leader.first_level:
        #     leader.state = "scanning"
        #     print("from caving --> 1st_level_scanning")
        #     return
        # leader.state = "scanning"
        # print("from caving --> scanning")
        leader.aim=leader.cave_exit[0]
        if leader.coordinates == leader.aim:
            print("from caving --> scanning")
            leader.state = "scanning"
            return
        leader.aim_path = findWayToAim(leader.coordinates, leader.aim, leader.world)
        print("from caving --> in_cave")
        leader.state = "in_cave"
        return


def handle_in_cave(leader):
    if reached_aim(leader.aim, leader):
        leader.in_cave = False
        leader.prev_aim = leader.coordinates
        leader.move_to(leader.world.grid.get_nearest_direction(leader.coordinates, leader.aim))
        if leader.scanning:
            print("from in_cave --> scanning")
            leader.state = "scanning"
            return
        print("from in_cave --> checking")
        leader.state = "checking"


def handle_scanning(leader):
    if leader.coordinates != leader.starting_location:
        get_neighbors(leader)
        if cave_entrance(leader):
            leader.state = "caving"
            dir = leader.world.grid.get_nearest_direction(leader.coordinates, leader.cave_entrance[0])
            leader.prev_aim = leader.coordinates
            leader.move_to(dir)
            if leader.first_level:
                print("1st_level_scanning --> caving")
                return
            print("scanning --> caving")
            return

        if leader.first_level:
            if get_an_adjacent_obstacle_directions_scanning(leader):
                dire = obstacles_free_direction(leader)
                if get_an_adjacent_tile_directions_scanning(leader):
                    leader.coating_locations.append(leader.coordinates)
        else:
            dire = obstacles_free_direction(leader)
            leader.coating_locations.append(leader.coordinates)
        leader.prev_aim = leader.coordinates
        leader.move_to(dire)
    else:
        leader.state = "checking"
        if leader.first_level:
            print("1st_level_scanning --> checking")
            leader.first_level = False
            return
        print("scanning --> checking")


def handle_to_tile(leader):
    if reached_aim(leader.aim, leader):
        leader.starting_location = leader.coordinates
        if get_an_adjacent_obstacle_directions(leader):
            dire = obstacles_free_direction(leader)
            leader.coating_locations.append(leader.coordinates)
            leader.prev_aim = leader.coordinates
            leader.move_to(dire)

        print("from toTile --> 1st level scanning")
        leader.state = "scanning"


def handle_taking(leader):
    if leader.in_cave:
        print("from taking -->  in_cave")
        leader.aim = leader.cave_exit[0]
        leader.aim_path = findWayToAim(leader.coordinates, leader.aim, leader.world)
        leader.prev_aim = leader.coordinates
        leader.state = "in_cave"
        return
    if reached_aim(leader.aim, leader):
        leader.take_particle_on(leader.aim)
        leader.coating_locations =  get_sorted_list_of_locations_distances(leader)
        leader.aim = leader.coating_locations.pop(0)
        leader.aim_path = findWayToAim(leader.coordinates, leader.aim, leader.world)
        print("from taking --> dropping")
        leader.state = "dropping"


def handle_dropping(leader):
    if leader.in_cave:
        print("from dropping -->  in_cave")
        leader.aim = leader.cave_exit[0]
        leader.aim_path = findWayToAim(leader.coordinates, leader.aim, leader.world)
        leader.prev_aim = leader.coordinates
        leader.state = "in_cave"
        return
    if reached_aim(leader.aim, leader):
        leader.drop_particle_on(leader.aim)
        if leader.get_particle_in(leader.world.grid.get_nearest_direction(leader.coordinates, leader.aim)) in leader.active_matters:
            leader.active_matters.remove((leader.get_particle_in(leader.world.grid.get_nearest_direction(leader.coordinates, leader.aim))))
        leader.state = "checking"
        print("from dropping -->  checking")


def handle_checking(leader):
    if not leader.coating_locations:
        print("from checking -->  scanning")
        leader.starting_location = leader.coordinates
        if get_an_adjacent_obstacle_directions(leader):
            leader.scanning = True
            dire = obstacles_free_direction(leader)
            leader.coating_locations.append(leader.coordinates)
            leader.prev_aim = leader.coordinates
            leader.move_to(dire)
        leader.state = "scanning"
    elif leader.active_matters:
        if leader.in_cave:
            print("from checking -->  in_cave")
            leader.aim = leader.cave_exit
            leader.aim_path = findWayToAim(leader.coordinates, leader.aim, leader.world)
            leader.prev_aim = leader.coordinates
            leader.state = "in_cave"
        else:
            print("from checking -->  taking")
            leader.scanning = False
            leader.am_distances = get_sorted_list_of_particles_distances(leader)
            leader.aim = leader.am_distances.pop(0)
            leader.aim_path = findWayToAim(leader.coordinates, leader.aim, leader.world)
            leader.prev_aim = leader.coordinates
            leader.state = "taking"
    else:
        print("It is my turn")
        leader.state = "leader"



def get_sorted_list_of_particles_distances(leader):
    distances =[]
    tmp_dict = {}
    sorted_list_of_particles_coordinates = []
    for particle in leader.active_matters:
        calculated_distance = leader.world.grid.get_distance(leader.coordinates, particle.coordinates)
        distances.append(calculated_distance)
        tmp_dict[particle.coordinates] = calculated_distance
    distances.sort()
    for distance in distances:
        for coords, dist in tmp_dict.items():
            if distance == dist:
                if coords not in sorted_list_of_particles_coordinates:
                    sorted_list_of_particles_coordinates.append(coords)
    return sorted_list_of_particles_coordinates


def get_sorted_list_of_locations_distances(leader):
    distances =[]
    tmp_dict = {}
    sorted_list_of_locations_coordinates = []
    for location in leader.coating_locations:
        calculated_distance = leader.world.grid.get_distance(leader.coordinates, location)
        distances.append(calculated_distance)
        tmp_dict[location] = calculated_distance
    distances.sort()
    for distance in distances:
        for coords, dist in tmp_dict.items():
            if distance == dist:
                if coords not in sorted_list_of_locations_coordinates:
                    sorted_list_of_locations_coordinates.append(coords)
    return sorted_list_of_locations_coordinates


def obstacles_free_direction(leader):
    index_dir = leader.directions_list.index(leader.obstacle_dir)
    for idx in range(len(leader.directions_list)):
        dire = leader.directions_list[(idx + index_dir) % len(leader.directions_list)]
        if leader.matter_in(dire) is False and leader.prev_aim == leader.world.grid.get_coordinates_in_direction(leader.coordinates, dire):
            idx_2 = len(leader.directions_list)
            while idx_2 >= 0:
                dire = leader.directions_list[(idx_2 + index_dir) % len(leader.directions_list)]
                if leader.matter_in(
                        dire) is False and leader.prev_aim != leader.world.grid.get_coordinates_in_direction(
                        leader.coordinates, dire):
                    return dire
                idx_2 -= 1
        if leader.matter_in(dire) is False and leader.prev_aim != leader.world.grid.get_coordinates_in_direction(
            leader.coordinates, dire):
            return dire


def get_adjacent_obstacles_directions(leader):
    leader.obstacle_dir.clear()
    for dir in leader.directions_list:
        if leader.matter_in(dir):
            leader.obstacle_dir.append(dir)
    if bool(leader.obstacle_dir):
        return True
    return False
    #return surroundings
# region surround island


def get_an_adjacent_obstacle_directions(leader):
    leader.obstacle_dir = None
    for dir in leader.directions_list:
        if leader.matter_in(dir):
            leader.obstacle_dir = dir
    if bool(leader.obstacle_dir):
        return True
    return False


def get_an_adjacent_obstacle_directions_scanning(leader):
    leader.obstacle_dir = None
    for dir in leader.directions_list:
        if leader.matter_in(dir):
            if leader.get_matter_in(dir).type == "particle" and leader.get_matter_in(dir) in leader.active_matters:
                leader.active_matters.remove(leader.get_matter_in(dir))
            leader.obstacle_dir = dir
    if bool(leader.obstacle_dir):
        return True
    return False


def get_an_adjacent_tile_directions_scanning(leader):
    leader.obstacle_dir = None
    for dir in leader.directions_list:
        if leader.matter_in(dir):
            if leader.get_matter_in(dir).type == "tile":
                return True
    return False


def getIdOfNearestParticleToIsland(sim):
    closestParticle = sim.get_particle_list()[0]
    min = None
    for particle in sim.get_particle_list():
        for tile in sim.get_tiles_list():
            value = sim.grid.get_distance(particle.coordinates, tile.coordinates)
            if min is None:
                min = value
                closestParticle = particle
                closest_tile_coordinate = tile.coordinates
            elif (value < min):
                min = value
                closestParticle = particle
                closest_tile_coordinate = tile.coordinates
    return closestParticle, min, closest_tile_coordinate


def findWayToAim(lcoordinates, tcoordinates, sim):
    coordLists = [[lcoordinates]]
    visitedcoordinates = [lcoordinates]
    while len(coordLists) > 0:
        currentList = coordLists.pop(0)
        length = len(currentList)
        if areAimCoordinatesReachable(tcoordinates, currentList[length - 1], sim):
            if currentList[0] == leader.coordinates:
                currentList.pop(0)
            currentList.append(tcoordinates)
            return currentList
        else:
            aroundLast = getAllSuroundingcoordinates(currentList[length - 1], sim)
            for tmp in aroundLast:
                if (isCoordUnvisitedAndFree(tmp, visitedcoordinates, sim)):
                    newList = deepcopy(currentList)
                    newList.append(tmp)
                    coordLists.append(newList)
                    visitedcoordinates.append(tmp)

def areAimCoordinatesReachable(acoordinates, bcoordinates, sim):
    if acoordinates == bcoordinates:
        return True
    around = getAllSuroundingcoordinates(acoordinates, sim)
    for tmp in around:
        if tmp == bcoordinates:
            return True
    return False

def isCoordUnvisitedAndFree(coord, visitedcoordinates, sim):
    if coord in visitedcoordinates:
        return False
    if coord in sim.get_particle_map_coordinates():
        return False
    if coord in sim.get_tile_map_coordinates():
        return False
    return True


def getAllSuroundingcoordinates(pcoordinates, sim):
    return [

         header.get_coordinates_in_direction(pcoordinates, sim.grid.get_directions_list()[NE]),
        header.get_coordinates_in_direction(pcoordinates, sim.grid.get_directions_list()[E]),
        header.get_coordinates_in_direction(pcoordinates, sim.grid.get_directions_list()[SE]),
        header.get_coordinates_in_direction(pcoordinates, sim.grid.get_directions_list()[SW]),
        header.get_coordinates_in_direction(pcoordinates, sim.grid.get_directions_list()[W]),
        header.get_coordinates_in_direction(pcoordinates, sim.grid.get_directions_list()[NW])
    ]


def reached_aim(aim, leader):
    if leader.aim_path:

        next_dir =  leader.world.grid.get_nearest_direction(leader.coordinates,  leader.aim_path.pop(0))
        next_coords = header.get_coordinates_in_direction(leader.coordinates, next_dir)
        # if leader.coordinates in leader.caving_locations and leader.aim not in leader.caving_locations:
        #     print("Inside the cave")
        #     leader.in_cave = True
        # elif leader.coordinates in leader.coating_locations:
        #     print("Outside the cave")
        #     leader.in_cave = False
        # elif leader.in_cave and leader.aim not in leader.caving_locations:
        #     print("New caving location")
        #     leader.caving_locations.append(leader.coordinates)
        #     leader.in_cave = True
        # else:
        #     leader.in_cave = False
        if aim == next_coords:
            return True
        leader.move_to(next_dir)
        return False
    return True