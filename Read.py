import cv2 

img = cv2.imread('Photos/Chacha.jpeg')
cv2.imshow('Chacha', img)
cv2.waitKey(0)
cv2.destroyAllWindows()