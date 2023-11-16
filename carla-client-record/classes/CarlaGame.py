# ------------------------------------------------------
# Import base library
import  os
import  sys
import  glob
import  random
import  pygame
from    collections \
        import  deque

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
# Import Custom Libraries
from    settings.gets \
        import  get_font
from    classes.CarlaClient \
        import  CarlaClient
from    util.prints \
        import  *

# ------------------------------------------------------
# CarlaGame Class
class   CarlaGame(CarlaClient):
    def __init__(self, args, config, lanes):
        # client, client-timeout, world, and map as args and configs
        super.__init__(args)
        
        # value setting from args & configs
        self.lanes          = lanes
        self.config         = config
        self.window         = (self.config.width, self.config.height)
        self.filename       = f"{self.config.output_directory}/{self.config.CARLA_TOWN}/"

        # display setting
        self.display        = pygame.display.set_mode(
            self.window, 
            pygame.HWSURFACE | pygame.DOUBLEBUF
        )
        self.font           = get_font()
        self.clock          = pygame.time.Clock()
        
        # map setting
        self.lane_marker    = LaneMarker()
        self.vehicle_manager= VehicleManager()
        self.image_saver    = BufferedImageSaver(
                                self.filename,
                                self.config.numberOfImages,
                                self.config.width,
                                self.config.height,
                                3,  # depth
                                ''  # sensorname
                            )
        self.label_saver    = LabelSaver(self.train_gt)
        self.image_counter  = 0

        if self.config.isThirdPerson:
            self.camera_transforms=[carla.Transform(carla.Location(x=-4.5, z=2.2), carla.Rotation(pitch=-14.5)),
                                    carla.Transform(carla.Location(x=-4.0, z=2.2), carla.Rotation(pitch=-18.0))]
        else:
            self.camera_transforms=[carla.Transform(carla.Location(x=0.0,  z=3.2), carla.Rotation(pitch=-19.5)), # camera 1
                                    carla.Transform(carla.Location(x=0.0,  z=2.8), carla.Rotation(pitch=-18.5)), # camera 2
                                    carla.Transform(carla.Location(x=0.3,  z=2.4), carla.Rotation(pitch=-15.0)), # camera 3
                                    carla.Transform(carla.Location(x=1.1,  z=2.0), carla.Rotation(pitch=-16.5)), # camera 4
                                    carla.Transform(carla.Location(x=1.0,  z=2.0), carla.Rotation(pitch=-18.5)), # camera 5
                                    carla.Transform(carla.Location(x=1.4,  z=1.2), carla.Rotation(pitch=-13.5)), # camera 6
                                    carla.Transform(carla.Location(x=1.8,  z=1.2), carla.Rotation(pitch=-14.5)), # camera 7
                                    carla.Transform(carla.Location(x=2.17, z=0.9), carla.Rotation(pitch=-14.5)), # camera 8
                                    carla.Transform(carla.Location(x=2.2,  z=0.7), carla.Rotation(pitch=-11.5))] # camera 9

    def reset_vehicle_position(self):
        """
        Resets the vehicle's position on the map. reset the agent creates 
        a new route of (number_of_lanepoints) waypoints to follow along. 
        """
        self.start_position = random.choice(self.map.get_spawn_points())
        waypoint = self.map.get_waypoint(self.start_position.location)

        # Initialize lane deques with a fixed number of lanepoints
        for lane in self.lanes:
            for lanepoint in range(0, self.config.number_of_lanepoints):
                lane.append(None)

        # Create n waypoints to have an initial route for the vehicle
        self.waypoint_list = deque(maxlen=self.config.number_of_lanepoints)

        for i in range(0, self.config.number_of_lanepoints):
            self.waypoint_list.append(waypoint.next(i + self.config.meters_per_frame)[0])
        
        for lanepoint in self.waypoint_list:
            lane_markings = self.lane_marker.calculate3DLanepoints(
                self.client,
                lanepoint
            )
        
        camera_index = random.randint(0, len(self.camera_transforms)-1)

        self.camera_rgb.set_transform(self.camera_transforms[camera_index])
        self.camera_semseg.set_transform(self.camera_transforms[camera_index])
        print_info("Camera Index:", camera_index)
        print_end()

        if self.config.draw3DLanes:
            for i, color in enumerate(self.lane_marker.colormap_carla):
                for j in range(0, self.config.number_of_lanepoints-1):
                    self.lane_marker.draw_lines(
                        self.client,
                        lane_markings[i][j],
                        lane_markings[i][j+1],
                        self.lane_marker.colormap_carla[color]
                    )

    def detect_lanemarkings(self, new_waypoint, image_semseg):
        lanes_list      = []    # filtered 2D-Points
        x_lanes_list    = []    # only x values of lanes
        lanes_3Dcoords  = self.lane_marker.calculate3DLanepoints(
            self.client,
            new_waypoint
        )

        for lane_3Dcoords in lanes_3Dcoords:
            lane = self.lane_marker.calculate2DLanepoints(self.camera_rgb, lane_3Dcoords)
            lane = self.lane_marker.calculateYintersections(lane)
            lane = self.lane_marker.filter2DLanepoints(lane, image_semseg)
            
            lanes_list.append(lane)
            x_lanes_list.append(self.lane_marker.format2DLanepoints(lane))
        
        return lanes_list, x_lanes_list

    def initialize(self):
        self.blueprint_library = self.world.get_blueprint_library()
        self.start_position = random.choice(self.map.get_spawn_points())
        self.vehicle = self.world.spawn_actor(random.choice(self.blueprint_library.filter("vehicle.ford.mustang")), self.start_position)
        self.actor_list.append(self.vehicle)
        self.vehicle.set_simulate_physics(False)
        self.camera_transforms = self.camera_transforms[random.randint(0, len(self.camera_transforms)-1)]

        self.bp_camera_rgb = self.blueprint_library.find("sensor.camera.rgb")
        self.bp_camera_rgb.set_attribute("image_size_x", f"{self.config.width}")
        self.bp_camera_rgb.set_attribute("image_size_y", f"{self.config.height}")
        self.bp_camera_rgb.set_attribute("fov",          f"{self.config.FOV}")
        self.camera_rgb_spawnpoint = self.camera_transforms
        self.camera_rgb = self.world.spawn_actor(
            self.bp_camera_rgb,
            self.camera_rgb_spawnpoint,
            attach_to=self.vehicle)
        self.actor_list.append(self.camera_rgb)

        self.bp_camera_semseg = self.blueprint_library.find("sensor.camera.semantic_segmentation")
        self.bp_camera_semseg.set_attribute("image_size_x", f"{self.config.width}")
        self.bp_camera_semseg.set_attribute("image_size_y", f"{self.config.height}")
        self.bp_camera_semseg.set_attribute("fov",          f"{self.config.FOV}")
        self.camera_semseg_spawnpoint = self.camera_transforms
        self.camera_semseg = self.world.spawn_actor(
            self.bp_camera_semseg,
            self.camera_semseg_spawnpoint,
            attach_to=self.vehicle)
        self.actor_list.append(self.camera_semseg)

        self.reset_vehicle_position()

        self.vehicle_manager.spawn_vehicles(self.world)

    def launch(self):
        print()