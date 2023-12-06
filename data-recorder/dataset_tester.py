import  cv2
import  numpy as np
import  matplotlib.pyplot as plt
from    scipy.interpolate import interp1d

def draw_lanes_on_image(dataset):
    image_path  = dataset["image_name"]
    lanes_x     = dataset["lanes_x"]
    lane_y      = dataset["lane_y"]

    image_org   = cv2.imread(image_path)
    image_new   = np.zeros((720, 1280, 3), dtype=np.uint8)

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
                cv2.line(image_org, (prev_x, prev_y), (x, y), color=(0, 0, 0), thickness=5)
                cv2.line(image_new, (prev_x, prev_y), (x, y), color=(255, 255, 255), thickness=5)

    cv2.imshow('Lanes', image_org)
    cv2.waitKey(0)
    cv2.imshow('Lanes', image_new)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    cv2.imwrite('lanepoints_on_original_image.jpg', image_org)
    cv2.imwrite('lanepoints_on_black_paint.jpg', image_new)

# main
dataset = {"lanes_x": [[-2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, 391, 429, 441, 446, 447, 446, 443, 439, 435, 430, 425, 419, 413, 406, 399, 392, 384, 376, 369, 361, 354, 345, 337, 328, 320, 311, 303, 295, 286, 277, 268, 259, 250, 241, 232, 223, 214, 206, 197, 188, 179, 170, 161, 152, 143], [-2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, 502, 557, 586, 608, 626, 642, 655, 668, 679, 689, 699, 709, 717, 726, 735, 743, 751, 759, 767, 775, 782, 789, 796, 803, 810, 818, 825, 831, 838, 845, 851, 858, 865, 871, 878, 885, 891, 898, 905, 912, 918, 925, 932, 938, 945], [-2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, 293, 285, 271, 255, 237, 218, 199, 178, 158, 138, 117, 95, 73, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2], [-2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2, -2]], "lane_y": [160, 170, 180, 190, 200, 210, 220, 230, 240, 250, 260, 270, 280, 290, 300, 310, 320, 330, 340, 350, 360, 370, 380, 390, 400, 410, 420, 430, 440, 450, 460, 470, 480, 490, 500, 510, 520, 530, 540, 550, 560, 570, 580, 590, 600, 610, 620, 630, 640, 650, 660, 670, 680, 690, 700, 710], "image_name": "../data/images/Town07_Opt/0021.jpg"}

draw_lanes_on_image(dataset)
