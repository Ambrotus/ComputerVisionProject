# import the necessary packages
from easyocr import Reader
import numpy as np
from PIL import ImageGrab

def cleanup_text(text):
	# strip out non-ASCII text so we can draw the text on the image
	# using OpenCV
	return "".join([c if ord(c) < 128 else "" for c in text]).strip()

def startOcr(q):
	outputText = []
	langs =["en"]
	deskimage = ImageGrab.grab()
	image = np.array(deskimage)
	x = 640
	y = 595
	x2= 1290
	y2= 760
	crop_img = image[y:y2, x:x2]
	image = crop_img

	# OCR the input image using EasyOCR
	print("[INFO] OCR'ing input image...")
	#langs = args["langs"].split(",")
	reader = Reader(['en'], gpu = True)
	results = reader.readtext(image)

	# loop over the results
	for (bbox, text, prob) in results:
		# display the OCR'd text and associated probability
		print("[INFO] {:.4f}: {}".format(prob, text))
		# cleanup the text and draw the box surrounding the text along
		# with the OCR'd text itself
		text = cleanup_text(text)
		outputText.append(text+'\n')
	# return outputText
	q.put(outputText)

# startOcr()



