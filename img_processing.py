import cv2
import numpy as np

def generate_light_intensity_map(input_image_path, output_image_path):
    image = cv2.imread(input_image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    normalized = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX)
    print(f"normalized: {len(normalized)}")
    colormap = np.zeros((256, 1, 3), dtype=np.uint8)
    print(f"colormap: {len(colormap)}")
    min = 70
    for i in range(256):
        if i < 15:
            colormap[i, 0, 0] = 30
            colormap[i, 0, 1] = 0    
            colormap[i, 0, 2] = 0
        elif i < min:
            colormap[i, 0, 0] = 255 - i 
            colormap[i, 0, 1] = 0      
            colormap[i, 0, 2] = 0
        elif i < 150:
            colormap[i, 0, 0] = 0        
            colormap[i, 0, 1] = 255     
            colormap[i, 0, 2] = i - min  
        elif i < 205:
            colormap[i, 0, 0] = 0        
            colormap[i, 0, 1] = 255 - (i - 150) 
            colormap[i, 0, 2] = 255     
        else:
            colormap[i, 0, 0] = 0       
            colormap[i, 0, 1] = 0      
            colormap[i, 0, 2] = 255
    color_mapped_image = cv2.applyColorMap(normalized, cv2.COLORMAP_JET) 

    for i in range(256):
        mask = normalized == i
        color_mapped_image[mask] = colormap[i, 0]

    cv2.imwrite(output_image_path, color_mapped_image)
    return color_mapped_image
def display(img):
    cv2.imshow("Light Intensity Map", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

input = "./LP-images/img.jpeg"
output = "./LP-images/output.jpeg"
#display(generate_light_intensity_map(input, output))
generate_light_intensity_map(input, output)

