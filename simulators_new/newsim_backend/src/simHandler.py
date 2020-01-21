# from .__main__ import SimulatorMetaClass
import asyncio
import math
from . import mathUtils
# TODO:
# - detect object > done!
# - detect obstacle > uses the same function as the above,
# with different parameters
# - update rover coords > done...?

# ACCORDING TO SEARCH FOR GATE ALGORITHM:
# 1. Arrived at waypoint
# 2. If waypoint is gate, begin search
# 3. --Search State Machine--
# whenever a tennis ball is found, check to see if second tennis ball is found
# if two targets found, jump to drive through gate
# 4. If two tags are found:
# a) drop tag locations
# b) drive through gate state
# 5. If 1 tag found and waypoint was gate:
# a) save location of tag 1
# b) begin gate search
# 6. If second tag < 2m from tag 1 location, continue search
# 7. If second tag > 2m from tag 1 location, drive between gate
# 8. Drive between gate: on approach, check if front or back of gate
# After driving through, turn around and check if front or back of gate


# contains the initialization code for initial setup of the field
def initObjectsOnField(sim):
    startPos = sim.GPS(39, 0, -110, 0, 0, 0)
    field = sim.Field(startPos)  # make field entity and rover
    rover = sim.Rover(startPos, sim.JoystickMsg.dampen, 1, 1)
    return rover, field  # if we init more than this, return a list
    # for future reference, this is where uploaded test cases get init


def addObject(sim, obj_struct, obj_type):  # this may be implemented
    # in a way that it totally not necessary

    # used later to add object from frontend
    if obj_type == "obstacle":
        sim.Obstacles.append(obj_struct)
    elif obj_type == "waypoint":
        sim.Waypoints.append(obj_struct)
    elif obj_type == "tennis ball":
        sim.Tennis_Balls.append(obj_struct)
    else:
        print("Object passed is not valid")


def removeObject(sim, obj_in):
    # used later to remove object from frontend
    # uses built-in id() function to identify instance we seek
    for item in sim.Waypoints:
        if id(item) == id(obj_in):
            sim.Waypoints.remove(obj_in)
            break
    for item in sim.Tennis_Balls:
        if id(item) == id(obj_in):
            sim.Waypoints.remove(obj_in)
            break
    for item in sim.Obstacles:
        if id(item) == id(obj_in):
            sim.Waypoints.remove(obj_in)
            break

    # debug code
    print("Object does not exist in list, can't be removed")
    pass


def calc_move_best_path(sim, object_list, rover, delta_y, delta_x):
    # TODO: Check logic, though seems good enough
    angle = math.atan2(delta_y, delta_x)
    if angle >= 0:
        diff = rover.fov/2 - angle
        rover.move_rot(-diff)
        return -diff
    else:
        diff = rover.fov/2 + angle
        rover.move_rot(-diff)
        return -diff


def calc_visible(sim, object_list):
    delta_x = 0  # TODO: needs to be math'd out
    delta_y = 0  # TODO: ditto to this m80
    for item in object_list:
        if (math.atan2(delta_y, delta_x) < sim.rover.fov / 2 and
                math.hypot(delta_x, delta_y) < sim.rover.cv_thresh):
            # checking if object is within
            # fov and detection distance (cv_thresh)
            if isinstance(item, sim.TennisBall):  # detect which object
                sim.TennisBallMsg.found = True
                sim.TennisBallMsg.distance = math.hypot(delta_x, delta_y)
                sim.TennisBallMsg.bearing = math.atan2(delta_y, delta_x)
            if isinstance(item, sim.Obstacle):
                sim.ObstacleMsg.detected = True
                sim.ObstacleMsg.bearing = calc_move_best_path(
                    sim, object_list, sim.rover,
                    delta_x, delta_y
                )
                # calculates best path away from the obstacle, not bearing to
    # for obj in object_list:
        # rover loc - obj loc = delta loc
        # use some trig and get your results
        # for tennis balls, mark if found

# a helper function for move_trans


def changeRoverPos(sim, deltaDeg):
    sim.rover.lat_deg = deltaDeg.lat_deg
    sim.rover.lat_min = deltaDeg.lat_min
    sim.rover.lon_deg = deltaDeg.lon_deg
    sim.rover.long_min = deltaDeg.lon_min


# move translationally, if distance is specified you move that many meters,
# otherwise you move at normal velocity
def move_trans(sim):
    # method to move translationally
    # uses joystick input to determine speed
    speed_trans = sim.rover.speed_translational * \
        ((1 - sim.JoystickMsg.dampen) / 2) * sim.JoystickMsg.forward_back
    deltaDeg = mathUtils.meters2deg(sim, speed_trans, sim.rover.bearing)
    changeRoverPos(sim, deltaDeg)


def move_rot(sim):  # method to rotate
    speed_rot = sim.rover.speed_rotational * \
        ((1 - sim.JoystickMsg.dampen) / 2) * sim.JoystickMsg.left_right
    sim.rover.bearing += speed_rot


def move_interpolate(sim, angle, distance):
    pass
    # would be used to calculate rover moving and turning
    # at the same time, since the rover can move and slightly
    # turn at the same time on the IRL rover
    # this is not currently used, but is here for later


async def simulatorOn(sim):
    while True:
        if sim.AutonStateMsg.is_auton is not True:
            break
        else:
            calc_visible(sim, sim.Tennis_Balls)
            calc_visible(sim, sim.Obstacles)
            move_trans(sim)
            move_rot(sim)
        await asyncio.sleep(10)


async def runSimulator(sim):
    sim.rover, sim.field = initObjectsOnField(sim)
    # need a frontend mechanism to actually turn auton_state to true

    while True:
        print("Sim ran!")
        if sim.AutonStateMsg.is_auton is True:
            simulatorOn(sim)
        await asyncio.sleep(10)
