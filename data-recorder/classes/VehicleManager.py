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
    Helper class to spawn and manage neighbor vehicles
    """
    def __init__(self):
        self.deviation_counter = 0.0
        self.vehicles_list = []
        self.vehicleswap_counter = 0
        self.indices_of_vehicles = []
        
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

        vehicle.set_transform(carla.Transform(waypoint_list[0 + 6 * int(config.isThirdPerson)].transform.location + 
                                              waypoint_list[0 + 6 * int(config.isThirdPerson)].transform.get_right_vector() * oscillation * (2/math.pi * math.asin(math.sin(self.deviation_counter))),
                                              carla.Rotation(pitch  = waypoint_list[0 + 6 * int(config.isThirdPerson)].transform.rotation.pitch, 
                                                             yaw    = waypoint_list[0 + 6 * int(config.isThirdPerson)].transform.rotation.yaw + angle * math.sin(self.deviation_counter), 
                                                             roll   = waypoint_list[0 + 6 * int(config.isThirdPerson)].transform.rotation.roll)))
        
        # Finally look for a new future waypoint to append to the list and show the lanepoints accordingly
        self.potential_new_waypoints = waypoint_list[-1].next(config.meters_per_frame)
        new_waypoint = random.choice(self.potential_new_waypoints)
        waypoint_list.append(new_waypoint)
        
        return new_waypoint
        
        
    def spawn_vehicles(self, world):
        """
        Spawns 5 random vehicles on the map. 
        Speed of the vehicles will be adjusted later, when they 
        are "attached" to the own car.

        Args:
            world: carla.World. Get the spawnpoints from the world object.
        """
        self.transforms = [carla.Transform(carla.Location(-1000,-1000,0)),
                           carla.Transform(carla.Location(-1000,-1010,0)),
                           carla.Transform(carla.Location(-1000,-1020,0)),
                           carla.Transform(carla.Location(-1000,-1030,0)),
                           carla.Transform(carla.Location(-1000,-1040,0))]
        
        spawn_points = world.get_map().get_spawn_points()
        vehicles = world.get_blueprint_library().filter('vehicle.*')
        cars = [vehicle for vehicle in vehicles if int(vehicle.get_attribute('number_of_wheels')) == 4]
        random.shuffle(cars)
        
        for i, car in enumerate(cars[:5]):
            neighbor_vehicle = world.spawn_actor(car, spawn_points[i])
            neighbor_vehicle.set_simulate_physics(False)
            neighbor_vehicle.set_transform(self.transforms[i])
            self.vehicles_list.append(neighbor_vehicle)
            

    def move_vehicles(self, waypoint_list, frame_counter=50):
        """
        Move the neighbor vehicles with the same speed as the own vehicle. 
        Methods are encapsulated in nested function to prevent calling
        them from outside, since they only should be called all together 
        and not individually.

        Args:
            waypoint_list: list. Access the waypoints from the waypoint_list to check lane information.
            frame_counter: int. Use the frame_counter to determine, when to randomly swap the neighbor vehicles. 
        """
        def move_mid_vehicle():
            if(waypoint_list[self.waypoint_indices[0]]):
                next_transform = carla.Transform(waypoint_list[self.waypoint_indices[0]].transform.location, 
                                                 waypoint_list[self.waypoint_indices[0]].transform.rotation)
                self.vehicles_list[0].set_transform(next_transform)
            else:
                self.vehicles_list[0].set_transform(self.transforms[0])
        
        def move_far_left_vehicle():
            if(waypoint_list[self.waypoint_indices[1]].get_left_lane() and 
               waypoint_list[self.waypoint_indices[1]].get_left_lane().lane_type == carla.LaneType.Driving and 
               waypoint_list[self.waypoint_indices[1]].get_left_lane().transform.rotation == waypoint_list[self.waypoint_indices[1]].transform.rotation):
                next_transform = carla.Transform(waypoint_list[self.waypoint_indices[1]].get_left_lane().transform.location, 
                                                 waypoint_list[self.waypoint_indices[1]].get_left_lane().transform.rotation)
                self.vehicles_list[1].set_transform(next_transform)
            else:
                self.vehicles_list[1].set_transform(self.transforms[1])

        def move_far_right_vehicle():
            if(waypoint_list[self.waypoint_indices[2]].get_right_lane() and 
               waypoint_list[self.waypoint_indices[2]].get_right_lane().lane_type == carla.LaneType.Driving and 
               waypoint_list[self.waypoint_indices[2]].get_right_lane().transform.rotation == waypoint_list[self.waypoint_indices[2]].transform.rotation):
                next_transform = carla.Transform(waypoint_list[self.waypoint_indices[2]].get_right_lane().transform.location, 
                                                 waypoint_list[self.waypoint_indices[2]].get_right_lane().transform.rotation)
                self.vehicles_list[2].set_transform(next_transform)
            else:
                self.vehicles_list[2].set_transform(self.transforms[2])
                
        def move_close_left_vehicle():
            if(waypoint_list[self.waypoint_indices[3]].get_left_lane() and 
                waypoint_list[self.waypoint_indices[3]].get_left_lane().lane_type == carla.LaneType.Driving and 
                waypoint_list[self.waypoint_indices[3]].get_left_lane().transform.rotation == waypoint_list[self.waypoint_indices[3]].transform.rotation):
                next_transform = carla.Transform(waypoint_list[self.waypoint_indices[3]].get_left_lane().transform.location, 
                                                  waypoint_list[self.waypoint_indices[3]].get_left_lane().transform.rotation)
                self.vehicles_list[3].set_transform(next_transform)
            else:
                self.vehicles_list[3].set_transform(self.transforms[3])

        def move_close_right_vehicle():
            if(waypoint_list[self.waypoint_indices[4]].get_right_lane() and 
                waypoint_list[self.waypoint_indices[4]].get_right_lane().lane_type == carla.LaneType.Driving and 
                waypoint_list[self.waypoint_indices[4]].get_right_lane().transform.rotation == waypoint_list[self.waypoint_indices[4]].transform.rotation):
                next_transform = carla.Transform(waypoint_list[self.waypoint_indices[4]].get_right_lane().transform.location, 
                                                  waypoint_list[self.waypoint_indices[4]].get_right_lane().transform.rotation)
                self.vehicles_list[4].set_transform(next_transform)
            else:
                self.vehicles_list[4].set_transform(self.transforms[4])
        
        # Each move function is being mapped with an index, so we just use the index to move a neighbor vehicle
        movement_map = {0: move_mid_vehicle,
                        1: move_far_left_vehicle,
                        2: move_far_right_vehicle,
                        3: move_close_left_vehicle,
                        4: move_close_right_vehicle}

        for i in self.indices_of_vehicles:
            movement_map[i]()
        
        # Randomly swap the cars
        if(self.vehicleswap_counter > frame_counter):
            number_of_vehicles = random.randint(0, 5)                                   # how many cars to spawn?
            self.indices_of_vehicles = random.sample(range(0,5), number_of_vehicles)    # which vehicles' index?
            self.waypoint_indices = [random.randint(10,30),                             # where to spawn at?
                                     random.randint(20,30),
                                     random.randint(20,30),
                                     random.randint(0,12),
                                     random.randint(0,12)]

            # Despawn them for a short moment to "clean up" road
            for i, vehicle in enumerate(self.vehicles_list):
                vehicle.set_transform(self.transforms[i])
            
            self.vehicleswap_counter = 0

        self.vehicleswap_counter += 1


    def destroy(self):
        for vehicle in self.vehicles_list:
            vehicle.destroy()