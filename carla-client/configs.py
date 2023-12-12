import  os
import  sys
import  glob

# ------------------------------------------------------
# - Carla Variables
CARLA_FOLDER_DIR    = "./carla-api/"
CARLA_EGG_FILE      = "dist/carla-*%d.%d-%s.egg"
CARLA_DIR           = CARLA_FOLDER_DIR + CARLA_EGG_FILE
CARLA_DIR           = glob.glob("../carla/dist/carla-*%d.%d-%s.egg" % (
                            sys.version_info.major,
                            sys.version_info.minor,
                        "win-amd64" if os.name == "nt" else "linux-x86_64"))[0]

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FPS = 20
FOV = 90.0
CARLA_TOWN = "Town15"

WORKER_THREADS = 1
CLIENT_TIMEOUT = 50.0
LANE_DETECTION_TIMEOUT = 30.0
NEIGHTBOR_VEHICLES_MODE = False

debugMode = False
noRendering = True
isSaving = True
isCenter = True
junctionMode = False
draw3DLanes = True

# Vertical startposition of the lanepoints in the 2D-image
row_anchor_start = 160
# Number of images after agent is respawned
images_until_respawn = 350
# Distance between the calculated lanepoints
meters_per_frame = 1.0
# Total length of a lane_list
number_of_lanepoints = 80

h_samples = []
for y in range(row_anchor_start, WINDOW_HEIGHT, 10):
    h_samples.append(y)
# ------------------------------------------------------


# ------------------------------------------------------
# - Saver Variables
dataset_directory = '../../dataset/datasetv2/testset/'
image_directory = dataset_directory + 'images/'
label_directory = dataset_directory + 'labels/'
masks_directory = dataset_directory + 'masks/'
train_gt = label_directory + 'train_gt_tmp.json'
test_gt = label_directory + 'test_gt.json'
overall_train_gt = label_directory + 'train_gt.json'
# ------------------------------------------------------