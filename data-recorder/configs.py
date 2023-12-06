# ------------------------------------------------------
# - Carla Variables
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FPS = 20
FOV = 90.0
CARLA_TOWN = "Town02_Opt"

WORKER_THREADS = 1
CLIENT_TIMEOUT = 40.0
LANE_DETECTION_TIMEOUT = 30.0
NEIGHTBOR_VEHICLES_MODE = False

# Save images and labels on disk
isSaving = True
# Keep own vehicle either in center of road or oscillate between lanemarkings
isCenter = True
# Calculate and draw 3D Lanes on Juction
junctionMode = False

# Number of images stored in a .npy file
number_of_images = 100
# Total number of .npy files
total_number_of_imagesets = 100
# Vertical startposition of the lanepoints in the 2D-image
row_anchor_start = 160
# Number of images after agent is respawned
images_until_respawn = 350
# Distance between the calculated lanepoints
meters_per_frame = 1.0
# Total length of a lane_list
number_of_lanepoints = 80
# Max size of images per folder
max_files_per_classification = 2000

h_samples = []
for y in range(row_anchor_start, WINDOW_HEIGHT, 10):
    h_samples.append(y)
# ------------------------------------------------------


# ------------------------------------------------------
# - Saver Variables
# Output for image files
image_directory = 'data/images/' + CARLA_TOWN + '/'
# Path to the image and label files
label_directory = 'data/dataset/' + CARLA_TOWN + '/'
train_gt = label_directory + 'train_gt_tmp.json'
test_gt = label_directory + 'test_gt.json'
overall_train_gt = label_directory + 'train_gt.json'
# ------------------------------------------------------