# ------------------------------------------------------
# Import library
import  os
import  cv2
import  json
import  pygame
import  numpy as np
from    utils.prints \
        import  *

# ------------------------------------------------------
# LabelSaver Class
class   DatasetSaver():
    def __init__(self, town, h_samples, label_dir, label_file, image_dir, img_width, img_height, mask_dir):
        self.town       = town
        self.h_samples  = h_samples
        self.label_dir  = label_dir
        self.label_file = label_file
        self.image_dir  = image_dir
        self.img_width  = img_width
        self.img_height = img_height
        self.mask_dir   = mask_dir
    
        self.index = 0

        folder = os.path.dirname(self.label_file)
        if not os.path.isdir(folder):
            os.makedirs(folder)

        self.label_file = open(self.label_file, 'a')

        print_info("VehicleManager initialize done")
        print_end()

    def save(self, display, x_lanes_list):
        # variables
        lanes_x     = x_lanes_list
        lane_y      = self.h_samples
        file        = f'{self.town}.{self.index:04d}.jpg'
        image       = self.image_dir + file
        mask        = self.mask_dir + file
        mask_src    = np.zeros((self.img_height, self.img_width, 3), dtype=np.uint8)
        
        # file exist checking
        folder      = os.path.dirname(image)
        if not os.path.isdir(folder):
            os.makedirs(folder)
        folder      = os.path.dirname(mask)
        if not os.path.isdir(folder):
            os.makedirs(folder)

        filestring = {
            "lanes_x":      lanes_x,
            "lane_y":       lane_y,
            "image":        image,
            "mask":         mask
        }
        jsonstring = json.dumps(filestring)
        self.label_file.write(jsonstring + '\n')

        # saving image
        pygame.image.save(display, f"{image}")

        # saving mask
        lanes = []
        for i in range(0, len(lanes_x)):
            xs = []
            ys = []
            for j in range(0, len(lane_y)):
                x = lanes_x[i][j]
                y = lane_y[j]
                if x is -2:
                    continue
                xs.append(x)
                ys.append(y)
            if xs and ys:
                lanes.append((xs, ys))
        for lane in lanes:
            xs = lane[0]
            ys = lane[1]
            for i in range(0, len(xs)):
                x = xs[i]
                y = ys[i]
                if i > 0:
                    prev_x, prev_y = xs[i-1], ys[i-1]
                    cv2.line(mask_src, (prev_x, prev_y), (x, y), color=(255, 255, 255), thickness=15)
        cv2.imwrite(mask, mask_src)

        self.index += 1

    def close_file(self):
        self.label_file.close()