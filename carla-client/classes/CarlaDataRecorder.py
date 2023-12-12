# ------------------------------------------------------
# Import base library
import  sys
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
    sys.path.append(config.CARLA_DIR)
    import  carla
except  IndexError:
    print_failure("Failed to import carla egg file.")

# ------------------------------------------------------
# CarlaDataRecorder Class
class   CarlaDataRecorder(CarlaClient):
    def __init__(self, args, lanes):
        # client, client-timeout, world, and map as args and configs
        super().__init__(args)
        self.lanes          = lanes
        settings = self.world.get_settings()
        if config.noRendering == True:
            settings.no_rendering_mode = True
        self.world.apply_settings(settings)
        
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

        self.camera = carla.Transform(carla.Location(x=1.6, z=1.7))

        self.start_positions = []
        self.start_positions_index = 0
        self.testset_positions = []
        if config.CARLA_TOWN == "":
            raise RuntimeError("CARLA_TOWN is not defined")
        elif config.CARLA_TOWN == "Town03_Opt":
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
        elif config.CARLA_TOWN == "Town07_Opt":
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
        elif config.CARLA_TOWN == "Town06_Opt":
            self.start_positions.append([
                carla.Transform(carla.Location(x=386.040741, y=38.276459, z=-0.005049), carla.Rotation(pitch=-0.003511, yaw=-0.027893, roll=0.000000)), 
                400
            ])
        elif config.CARLA_TOWN == "Town10HD_Opt":
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
        elif config.CARLA_TOWN == "Town11":
            self.start_positions.append([
                carla.Transform(carla.Location(x=6670.942871, y=-2696.028076, z=58.645386), carla.Rotation(pitch=0.241741, yaw=21.042400, roll=0.002043)),
                400
            ])
            self.start_positions.append([
                carla.Transform(carla.Location(x=6939.931641, y=-697.460632, z=44.007175), carla.Rotation(pitch=0.953829, yaw=24.504562, roll=0.016194)),
                400
            ])
            self.start_positions.append([
                carla.Transform(carla.Location(x=7285.354980, y=-2869.584229, z=60.661160), carla.Rotation(pitch=-4.150453, yaw=96.144508, roll=0.188755)),
                400
            ])
        elif config.CARLA_TOWN == "Town15":
            # self.start_positions.append([ # park - path 1
            #     carla.Transform(carla.Location(x=728.285461, y=694.559021, z=117.997192), carla.Rotation(pitch=-0.052524, yaw=-59.337170, roll=-0.078735)),
            #     180,
            # ])
            # self.start_positions.append([ # park - path 2
            #     carla.Transform(carla.Location(x=723.046753, y=742.126831, z=117.998192), carla.Rotation(pitch=0.094332, yaw=32.755676, roll=0.041595)),
            #     600,
            # ])
            # self.start_positions.append([ # park - path 3
            #     carla.Transform(carla.Location(x=482.678711, y=794.510864, z=122.868706), carla.Rotation(pitch=-0.732668, yaw=-11.800282, roll=-0.021667)),
            #     230,
            # ])
            # self.start_positions.append([
            #     carla.Transform(carla.Location(x=273.497955, y=-340.431702, z=152.580505), carla.Rotation(pitch=-0.350040, yaw=-137.467239, roll=-0.006622)),
            #     450
            # ])
            # self.start_positions.append([
            #     carla.Transform(carla.Location(x=-196.286896, y=-613.031799, z=158.521622), carla.Rotation(pitch=3.988202, yaw=14.457486, roll=0.295075)),
            #     600
            # ])
            self.start_positions.append([
                carla.Transform(carla.Location(x=-109.906685, y=127.888123, z=151.391724), carla.Rotation(pitch=-0.984428, yaw=-42.932205, roll=0.088353)),
                650,
            ])
        else:
            for spawn_point in self.map.get_spawn_points():
                self.start_positions.append([spawn_point, config.images_until_respawn])
        print_info("CarlaGame initialize done")
        print_end()

    def reset_vehicle_position(self):
        print_debug("CarlaGame reset_vehicle_position")
        """
        Resets the vehicle's position on the map. reset the agent creates 
        a new route of (number_of_lanepoints) waypoints to follow along. 
        """
        _chosen                     = self.start_positions[self.start_positions_index]
        self.start_position         = _chosen[0]
        config.images_until_respawn = _chosen[1]
        self.reset_counter          = self.dataset_saver.index
        self.start_positions_index  += 1
        if self.start_positions_index >= len(self.start_positions):
            self.start_positions_index = 0

        print_info(f"{BOLD}[Reset-Vehicle-Position]{RESET} respon")
        waypoint = self.map.get_waypoint(self.start_position.location)

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
        print_debug("CarlaGame detect_lanemarkings")
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
        print_debug("CarlaGame render_display")
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

        pygame.display.flip()

    def on_gameloop(self):
        print_debug("CarlaGame on_gameloop")
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
        print_info(f"{BOLD}[on_gameloop]{RESET} index: {self.dataset_saver.index}")
        
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
        print_debug("CarlaGame initialize")
        self.blueprint_library = self.world.get_blueprint_library()
        self.start_position = random.choice(self.map.get_spawn_points())
        if self.start_positions_index >= len(self.start_positions):
            self.start_positions_index = 0
        print_debug("CarlaGame initialize start_position")
        self.vehicle = self.world.spawn_actor(random.choice(self.blueprint_library.filter("vehicle.ford.mustang")), self.start_position)
        self.actor_list.append(self.vehicle)
        # self.vehicle.set_simulate_physics(False)
        print_debug("CarlaGame initialize vehicle spawned")
        self.bp_camera_rgb = self.blueprint_library.find("sensor.camera.rgb")
        self.bp_camera_rgb.set_attribute("image_size_x", f"{config.WINDOW_WIDTH}")
        self.bp_camera_rgb.set_attribute("image_size_y", f"{config.WINDOW_HEIGHT}")
        self.bp_camera_rgb.set_attribute("fov",          f"{config.FOV}")
        print_debug("CarlaGame initialize camera_rgb")
        self.camera_rgb_spawnpoint = self.camera
        print_debug("CarlaGame initialize camera_rgb_spawnpoint")
        self.camera_rgb = self.world.spawn_actor(
            self.bp_camera_rgb,
            self.camera_rgb_spawnpoint,
            attach_to=self.vehicle)
        print_debug("CarlaGame initialize camera_rgb")
        self.actor_list.append(self.camera_rgb)
        print_debug("CarlaGame initialize camera spawned")
        self.bp_camera_semseg = self.blueprint_library.find("sensor.camera.semantic_segmentation")
        self.bp_camera_semseg.set_attribute("image_size_x", f"{config.WINDOW_WIDTH}")
        self.bp_camera_semseg.set_attribute("image_size_y", f"{config.WINDOW_HEIGHT}")
        self.bp_camera_semseg.set_attribute("fov",          f"{config.FOV}")
        print_debug("CarlaGame initialize camera_semseg")
        self.camera_semseg_spawnpoint = self.camera
        print_debug("CarlaGame initialize camera_semseg_spawnpoint")
        self.camera_semseg = self.world.spawn_actor(
            self.bp_camera_semseg,
            self.camera_semseg_spawnpoint,
            attach_to=self.vehicle)
        print_debug("CarlaGame initialize camera_semseg")
        self.actor_list.append(self.camera_semseg)
        print_debug("CarlaGame initialize camera_semseg spawned")

        self.reset_vehicle_position()

    def launch(self):
        print_debug("CarlaGame launch")
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