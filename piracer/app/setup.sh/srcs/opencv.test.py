import cv2

img_adr = "./asset/img/test.jpeg"

img = cv2.imread(img_adr,cv2.IMREAD_COLOR)

cv2.imshow("TEST", img)
cv2.waitKey(0)
cv2.destroyAllWindows