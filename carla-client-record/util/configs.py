class     Configs():
    def __init__(self):
        # ------------------------------------------------------
        # - Carla Variables
        self.WINDOW_WIDTH = 1280
        self.WINDOW_HEIGHT = 720
        self.FPS = 20
        self.FOV = 90.0
        self.CARLA_TOWN = "Town03_Opt"

        self.WORKER_THREADS = 1
        self.CLIENT_TIMEOUT = 30.0
        self.LANE_DETECTION_TIMEOUT = 30.0

        # Save images and labels on disk
        self.isSaving = True
        # Keep own vehicle either in center of road or oscillate between lanemarkings
        self.isCenter = True
        # Draw all lanes in carla simulator
        self.draw3DLanes = False
        # Calculate and draw 3D Lanes on Juction
        self.junctionMode = True
        # Third-person view for the ego vehicle
        self.isThirdPerson = False

        # Number of images stored in a .npy file
        self.number_of_images = 100
        # Total number of .npy files
        self.total_number_of_imagesets = 100
        # Vertical startposition of the lanepoints in the 2D-image
        self.row_anchor_start = 160
        # Number of images after agent is respawned
        self.images_until_respawn = 350
        # Distance between the calculated lanepoints
        self.meters_per_frame = 1.0
        # Total length of a lane_list
        self.number_of_lanepoints = 80
        # Max size of images per folder
        self.max_files_per_classification = 2000

        self.h_samples = []
        for y in range(self.row_anchor_start, self.WINDOW_HEIGHT, 10):
            self.h_samples.append(y)
        # ------------------------------------------------------


        # ------------------------------------------------------
        # - Saver Variables
        # Output for .npy files
        self.output_directory = 'data/rawimages/'
        # Loading directory of .npy files
        self.loading_directory = self.output_directory + self.CARLA_TOWN + '/'
        # Path to the image and label files
        self.saving_directory = 'data/dataset/' + self.CARLA_TOWN + '/'
        self.train_gt = self.saving_directory + 'train_gt_tmp.json'
        self.test_gt = self.saving_directory + 'test_gt.json'
        self.overall_train_gt = self.saving_directory + 'train_gt.json'
        # ------------------------------------------------------