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
from    classes.BufferedImageSaver \
        import  BufferedImageSaver
from    classes.LabelSaver \
        import  LabelSaver


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

# ------------------------------------------------------
# CarlaGame Class
class   CarlaGame(CarlaClient):
    def __init__(self, args, lanes):
        # client, client-timeout, world, and map as args and configs
        super().__init__(args, lanes)
        
        # pygame setting
        pygame.init()
        self.window         = (config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
        self.display        = pygame.display.set_mode(
            self.window, 
            pygame.HWSURFACE | pygame.DOUBLEBUF
        )
        self.font           = get_font()
        self.clock          = pygame.time.Clock()

        # output setting
        self.actor_list     = []
        self.filename       = f"{config.output_directory}/{config.CARLA_TOWN}/"
        
        # manager setting
        self.lane_marker    = LaneMarker(self.lanes)
        self.vehicle_manager= VehicleManager()
        self.image_saver    = BufferedImageSaver(
                                self.filename,
                                config.number_of_images,
                                config.WINDOW_WIDTH,
                                config.WINDOW_HEIGHT,
                                3,  # depth
                                ''  # sensorname
                            )
        self.label_saver    = LabelSaver(
                                config.h_samples, 
                                config.saving_directory,
                                config.train_gt,   
                            )
        self.image_counter  = 0

        # 
        if config.isThirdPerson:
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
        print_info("CarlaGame initialize done")
        print_end()

    def reset_vehicle_position(self):
        """
        Resets the vehicle's position on the map. reset the agent creates 
        a new route of (number_of_lanepoints) waypoints to follow along. 
        """
        self.start_position = random.choice(self.map.get_spawn_points())
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
        
        camera_index = random.randint(0, len(self.camera_transforms)-1)

        self.camera_rgb.set_transform(self.camera_transforms[camera_index])
        self.camera_semseg.set_transform(self.camera_transforms[camera_index])
        print_info("Camera Index:", camera_index)
        print_end()

        if config.draw3DLanes:
            for i, color in enumerate(self.lane_marker.colormap_carla):
                for j in range(0, config.number_of_lanepoints-1):
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

    def render_display(self, image, image_semseg, lanes_list, render_lanes=True):
        """
        Renders the images captured from both cameras and shows it on the
        pygame display

        Args:
            image: numpy array. Shows the 3-channel numpy imagearray on the pygame display.
            image_semseg: numpy array. Shows the semantic segmentation image on the pygame display.
        """
        draw_image(self.display, image)
        #draw_image(self.display, image_semseg, blend=True)

        if render_lanes:
            for i, color in enumerate(self.lane_marker.colormap):
                if lanes_list[i]:
                    for j in range(len(lanes_list[i])):
                        pygame.draw.circle(self.display, self.lane_marker.colormap[color], lanes_list[i][j], 3, 2)
        
        self.display.blit(self.font.render('% 5d FPS ' % self.clock.get_fps(), True, (255, 255, 255)), (8, 10))
        self.display.blit(self.font.render('Dataset % 2d ' % self.image_saver.reset_count, True, (255, 255, 255)), (20, 30))
        self.display.blit(self.font.render('Map: ' + config.CARLA_TOWN, True, (255, 255, 255)), (20, 50))

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
        print(snapshot)
        # Move own vehicle to the next waypoint
        new_waypoint = self.vehicle_manager.move_agent(self.vehicle, self.waypoint_list)
        
        # Move neighbor vehicles with the same speed as the own vehicle
        self.vehicle_manager.move_vehicles(self.waypoint_list)
        
        # Detect if junction is ahead
        self.vehicle_manager.detect_junction(self.waypoint_list)
        
        # Convert and reshape image from Nx1 to shape(720, 1280, 3)
        image_semseg.convert(carla.ColorConverter.CityScapesPalette)
        image_semseg = reshape_image(image_semseg)
        
        # Calculate all the lanes with the helper class 'LaneMarkings'
        lanes_list, x_lanes_list = self.detect_lanemarkings(new_waypoint, image_semseg)
        
        # Draw all 3D lanes in carla simulator
        if config.draw3DLanes:
            for i, color in enumerate(self.lanemarkings.colormap_carla):
                    self.lanemarkings.draw_lanes(self.client, self.lanes[i][-1], self.lanes[i][-2], self.lanemarkings.colormap_carla[color])
        
        # Render the pygame display and show the lanes accordingly
        self.render_display(image_rgb, image_semseg, lanes_list)

        # Save images using buffered imagesaver
        if config.isSaving:
            if (not config.junctionMode and self.vehicle_manager.junctionInSightCounter <= 0) or config.junctionMode:
                self.image_saver.add_image(image_rgb.raw_data, 'CameraRGB')
                self.label_saver.add_label(x_lanes_list)
                self.image_counter += 1
                if(self.image_counter % config.images_until_respawn == 0):
                    self.reset_vehicle_position()

    def stop_saving(self):
        """
        After collecting more than n .npy files, stop saving and close the game window

        Returns True if we collected more than 100 .npy files
        """
        if(self.image_saver.reset_count > config.total_number_of_imagesets - 1):
            print_info("Data collected...")
            return True
        
        return False

    def initialize(self):
        self.blueprint_library = self.world.get_blueprint_library()
        self.start_position = random.choice(self.map.get_spawn_points())
        self.vehicle = self.world.spawn_actor(random.choice(self.blueprint_library.filter("vehicle.ford.mustang")), self.start_position)
        self.actor_list.append(self.vehicle)
        self.vehicle.set_simulate_physics(False)
        self.camera_transform = self.camera_transforms[random.randint(0, len(self.camera_transforms)-1)]

        self.bp_camera_rgb = self.blueprint_library.find("sensor.camera.rgb")
        self.bp_camera_rgb.set_attribute("image_size_x", f"{config.WINDOW_WIDTH}")
        self.bp_camera_rgb.set_attribute("image_size_y", f"{config.WINDOW_HEIGHT}")
        self.bp_camera_rgb.set_attribute("fov",          f"{config.FOV}")
        self.camera_rgb_spawnpoint = self.camera_transform
        self.camera_rgb = self.world.spawn_actor(
            self.bp_camera_rgb,
            self.camera_rgb_spawnpoint,
            attach_to=self.vehicle)
        self.actor_list.append(self.camera_rgb)

        self.bp_camera_semseg = self.blueprint_library.find("sensor.camera.semantic_segmentation")
        self.bp_camera_semseg.set_attribute("image_size_x", f"{config.WINDOW_WIDTH}")
        self.bp_camera_semseg.set_attribute("image_size_y", f"{config.WINDOW_HEIGHT}")
        self.bp_camera_semseg.set_attribute("fov",          f"{config.FOV}")
        self.camera_semseg_spawnpoint = self.camera_transform
        self.camera_semseg = self.world.spawn_actor(
            self.bp_camera_semseg,
            self.camera_semseg_spawnpoint,
            attach_to=self.vehicle)
        self.actor_list.append(self.camera_semseg)

        self.reset_vehicle_position()

        self.vehicle_manager.spawn_vehicles(self.world)

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
                    if should_quit() or self.stop_saving():
                        return
                    self.on_gameloop()
        finally:
            print_info("Saving files...")
            self.image_saver.save()
            self.label_saver.close_file()
            print_end()

            print_info("Destroying actors and cleaning up...")
            for actor in self.actor_list:
                actor.destroy()
            self.vehicle_manager.destroy()
            print_end()

            pygame.quit()
            print_success("Done.")
            print_end()