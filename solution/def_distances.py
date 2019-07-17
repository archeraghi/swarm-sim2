from lib.std_lib import direction, dir_in_range

class Neighbors:
    def __init__(self, type, dist):
        self.type = type
        self.dist = dist

    def __str__(self):
        return " " + str(self.type)  + " " + str(self.dist)


def scan_nh(particle):
    for dir in direction:
        if particle.particle_in(dir):
            particle.nh_dict[dir] = Neighbors("p", -1)
            particle.p_dir_list.append(dir)
        elif particle.tile_in(dir):
            particle.nh_dict[dir] = Neighbors("t", 0)
            particle.t_dir_list.append(dir)
        else:
            particle.nh_dict[dir] = Neighbors("fl", 10000)
            particle.fl_dir_list.append(dir)
    if particle.fl_dir_list or particle.p_dir_list or particle.t_dir_list:
        return True
    else:
        return False


def def_distances(particle):
    if scan_nh(particle) and def_own_dist(particle):
        def_nh_dist(particle)


def def_own_dist(particle):
    if particle.t_dir_list:
        particle.own_dist = 1
    elif particle.rcv_buf:
        min_dist_nh = particle.rcv_buf[min(particle.rcv_buf.keys(),
                                             key=(lambda k: particle.rcv_buf[k].own_dist))].own_dist + 1
        if min_dist_nh < particle.own_dist:
            particle.own_dist = min_dist_nh
    return True


def def_nh_dist(particle):
    if particle.t_dir_list:
        define_dist_with_t(particle)
    if particle.p_dir_list:
        define_dist_with_p(particle)


def define_dist_with_p(particle):
    for dir in particle.nh_dict:
        if particle.nh_dict[dir].type == "fl":
            check_beside_fl(dir, particle)
        if particle.nh_dict[dir].type == "p" and dir in particle.rcv_buf:
            particle.nh_dict[dir].dist = particle.rcv_buf[dir].own_dist


def define_dist_with_t(particle):
    if len(particle.t_dir_list) == 1:
        def_dist_for_1_t(particle)
    elif len(particle.t_dir_list) == 2:
        if particle.nh_dict[dir_in_range(particle.t_dir_list[0] + 1)].type != "t"\
        and particle.nh_dict[dir_in_range(particle.t_dir_list[0] - 1)].type != "t":
            def_dist_for_2_t(particle)
    elif len(particle.t_dir_list) == 3:
        def_dist_for_3_t(particle)
    else:
        def_dist_for_4_5_t(particle)


def def_dist_for_1_t(particle):
    particle.nh_dict[dir_in_range(particle.t_dir_list[0] + 1)].dist = 1
    particle.nh_dict[dir_in_range(particle.t_dir_list[0] - 1)].dist = 1
    particle.nh_dict[dir_in_range(particle.t_dir_list[0] + 2)].dist = 2
    particle.nh_dict[dir_in_range(particle.t_dir_list[0] - 2)].dist = 2
    particle.nh_dict[dir_in_range(particle.t_dir_list[0] + 3)].dist = 2


def def_dist_for_2_t(particle):
    particle.nh_dict[dir_in_range(particle.t_dir_list[0] - 1)].dist = 1
    particle.nh_dict[dir_in_range(particle.t_dir_list[0] + 1)].dist = 1
    if particle.nh_dict[dir_in_range(particle.t_dir_list[0] + 2)].type == "t":
        particle.nh_dict[dir_in_range(particle.t_dir_list[0] + 3)].dist = 1
        particle.nh_dict[dir_in_range(particle.t_dir_list[0] - 2)].dist = 2
    elif particle.nh_dict[dir_in_range(particle.t_dir_list[0] + 3)].type == "t":
        particle.nh_dict[dir_in_range(particle.t_dir_list[0] + 2)].dist = 1
        particle.nh_dict[dir_in_range(particle.t_dir_list[0] - 2)].dist = 1
    else:
        particle.nh_dict[dir_in_range(particle.t_dir_list[0] + 3)].dist = 1
        particle.nh_dict[dir_in_range(particle.t_dir_list[0] + 2)].dist = 2


def def_dist_for_3_t(particle):
    i = 0
    for i in range(0, 3):
        if particle.nh_dict[dir_in_range(particle.t_dir_list[i] + 1)].type == "t" \
                and particle.nh_dict[dir_in_range(particle.t_dir_list[i] - 1)].type == "t":
            particle.nh_dict[dir_in_range(particle.t_dir_list[i] + 2)].dist = 1
            particle.nh_dict[dir_in_range(particle.t_dir_list[i] - 2)].dist = 1
            particle.nh_dict[dir_in_range(particle.t_dir_list[i] + 3)].dist = 2
    if i == 3:
        for dir in direction:
            if dir not in particle.t_dir_list:
                particle.nh_dict[dir].dist = 1


def def_dist_for_4_5_t(particle):
    for dir in direction:
        if dir not in particle.t_dir_list:
            particle.nh_dict[dir].dist = 1


def check_beside_fl(dir, particle):
    if particle.nh_dict[dir_in_range(dir + 1)].type == "fl" \
            and particle.nh_dict[dir_in_range(dir - 1)].type == "fl":
        particle.nh_dict[dir].dist = particle.own_dist + 1
    else:
        particle.nh_dict[dir].dist = particle.own_dist