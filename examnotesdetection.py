# -*- coding: utf-8 -*-
"""ExamNotesDetection.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Td4K--BkhGoPSByhsVPJwA5f-COczCLR

LeNet Model
"""

from keras.models import Sequential
from keras.layers.convolutional import Conv2D
from keras.layers.convolutional import MaxPooling2D
from keras.layers.core import Activation
from keras.layers.core import Flatten
from keras.layers.core import Dense
from keras import backend as K

class LeNet:
    @staticmethod
    def build(widht,height,depth,classes):
        model = Sequential()
        inputShape = (height,widht,depth)
        
        if K.image_data_format() == 'channels_first':
            inputShape = (depth,height,widht)
            
        model.add(Conv2D(20,(5,5), padding='SAME' ,input_shape=inputShape))
        model.add(Activation('relu'))
        model.add(MaxPooling2D(pool_size=(2,2), strides=(2,2)))
        
        model.add(Conv2D(50,(5,5), padding='SAME'))
        model.add(Activation('relu'))
        model.add(MaxPooling2D(pool_size=(2,2), strides=(2,2)))
        
        model.add(Flatten())
        model.add(Dense(500))
        model.add(Activation('relu'))
        
        model.add(Dense(classes))
        model.add(Activation('softmax'))
        
        return model

import matplotlib
matplotlib.use('Agg')

from keras.preprocessing.image import ImageDataGenerator
from keras.optimizers import Adam
from sklearn.model_selection import train_test_split
from keras.preprocessing.image import img_to_array
from tensorflow.keras.utils import to_categorical
from imutils import paths
import matplotlib.pyplot as plt 
import numpy as np 
import argparse
import random
import cv2
import os

EPOCHS = 100
INIT_LR = 1e-3
BS = 32

#initialize the data and labels
print("[INFO] Loading images....")
data = []
labels = []
imagePaths = []

# Commented out IPython magic to ensure Python compatibility.
# %cd

#image paths and shuffle them
notes = '/DataExam/notes'
not_notes = '/DataExam/not_notes'
for filename in os.listdir(notes):
		img = os.path.join(notes,filename)
		imagePaths.append(img)

for filename in os.listdir(not_notes):
		img = os.path.join(not_notes,filename)
		imagePaths.append(img)

random.seed(42)
random.shuffle(imagePaths)		

for imagePath in imagePaths:

	image = cv2.imread(imagePath)
	image = cv2.resize(image,(28,28))
	image = img_to_array(image)
	data.append(image)


	label = imagePath.split(os.path.sep)[-2]
	label = 1 if label == 'notes' else 0
	labels.append(label)

#scale image in range [0,1]
data = np.array(data,dtype='float')/255.0
labels = np.array(labels)
(trainX,testX,trainY,testY) = train_test_split(data,labels,test_size=0.25,random_state=42)

#convert labels from int to vector
trainY = to_categorical(trainY,num_classes=2)
testY = to_categorical(testY,num_classes=2)

"""#data augmentation"""

# construct the image generator for data augmentation
aug = ImageDataGenerator(rotation_range=30, width_shift_range=0.1,
	height_shift_range=0.1, shear_range=0.2, zoom_range=0.2,
	horizontal_flip=True, fill_mode="nearest")

#initialize the model
print("[INFO] compiling model...")
model = LeNet.build(widht=28,height=28,depth=3,classes=2)
opt = Adam(lr=INIT_LR, decay = INIT_LR/EPOCHS)
model.compile(loss='binary_crossentropy', optimizer=opt, metrics=['accuracy'])

#train the network
print('[INFO] training network...')
H = model.fit_generator(aug.flow(trainX,trainY,batch_size=BS),
	validation_data=(testX,testY), steps_per_epoch=len(trainX)//BS,
	epochs=EPOCHS, verbose=1)

print('[INFO] serializing network...')
model.save('mymodel.h5')

plt.style.use("ggplot")
plt.figure()
N = EPOCHS
plt.plot(np.arange(0,N), H.history['loss'], label = 'train_loss')
plt.plot(np.arange(0,N), H.history['val_loss'], label = 'val_loss')
plt.plot(np.arange(0,N), H.history['acc'], label = 'train_acc')
plt.plot(np.arange(0,N), H.history['val_acc'], label = 'val_acc')
plt.title("Training loss and accuracy on Notes/Not Notes")
plt.xlabel("Epoch#")
plt.ylabel("Loss/Accuracy")
plt.legend(loc='lower left')

from keras.preprocessing.image import img_to_array
from keras.models import load_model
import numpy as np 
import argparse
import imutils
import cv2
import os

ap = argparse.ArgumentParser()

# ap.add_argument("-i", "--image", required=True,
#	help="path to input image")
#args = vars(ap.parse_args())

#image = cv2.imread(args['image'])
examples = '/DataExam/examples'
image = []

for img in os.listdir(examples):
	img = os.path.join(examples,img)
	image = cv2.imread(img)
	# orig = image.copy()
	image = cv2.resize(image,(28,28))
	image = image.astype('float')/255.0	
	image = img_to_array(image)
	image = np.expand_dims(image, axis=0)
	model = load_model('mymodel.h5')
	(not_notes, notes) = model.predict(image)[0]
	label = 'notes' if notes > not_notes else "not_notes"
	proba = notes if notes > not_notes else not_notes
	label = "{}: {:.2f}%".format(label,proba*100)
	if(notes > not_notes):
		os.remove(img)


# output = imutils.resize(orig,width=400)
# cv2.putText(output,label,(10,25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

# cv2.imshow("Output", output)
# cv2.waitKey(0)