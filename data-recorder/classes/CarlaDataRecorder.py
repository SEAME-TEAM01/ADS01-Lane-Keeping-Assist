# ------------------------------------------------------
# Import base library
import  os
import  sys
import  glob
import  random
import  pygame
from    collections \
        import  deque

import  configs as config
from    utils.prints \
        import  *
from    utils.gets \
        import  get_font
from    utils.features \
        import  reshape_image, \
                draw_image, \
                should_quit

from    classes.CarlaClient \
        import  CarlaClient
from    classes.LaneMarker \
        import  LaneMarker
from    classes.VehicleManager \
        import  VehicleManager
from    classes.CarlaSyncMode \
        import  CarlaSyncMode
from    classes.DatasetSaver \
        import  DatasetSaver


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
# CarlaDataRecorder Class
class   CarlaDataRecorder(CarlaClient):
    def __init__(self, args, lanes):
        # client, client-timeout, world, and map as args and configs
        super().__init__(args)
        self.lanes          = lanes
        
        # pygame setting
        pygame.init()
        print_end()
        self.window         = (config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
        self.display        = pygame.display.set_mode(
            self.window, 
            pygame.HWSURFACE | pygame.DOUBLEBUF
        )
        self.font           = get_font()
        self.clock          = pygame.time.Clock()

        # output setting
        self.actor_list     = []
        self.reset_counter  = 0
        
        # manager setting
        self.lane_marker    = LaneMarker(self.lanes)
        self.vehicle_manager= VehicleManager()
        self.dataset_saver  = DatasetSaver(
                                config.CARLA_TOWN,
                                config.h_samples, 
                                config.label_directory,
                                config.train_gt,
                                config.image_directory,
                                config.WINDOW_WIDTH,
                                config.WINDOW_HEIGHT,
                                config.masks_directory)

        # self.camera_transforms=[carla.Transform(carla.Location(x=0.0,  z=3.2), carla.Rotation(pitch=-19.5)), # camera 1
        #                         carla.Transform(carla.Location(x=0.0,  z=2.8), carla.Rotation(pitch=-18.5)), # camera 2
        #                         carla.Transform(carla.Location(x=0.3,  z=2.4), carla.Rotation(pitch=-15.0)), # camera 3
        #                         carla.Transform(carla.Location(x=1.1,  z=2.0), carla.Rotation(pitch=-16.5)), # camera 4
        #                         carla.Transform(carla.Location(x=1.0,  z=2.0), carla.Rotation(pitch=-18.5)), # camera 5
        #                         carla.Transform(carla.Location(x=1.4,  z=1.2), carla.Rotation(pitch=-13.5)), # camera 6
        #                         carla.Transform(carla.Location(x=1.8,  z=1.2), carla.Rotation(pitch=-14.5)), # camera 7
        #                         carla.Transform(carla.Location(x=2.17, z=0.9), carla.Rotation(pitch=-14.5)), # camera 8
        #                         carla.Transform(carla.Location(x=2.2,  z=0.7), carla.Rotation(pitch=-11.5))] # camera 9
        self.camera = carla.Transform(carla.Location(x=1.5,  z=2.0), carla.Rotation(pitch=-14.5))

        self.start_positions = []
        if config.CARLA_TOWN is "":
            raise RuntimeError("CARLA_TOWN is not defined")
        elif config.CARLA_TOWN is "Town03_Opt":
            self.start_positions.append([
                carla.Transform(carla.Location(x=-85.302979, y=156.585388, z=0.003271),carla.Rotation(pitch=0.000376, yaw=87.022415, roll=0.000014)),
                270
            ])
            self.start_positions.append([
                carla.Transform(carla.Location(x=241.111710, y=35.939137, z=0.018846),carla.Rotation(pitch=0.001667, yaw=-86.087097, roll=0.000035)),
                270
            ])
            self.start_positions.append([
                carla.Transform(carla.Location(x=169.453049, y=-194.047333, z=-0.021909),carla.Rotation(pitch=0.038147, yaw=-0.862884, roll=-0.000122)),
                270
            ])
        elif config.CARLA_TOWN is "Town07_Opt":
            self.start_positions.append([
                carla.Transform(carla.Location(x=-24.028019, y=-246.138351, z=0.860913),carla.Rotation(pitch=4.539699, yaw=-170.428787, roll=-0.149170)),
                200
            ])
            self.start_positions.append([
                carla.Transform(carla.Location(x=82.813736, y=47.457050, z=0.027074),carla.Rotation(pitch=-0.011598, yaw=-70.911583, roll=-0.000183)), 
                30
            ])
            self.start_positions.append([
                carla.Transform(carla.Location(x=61.971699, y=-85.821495, z=6.278840),carla.Rotation(pitch=4.703701, yaw=-80.328285, roll=0.000000)),
                150
            ])
            self.start_positions.append([
                carla.Transform(carla.Location(x=-59.366730, y=-239.509918, z=3.687235),carla.Rotation(pitch=4.545931, yaw=-219.917603, roll=0.000000)),
                180
            ])
        elif config.CARLA_TOWN is "Town10HD_Opt":
            self.start_positions.append([
                carla.Transform(carla.Location(x=-114.218651, y=41.329021, z=0.002613), carla.Rotation(pitch=0.128858, yaw=90.870064, roll=-0.008606)),
                310
            ])
            self.start_positions.append([
                carla.Transform(carla.Location(x=106.213867, y=0.070332, z=-0.001398), carla.Rotation(pitch=-0.004426, yaw=-90.735901, roll=-0.000000)),
                80
            ])
            self.start_positions.append([
                carla.Transform(carla.Location(x=101.876251, y=58.557976, z=0.003270), carla.Rotation(pitch=0.000417, yaw=90.004517, roll=0.000000)),
                310
            ])
        else:
            for spawn_point in self.map.get_spawn_points():
                self.start_positions.append([spawn_point, config.images_until_respawn])
        print_info("CarlaGame initialize done")
        print_end()

    def reset_vehicle_position(self):
        """
        Resets the vehicle's position on the map. reset the agent creates 
        a new route of (number_of_lanepoints) waypoints to follow along. 
        """
        _chosen                     = random.choice(self.start_positions)
        self.start_position         = _chosen[0]
        config.images_until_respawn = _chosen[1]
        self.reset_counter          = self.dataset_saver.index

        print_info(f"{BOLD}[Reset-Vehicle-Position]{RESET} chosen spawnpoint is {self.start_position}, {self.start_position.location}")
        # for spawn_point in self.map.get_spawn_points():
        #     print("\tspawn_point:", spawn_point, ", ", spawn_point.location)
        waypoint = self.map.get_waypoint(self.start_position.location)
        print_end()

        # Initialize lane deques with a fixed number of lanepoints
        for lane in self.lanes:
            for lanepoint in range(0, config.number_of_lanepoints):
                lane.append(None)

        # Create n waypoints to have an initial route for the vehicle
        self.waypoint_list = deque(maxlen=config.number_of_lanepoints)

        for i in range(0, config.number_of_lanepoints):
            self.waypoint_list.append(waypoint.next(i + config.meters_per_frame)[0])
        for lanepoint in self.waypoint_list:
            lane_markings = self.lane_marker.calculate3DLanepoints(
                self.client,
                lanepoint
            )

        self.camera_rgb.set_transform(self.camera)
        self.camera_semseg.set_transform(self.camera)

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

    def render_display(self, image, x_lanes_list, lanes_list, render_lanes=True):
        """
        Renders the images captured from both cameras and shows it on the
        pygame display

        Args:
            image: numpy array. Shows the 3-channel numpy imagearray on the pygame display.
            image_semseg: numpy array. Shows the semantic segmentation image on the pygame display.
        """
        draw_image(self.display, image)

        # image save without lane points
        if config.isSaving:
            self.dataset_saver.save(self.display, x_lanes_list)

        if render_lanes:
            for i, color in enumerate(self.lane_marker.colormap):
                if lanes_list[i]:
                    for j in range(len(lanes_list[i])):
                        pygame.draw.circle(self.display, self.lane_marker.colormap[color], lanes_list[i][j], 3, 2)
        
        self.display.blit(self.font.render('% 5d FPS ' % self.clock.get_fps(), True, (255, 255, 255)), (8, 10))
        self.display.blit(self.font.render('Map: ' + config.CARLA_TOWN, True, (255, 255, 255)), (20, 50))

        # # image save with lane points
        # if config.isSaving:
        #     self.dataset_saver.save(self.display, x_lanes_list)

        pygame.display.flip()

    def on_gameloop(self):
        """
        Determines the logic of movement and what should happen every frame. 
        Also adds an image to the image saver and the corresponding label to the label saver, if the frame is meant to be saved. 
        In the actual implementation the points, which will be saved, are drawn to the screen on runtime (not on the saved images).
        """
        self.clock.tick()
        
        # Advance the simulation and wait for the data.
        snapshot, image_rgb, image_semseg = self.sync_mode.tick(timeout=1.0)

        # Move own vehicle to the next waypoint
        new_waypoint = self.vehicle_manager.move_agent(self.vehicle, self.waypoint_list)
        print_info(f"{BOLD}[on_gameloop]{RESET} index: {self.dataset_saver.index} waypoint {new_waypoint}")
        
        # Detect if junction is ahead
        self.vehicle_manager.detect_junction(self.waypoint_list)
        
        # Convert and reshape image from Nx1 to shape(720, 1280, 3)
        image_semseg.convert(carla.ColorConverter.CityScapesPalette)
        image_semseg = reshape_image(image_semseg)
        
        # Calculate all the lanes with the helper class 'LaneMarkings'
        lanes_list, x_lanes_list = self.detect_lanemarkings(new_waypoint, image_semseg)
        
        # Render the pygame display and show the lanes accordingly
        self.render_display(image_rgb, x_lanes_list, lanes_list, config.draw3DLanes)
        
        if config.isSaving:
            if(self.dataset_saver.index % (config.images_until_respawn + self.reset_counter) == 0):
                self.reset_vehicle_position()

    def initialize(self):
        self.blueprint_library = self.world.get_blueprint_library()
        self.start_position = random.choice(self.map.get_spawn_points())
        self.vehicle = self.world.spawn_actor(random.choice(self.blueprint_library.filter("vehicle.ford.mustang")), self.start_position)
        self.actor_list.append(self.vehicle)
        self.vehicle.set_simulate_physics(False)

        self.bp_camera_rgb = self.blueprint_library.find("sensor.camera.rgb")
        self.bp_camera_rgb.set_attribute("image_size_x", f"{config.WINDOW_WIDTH}")
        self.bp_camera_rgb.set_attribute("image_size_y", f"{config.WINDOW_HEIGHT}")
        self.bp_camera_rgb.set_attribute("fov",          f"{config.FOV}")
        self.camera_rgb_spawnpoint = self.camera
        self.camera_rgb = self.world.spawn_actor(
            self.bp_camera_rgb,
            self.camera_rgb_spawnpoint,
            attach_to=self.vehicle)
        self.actor_list.append(self.camera_rgb)

        self.bp_camera_semseg = self.blueprint_library.find("sensor.camera.semantic_segmentation")
        self.bp_camera_semseg.set_attribute("image_size_x", f"{config.WINDOW_WIDTH}")
        self.bp_camera_semseg.set_attribute("image_size_y", f"{config.WINDOW_HEIGHT}")
        self.bp_camera_semseg.set_attribute("fov",          f"{config.FOV}")
        self.camera_semseg_spawnpoint = self.camera
        self.camera_semseg = self.world.spawn_actor(
            self.bp_camera_semseg,
            self.camera_semseg_spawnpoint,
            attach_to=self.vehicle)
        self.actor_list.append(self.camera_semseg)

        self.reset_vehicle_position()

    def launch(self):
        try:
            self.initialize()

            with CarlaSyncMode(
                self.world,
                self.camera_rgb,
                self.camera_semseg,
                fps=config.FPS
            ) as self.sync_mode:
                while True:
                    if should_quit():
                        return
                    self.on_gameloop()
        finally:
            print_info("Saving files...")
            self.dataset_saver.close_file()
            print_end()

            print_info("Destroying actors and cleaning up...")
            for actor in self.actor_list:
                actor.destroy()
            print_end()

            pygame.quit()
            print_success("Done.")
            print_end()