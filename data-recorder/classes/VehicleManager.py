# ------------------------------------------------------
# Import base library
import  os
import  sys
import  glob
import  math
import  random
from    utils.prints \
        import  *
import  configs as config

# ------------------------------------------------------
# Find carla library
try:
    sys.path.append(glob.glob("../carla/dist/carla-*%d.%d-%s.egg" % (
        sys.version_info.major,
        sys.version_info.minor,
        "win-amd64" if os.name == "nt" else "linux-x86_64"))[0])
except  IndexError:
    pass
import  carla


# ------------------------------------------------------
# VehicleManager Library
class   VehicleManager():
    """
    Helper class to spawn and manage vehicle
    """
    def __init__(self):
        self.deviation_counter = 0.0
        
        if not config.junctionMode:
            self.junctionInSightCounter = config.number_of_lanepoints
        
        print_info("VehicleManager initialize done")
        print_end()

    def detect_junction(self, waypoint_list):
        """
        Detects, whether the actual image contains a junction. 
        Because of a long multi-lane highway in Town04, the argument here is different to other towns. Carla doesn't distinguish junctions, 
        so a highway access is a junction as well. To avoid these normal pictures from being filtered out, we just detect multiple choices of drivable directions as a junction.
        While this is possible in Town04, other towns have to many special cases, where errors would be included in the dataset, so we have to check junctions the normal way.
        The junctionInSightCounter describes how many images from the actual one shouldn't be saved. 

        Args:
            waypoint_list: list. List of waypoints where the vehicle will be next.
        """
        if not config.junctionMode:
            if config.CARLA_TOWN == ('Town04' or 'Town06'):
                res =[i for i,v in enumerate(waypoint_list) if len(v.next(config.meters_per_frame))>1]
                if res:
                    junction_argument = res[0] < config.number_of_lanepoints - 15
                else:
                    junction_argument = False
                #junction_argument = len(self.potential_new_waypoints) > 1
                offset = 20
            else:
                res =[i for i,v in enumerate(waypoint_list) if v.is_junction]
                if res:
                    junction_argument = res[0] < config.number_of_lanepoints - 15
                else:
                    junction_argument = False

                offset = 0
            # Junctions are not included in the set of trainingsdata, so we jump over every picture where a junction is in sight 
            if junction_argument:
                self.junctionInSightCounter = config.number_of_lanepoints - 20 + offset
            else:
                self.junctionInSightCounter -= 1     
    
    def move_agent(self, vehicle, waypoint_list):
        """
        Move the own agent along the given waypoints in waypoint_list.
        After we moved to the first position of the list, we need to look 
        out for a new future waypoint to append to the list, which is chosen 
        randomly. The waypoint_list always contains a fixed number of waypoints.

        Args:
            vehicle: carla.Actor. Vehicle to move along the given waypoints.
            waypoint_list: list. List of waypoints to move the vehicle along.

        Returns:
            new_waypoint: carla.Waypoint. Append the new_waypoint to the waypoint_list every tick.
        """
        self.deviation_counter += 0.08
        
        if config.isCenter:
            oscillation = 0.2
            angle = 3
        else:
            oscillation = 1
            angle = 10

        vehicle.set_transform(carla.Transform(waypoint_list[0].transform.location + 
                                              waypoint_list[0].transform.get_right_vector() * oscillation * (2/math.pi * math.asin(math.sin(self.deviation_counter))),
                                              carla.Rotation(pitch  = waypoint_list[0].transform.rotation.pitch, 
                                                             yaw    = waypoint_list[0].transform.rotation.yaw + angle * math.sin(self.deviation_counter), 
                                                             roll   = waypoint_list[0].transform.rotation.roll)))

        # Finally look for a new future waypoint to append to the list and show the lanepoints accordingly
        self.potential_new_waypoints = waypoint_list[-1].next(config.meters_per_frame)
        new_waypoint = random.choice(self.potential_new_waypoints)
        waypoint_list.append(new_waypoint)
        
        return new_waypoint