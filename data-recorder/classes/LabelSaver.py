# ------------------------------------------------------
# Import library
from    utils.prints \
        import  *
import  os
import  json

# ------------------------------------------------------
# LabelSaver Class
class   LabelSaver():
    """
    Helper class to save all the lanedata (labels). Each label contains a list 
    of the x values of a lane, their corresponding predefined y-values and 
    their path to the image.
    """
    def __init__(self, h_samples, saving_directory, label_file):
        self.h_samples = h_samples
        self.saving_directory = saving_directory
        self.label_file = label_file

        self.image_name = 0
        
        folder = os.path.dirname(self.label_file)
        if not os.path.isdir(folder):
            os.makedirs(folder)
            
        if os.path.exists(self.label_file):
            os.remove(self.label_file)
        
        self.file = open(self.label_file, 'a')

        print_info("VehicleManager initialize done")
        print_end()
        

    def add_label(self, x_lane_list):
        filestring = {"lanes": x_lane_list,
                      "h_samples": self.h_samples,
                      "raw_file": self.saving_directory + f'{self.image_name:04d}' + '.jpg'}
        
        jsonstring = json.dumps(filestring)
        self.file.write(jsonstring + '\n')
        self.image_name += 1
    
    
    def close_file(self):
        self.file.close()