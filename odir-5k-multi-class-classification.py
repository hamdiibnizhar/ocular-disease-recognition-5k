# -*- coding: utf-8 -*-
"""ODIR-5K-Multi-Class-Classification.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1NKl-fvzb2_mAGDQO2TLvpNRa3mMcYnFe
"""

#upload kaggle.json and tensorflow_addons wheel
from google.colab import files
files.upload()

# ! pip install kaggle
# ! sudo python3 -m pip install tfa-nightly
! sudo python3 -m pip install /content/tensorflow_addons-0.11.0.dev0-cp36-cp36m-linux_x86_64.whl

from google.colab import drive
drive.mount('/content/gdrive')

! mkdir ~/.kaggle
! cp kaggle.json ~/.kaggle/
! chmod 600 ~/.kaggle/kaggle.json

import zipfile

! kaggle datasets download -d 'andrewmvd/ocular-disease-recognition-odir5k' -p '/tmp'

local_zip = '/tmp/ocular-disease-recognition-odir5k.zip'
zip_ref = zipfile.ZipFile(local_zip, 'r')
zip_ref.extractall('/tmp')
zip_ref.close()

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import sklearn

import tensorflow as tf
import tensorflow_addons as tfa
import keras_preprocessing
from keras_preprocessing import image
from keras_preprocessing.image import ImageDataGenerator
import tensorflow.keras.optimizers

import os
import shutil
from random import sample

print(tf.__version__)

os.chdir('/tmp/ODIR-5K')

from pandas import read_excel

my_sheet = 'Sheet1'
file_name = '/tmp/ODIR-5K/data.xlsx'
df = read_excel(file_name, sheet_name = my_sheet)
print(df.head())

leftEyeKeywords = df['Left-Diagnostic Keywords'].copy()
rightEyeKeywords = df['Right-Diagnostic Keywords'].copy()

leftEyeKeywords = leftEyeKeywords.str.split("，")
rightEyeKeywords = rightEyeKeywords.str.split("，")

leftEyeKeywords[2]

from sklearn.preprocessing import MultiLabelBinarizer

mlb = MultiLabelBinarizer()

res = pd.DataFrame(mlb.fit_transform(rightEyeKeywords),
                   columns=mlb.classes_,
                   index=rightEyeKeywords.index)

allDiagnosisLeft = res.columns.to_list()
len(allDiagnosisLeft)

res = pd.DataFrame(mlb.fit_transform(leftEyeKeywords),
                   columns=mlb.classes_,
                   index=leftEyeKeywords.index)

allDiagnosisRight = res.columns.to_list()
len(allDiagnosisRight)

allDiagnosis=list(set(allDiagnosisLeft+allDiagnosisRight))
print("total different keys diagnosis :", len(allDiagnosis))

test_df = df.copy()
doubleDiagnosisRow = []

def getKeyDiagnosisSingle(colName):
  keyDiagnosis = []
  global doubleDiagnosisRow
  store = True
  for row in range(len(test_df[colName])):
    store = True
    if test_df[colName][row] == 1:
      for lable in test_df.columns[7:]:
        if lable == colName:
          continue
        if test_df[lable][row] == 1:
          doubleDiagnosisRow.append(row)
          store = False
          break
        
      if store == True:
        for i in rightEyeKeywords[row]:
          keyDiagnosis.append(i)
        for i in leftEyeKeywords[row]:
          keyDiagnosis.append(i)
      

  keyDiagnosis = list(set(keyDiagnosis))
  return keyDiagnosis

keyNormal = getKeyDiagnosisSingle(test_df.columns[7])
keyDiabetes = getKeyDiagnosisSingle(test_df.columns[8])
keyGlaucoma = getKeyDiagnosisSingle(test_df.columns[9])
keyCataract = getKeyDiagnosisSingle(test_df.columns[10])
keyAMD = getKeyDiagnosisSingle(test_df.columns[11])
keyHypertension = getKeyDiagnosisSingle(test_df.columns[12])
keyMyopia = getKeyDiagnosisSingle(test_df.columns[13])
keyOtherDisease = getKeyDiagnosisSingle(test_df.columns[14])

labelString = ['Normal', 'Diabetes', 'Glaucoma', 'Cataract', 'AMD', 'Hypertension', 'Myopia', 'Abnormalities']
keyAll = [keyNormal, keyDiabetes, keyGlaucoma, keyCataract, keyAMD, keyHypertension, keyMyopia, keyOtherDisease]

for i in range(8):
  print(labelString[i], len(keyAll[i]))

keyNormal

print("intersect by normal :\n")
for i in range(1,len(keyAll)):
  keyAll[i] = list(set(keyAll[i])-set(keyAll[0]))

for i in range(8):
  print(labelString[i], len(keyAll[i]))

print("\nintersect by other :\n")
for i in range(len(keyAll)):
  for j in range(i,len(keyAll)):
    if i == j:
      continue
    else :
      keyAll[i] = list(set(keyAll[i])-set(keyAll[j]))

for i in range(8):
  print(labelString[i], len(keyAll[i]))

def getAllRecognizedKey(mkeyAll):
  mallkeyDiagnosis = []
  for i in range(len(mkeyAll)):
    mkeyAll[i] = list(set(mkeyAll[i]))
    mallkeyDiagnosis = mallkeyDiagnosis+list(set(mkeyAll[i]))
  return mallkeyDiagnosis

keyNormal, keyDiabetes, keyGlaucoma, keyCataract, keyAMD, keyHypertension, keyMyopia, keyOtherDisease = keyAll[0], keyAll[1], keyAll[2], keyAll[3], keyAll[4], keyAll[5], keyAll[6], keyAll[7]

allkeyDiagnosis = getAllRecognizedKey(keyAll)
len(allkeyDiagnosis)

doubleDiagnosisRow = list(set(doubleDiagnosisRow))
print("double lablel row ",len(doubleDiagnosisRow))
doubleDiagnosisRow.sort()
# doubleDiagnosisRow

notlisted = []
listed = False
for row in doubleDiagnosisRow:
  # print(row)
  for ilist in leftEyeKeywords[row]:
    # print(ilist)
    listed = False
    for j in keyAll:
      if ilist in j:
        listed = True
        break
    if listed == False:
      notlisted.append(ilist)

for row in doubleDiagnosisRow:
  for ilist in rightEyeKeywords[row]:
    listed = False
    for j in keyAll:
      if ilist in j:
        listed = True
        break
    if listed == False:
      notlisted.append(ilist)

notlisted = list(set(notlisted))
# notlisted
print("not listed diagnosis key :",len(notlisted))

def intersectFromMultiLabel(mkeyAll):
  mnotRecognizedList = []
  mallkeyDiagnosis = []
  for i in range(len(mkeyAll)):
    mkeyAll[i] = list(set(mkeyAll[i]))
    mallkeyDiagnosis = mallkeyDiagnosis+list(set(mkeyAll[i])) 
  for row in doubleDiagnosisRow:
    notlistedList = []
    listedList = []
    colIndex = []
    ind = []
    tempList = []
    for ilist in leftEyeKeywords[row]:
      if ilist not in mallkeyDiagnosis:
        tempList.append(ilist)
    for ilist in rightEyeKeywords[row]:
      if ilist not in mallkeyDiagnosis:
        tempList.append(ilist)

    for i in range(7, len(test_df.columns)):
      if test_df[test_df.columns[i]][row] == 1:
        colIndex.append(i-7)
    tempList = list(set(tempList))
    isContainAbnormal = 7 in colIndex
    if len(tempList) > 0:
      ind = colIndex
      for ilist in leftEyeKeywords[row]:
        if ilist not in tempList:
          listedList.append(ilist)
      for ilist in rightEyeKeywords[row]:
        if ilist not in tempList:
          listedList.append(ilist)
      
      for ilist in listedList:
        for i in colIndex:    
          if ilist in keyNormal:
            continue
          if ilist in mkeyAll[i]:
            ind.remove(i)

      if len(ind) == 0 and isContainAbnormal:
        ind.append(7)
      if len(ind) == 1 and len(tempList) == 1:
        mkeyAll[ind[0]] = mkeyAll[ind[0]] + tempList
        mkeyAll[ind[0]] = list(set(mkeyAll[ind[0]]))
      else:
        print("not recognize")
        mnotRecognizedList.append(tempList[0])
        mnotRecognizedList = list(set(mnotRecognizedList))

    mallkeyDiagnosis = []
    for i in mkeyAll:
      mallkeyDiagnosis = mallkeyDiagnosis+list(set(i))
  return mkeyAll, mnotRecognizedList

itterate = True
notRecognizedList = []
while itterate :
  temp_allkeyDiagnosis = allkeyDiagnosis.copy()
  keyAll, notRecognizedList = intersectFromMultiLabel(keyAll)
  allkeyDiagnosis = getAllRecognizedKey(keyAll)
  # print(len(temp_allkeyDiagnosis), len(allkeyDiagnosis))
  print(notRecognizedList)
  if len(temp_allkeyDiagnosis) == len(allkeyDiagnosis):
    print(True)
    itterate = False

allkeyDiagnosis = getAllRecognizedKey(keyAll)

keyNormal, keyDiabetes, keyGlaucoma, keyCataract, keyAMD, keyHypertension, keyMyopia, keyOtherDisease = keyAll[0], keyAll[1], keyAll[2], keyAll[3], keyAll[4], keyAll[5], keyAll[6], keyAll[7]

for i in range(8):
  print(labelString[i], len(keyAll[i]))

print("\nall regnized key :",len(allkeyDiagnosis))
print("\nnot recognized key : ", list(set(allDiagnosis)-set(allkeyDiagnosis)))

#manual listed key
string = 'suspected cataract'
if string in notRecognizedList and string not in allkeyDiagnosis:
  keyAll[3].append(string)
  notRecognizedList.remove(string)

keyAll[3]

allkeyDiagnosis = getAllRecognizedKey(keyAll)

keyNormal, keyDiabetes, keyGlaucoma, keyCataract, keyAMD, keyHypertension, keyMyopia, keyOtherDisease = keyAll[0], keyAll[1], keyAll[2], keyAll[3], keyAll[4], keyAll[5], keyAll[6], keyAll[7]

for i in range(len(keyAll)):
  print(labelString[i], len(keyAll[i]))

print("\nall regnized key :",len(allkeyDiagnosis))
print("\nnot recognized key : ", list(set(allDiagnosis)-set(allkeyDiagnosis)))

string = 'central serous chorioretinopathy'

for i in notRecognizedList:
  if i not in allkeyDiagnosis:
    print("not in : ", i)

string in keyOtherDisease

train_dir = 'training'
validation_dir = 'validation'
test_dir = 'testing'

training_source_path = '/tmp/ODIR-5K/Training Images/'
testing_source_path = '/tmp/ODIR-5K/Testing Images/'

training_path = '/tmp/ODIR-5K/training/'
validation_path = '/tmp/ODIR-5K/validation/'
testing_path = '/tmp/ODIR-5K/testing/'

if os.path.exists(training_path) or os.path.exists(validation_path) or os.path.exists(testing_path):
  shutil.rmtree(training_path)
  shutil.rmtree(validation_path)
  shutil.rmtree(testing_path)

os.mkdir(train_dir)
os.mkdir(validation_dir)
os.mkdir(test_dir)

for i in labelString:
  os.mkdir(train_dir+'/'+i)
  os.mkdir(validation_dir+'/'+i)
  # os.mkdir(test_dir+'/'+i)

testing_source_files = os.listdir(testing_source_path)
print(len(testing_source_files))
training_source_files = os.listdir(training_source_path)
print(len(training_source_files))

# training_files = training_source_files

fraction = 0.1

nvalidation = int(len(training_source_files)*fraction)
ntraining = len(training_source_files)-nvalidation

validation_files = sample(training_source_files, nvalidation)
training_files = sample(training_source_files, ntraining)
testing_files = testing_source_files
print(len(training_files))
print(len(validation_files))
print(len(testing_files))
# validation_file = testing_source_files


# print(len(validation_files))
# validation_files

temp_df = df['Left-Fundus']
len(temp_df)
temp_df[12]
temp_df = df['Right-Fundus']
rightEyeKeywords[5]
testing_files[1]

temp_keywords = rightEyeKeywords
temp_keywords[12]

notSortedFiles = []
"using continue because there are files have more than one diagnosis keys"
for fileName in training_files:
  nrow = None
  if 'left' in fileName:
    temp_df = df['Left-Fundus']
    temp_keywords = leftEyeKeywords
  elif 'right' in fileName:
    temp_df = df['Right-Fundus']
    temp_keywords = rightEyeKeywords

  for row in range(len(temp_df)):
    if fileName == temp_df[row]:
      nrow = row
      break

  if nrow == None:
    # print("file not listed in data")
    shutil.copyfile(training_source_path+fileName, training_path+fileName)
    continue

  for i in temp_keywords[nrow]:
    if i in keyNormal:
      shutil.copyfile(training_source_path+fileName, training_path+'Normal/'+fileName)
      continue
    if i in keyDiabetes:
      shutil.copyfile(training_source_path+fileName, training_path+'Diabetes/'+fileName)
      continue
    if i in keyGlaucoma:
      shutil.copyfile(training_source_path+fileName, training_path+'Glaucoma/'+fileName)
      continue
    if i in keyCataract:
      shutil.copyfile(training_source_path+fileName, training_path+'Cataract/'+fileName)
      continue
    if i in keyAMD:
      shutil.copyfile(training_source_path+fileName, training_path+'AMD/'+fileName)
      continue
    if i in keyHypertension:
      shutil.copyfile(training_source_path+fileName, training_path+'Hypertension/'+fileName)
      continue
    if i in keyMyopia:
      shutil.copyfile(training_source_path+fileName, training_path+'Myopia/'+fileName)
      continue
    if i in keyOtherDisease:
      shutil.copyfile(training_source_path+fileName, training_path+'Abnormalities/'+fileName)
      continue
    # else:
    print("not in list key : ", "| row : ", row, "| file name : ", fileName, "| key diagnosis : ", i)
    notSortedFiles.append(fileName)
    notSortedFiles=list(set(notSortedFiles))
    # break
    
print(len(os.listdir(training_path+'AMD')))
print(len(os.listdir(training_path+'Abnormalities')))
print(len(os.listdir(training_path+'Normal')))
print(len(os.listdir(training_path+'Cataract')))

for fileName in validation_files:
  nrow = None
  if 'left' in fileName:
    temp_df = df['Left-Fundus']
    temp_keywords = leftEyeKeywords
  elif 'right' in fileName:
    temp_df = df['Right-Fundus']
    temp_keywords = rightEyeKeywords

  for row in range(len(temp_df)):
    if fileName == temp_df[row]:
      nrow = row
      break

  if nrow == None:
    # print("file not listed in data")
    shutil.copyfile(training_source_path+fileName, validation_path+fileName)
    continue

  for i in temp_keywords[nrow]:
    if i in keyNormal:
      shutil.copyfile(training_source_path+fileName, validation_path+'Normal/'+fileName)
      continue
    if i in keyDiabetes:
      shutil.copyfile(training_source_path+fileName, validation_path+'Diabetes/'+fileName)
      continue
    if i in keyGlaucoma:
      shutil.copyfile(training_source_path+fileName, validation_path+'Glaucoma/'+fileName)
      continue
    if i in keyCataract:
      shutil.copyfile(training_source_path+fileName, validation_path+'Cataract/'+fileName)
      continue
    if i in keyAMD:
      shutil.copyfile(training_source_path+fileName, validation_path+'AMD/'+fileName)
      continue
    if i in keyHypertension:
      shutil.copyfile(training_source_path+fileName, validation_path+'Hypertension/'+fileName)
      continue
    if i in keyMyopia:
      shutil.copyfile(training_source_path+fileName, validation_path+'Myopia/'+fileName)
      continue
    if i in keyOtherDisease:
      shutil.copyfile(training_source_path+fileName, validation_path+'Abnormalities/'+fileName)
      continue
    # break
    print("not in list key : ", "| row : ", row, "| file name : ", fileName, "| key diagnosis : ", i)
    notSortedFiles.append(fileName)
    notSortedFiles=list(set(notSortedFiles))

print(len(os.listdir(validation_path+'AMD')))
print(len(os.listdir(validation_path+'Abnormalities')))
print(len(os.listdir(validation_path+'Normal')))
print(len(os.listdir(validation_path+'Cataract')))

for fileName in testing_files:
  nrow = None
  if 'left' in fileName:
    temp_df = df['Left-Fundus']
    temp_keywords = leftEyeKeywords
  if 'right' in fileName:
    temp_df = df['Right-Fundus']
    temp_keywords = rightEyeKeywords

  for row in range(len(temp_df)):
    if fileName == temp_df[row]:
      nrow = row
      break

  if nrow == None:
    # print("file not listed in data")
    shutil.copyfile(testing_source_path+fileName, testing_path+fileName)
    continue

  for i in temp_keywords[nrow]:
    if i in keyNormal:
      shutil.copyfile(testing_source_path+fileName, testing_path+'Normal/'+fileName)
      continue
    if i in keyDiabetes:
      shutil.copyfile(testing_source_path+fileName, testing_path+'Diabetes/'+fileName)
      continue
    if i in keyGlaucoma:
      shutil.copyfile(testing_source_path+fileName, testing_path+'Glaucoma/'+fileName)
      continue
    if i in keyCataract:
      shutil.copyfile(testing_source_path+fileName, testing_path+'Cataract/'+fileName)
      continue
    if i in keyAMD:
      shutil.copyfile(testing_source_path+fileName, testing_path+'AMD/'+fileName)
      continue
    if i in keyHypertension:
      shutil.copyfile(testing_source_path+fileName, testing_path+'Hypertension/'+fileName)
      continue
    if i in keyMyopia:
      shutil.copyfile(testing_source_path+fileName, testing_path+'Myopia/'+fileName)
      continue
    if i in keyOtherDisease:
      shutil.copyfile(testing_source_path+fileName, testing_path+'Abnormalities/'+fileName)
      continue
    print("not in list key : ", "| row : ", row, "| file name : ", fileName, "| key diagnosis : ", i)
    notSortedFiles.append(fileName)
    notSortedFiles=list(set(notSortedFiles))

# print(len(os.listdir(testing_path+'AMD')))
# print(len(os.listdir(testing_path+'Abnormalities')))
# print(len(os.listdir(testing_path+'Normal')))
# print(len(os.listdir(testing_path+'Cataract')))
print(len(os.listdir(testing_path)))

notSortedFiles

dirList = os.listdir(training_path)
countx = 0
for i in dirList:
  countx+=len(os.listdir(training_path+i))

print(countx)

len(os.listdir(training_source_path))

from PIL import Image

cataractImageList = os.listdir(training_path+'Cataract')
imagePath = training_path+'Cataract/'+cataractImageList[2]
im = Image.open(imagePath)
width, height = im.size
print(width, height, "from", imagePath)

img = image.load_img(imagePath)
plt.imshow(img)
img = image.load_img(imagePath, target_size=(int(height/16),int(width/16)), interpolation="lanczos")
plt.imshow(img)

# target_size = (int(height/16),int(width/16))
target_size = (200, 300)
# mode = 'grayscale'
color_mode = 'rgb'
if color_mode == 'grayscale':
  shapeadd = (1,)
if color_mode == 'rgb':
  shapeadd = (3,)

train_datagen = ImageDataGenerator(
                                  rescale = 1./255,
                                  zoom_range=0.2,
                                  rotation_range=40,
                                  # horizontal_flip=True,
                                  # width_shift_range=0.2,
                                  # height_shift_range=0.2,
                                  # shear_range=0.2,                                  
                                  fill_mode='nearest',
                                   
                                  # featurewise_center=False,  # set input mean to 0 over the dataset
                                  # samplewise_center=False,  # set each sample mean to 0
                                  # featurewise_std_normalization=False,  # divide inputs by std of the dataset
                                  # samplewise_std_normalization=False,  # divide each input by its std
                                  # zca_whitening=False,  # apply ZCA whitening
                                  # vertical_flip=False
                                  )

validation_datagen = ImageDataGenerator(
                                        rescale = 1./255,
                                        )

train_generator = train_datagen.flow_from_directory(
	training_path,
	target_size=target_size,
  # interpolation="lanczos",
  # batch_size=80,
	class_mode='categorical',
  color_mode=color_mode,
)

validation_generator = validation_datagen.flow_from_directory(
	validation_path,
	target_size=target_size,
  # interpolation="lanczos",
  # batch_size=25,
	class_mode='categorical',  
  color_mode=color_mode,
)

nEpoch = 25
input_shape = target_size + shapeadd
learning_rate = 0.0001
optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate)
# tf.keras.optimizers.SGD(learning_rate=learning_rate)

AUC_value = tf.keras.metrics.AUC(
                                  # name='AUC values',
                                  num_thresholds=200, 
                                  curve='ROC', 
                                  summation_method='interpolation',
                                  # threshold=0.5, 
                                  multi_label=True,
                                  )

kappa_score = tfa.metrics.CohenKappa(
                                      num_classes=8,
                                      name='kappa score',
                                      # sparse_labels=False,
                                      # regression=False,
                                      # weightage='quadratic',
                                      # dtype=np.int32,
                                    )

F1_score = tfa.metrics.F1Score(
                                num_classes=8,
                                name='F-1 score',
                                # average='macro',
                                # threshold=0.5,
                              )

model_path = '/content/gdrive/My Drive/Trained_Models/ODIR5K-bottleneck/'
checkpoint_path = model_path+'ODIR5K.ckpt'
checkpoint_dir = os.path.dirname(checkpoint_path)

model_save_weights = 'weight'
model_save_name_h5 = 'ODIR5K.h5'
model_save_name_tf = 'ODIR5K_TF'

use_training_model = True

if (os.path.isfile(model_path+model_save_name_h5) or os.path.exists(model_path+model_save_name_tf)) and use_training_model:
  # if os.path.exists(model_path+model_save_name_tf):
  #   print("using tf")
  #   model = tf.keras.models.load_model(model_path+model_save_name_tf)
  if os.path.isfile(model_path+model_save_name_h5):
    print("using h5")
    model = tf.keras.models.load_model(model_path+model_save_name_h5)
  # model.summary()
  output = model.output
else:
  print("no using saved model")
  model = tf.keras.models.Sequential([
      # The first convolution
      tf.keras.layers.Conv2D(32, (3,3), activation='relu', input_shape=input_shape),
      tf.keras.layers.Conv2D(32, (3,3), activation='relu'),
      tf.keras.layers.MaxPooling2D(2, 2),
      tf.keras.layers.BatchNormalization(),
      # The second convolution
      tf.keras.layers.Conv2D(64, (3,3), activation='relu'),
      tf.keras.layers.Conv2D(64, (3,3), activation='relu'),
      tf.keras.layers.MaxPooling2D(2,2),
      tf.keras.layers.BatchNormalization(),
      # The third convolution
      tf.keras.layers.Conv2D(128, (3,3), activation='relu'),
      tf.keras.layers.Conv2D(128, (3,3), activation='relu'),
      tf.keras.layers.MaxPooling2D(2,2),
      tf.keras.layers.BatchNormalization(),
      # The fourth convolution
      tf.keras.layers.Conv2D(256, (3,3), activation='relu'),
      tf.keras.layers.Conv2D(256, (3,3), activation='relu'),
      tf.keras.layers.MaxPooling2D(2,2),
      tf.keras.layers.BatchNormalization(),

      tf.keras.layers.Flatten(),
      tf.keras.layers.Dense(256, activation='relu'),
      tf.keras.layers.Dense(64, activation='relu'),
      tf.keras.layers.BatchNormalization(),
      # tf.keras.layers.Dropout(0.2),
      tf.keras.layers.Dense(8, activation='softmax')
  ])
  # model.compile(loss = 'categorical_crossentropy', optimizer=optimizer, metrics=['accuracy'])

model.summary()
model.compile(loss='categorical_crossentropy', 
              optimizer=optimizer, 
              metrics=[
                       'accuracy', 
                       kappa_score, 
                       F1_score, 
                       AUC_value,
                       ]
              )

checkpoint_path = "/content/gdrive/My Drive/Trained_Models/ODIR5K/ODIR5K.ckpt"
checkpoint_dir = os.path.dirname(checkpoint_path)

cp_callback = tf.keras.callbacks.ModelCheckpoint(filepath=checkpoint_path,
                                                #  save_weights_only=True,
                                                 verbose=1)

stopAccuracy = 0.900

# Define a Callback class that stops training once accuracy reaches the certain accuracy
class callbackStop(tf.keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs={}):
    if(logs.get('accuracy')>stopAccuracy):
      print("\nReached", stopAccuracy*100, " accuracy so cancelling training!")
      self.model.stop_training = True

callbackstop = callbackStop()

history = model.fit(train_generator, validation_data=validation_generator, 
                    epochs=150,
                    steps_per_epoch=50,
                    # batch_size=train_generator.batch_size,
                    # steps_per_epoch = train_generator.samples // train_generator.batch_size,
                    # validation_steps = validation_generator.samples // validation_generator.batch_size,
                    verbose=1,
                    callbacks=[
                               callbackstop, 
                              #  cp_callback
                               ],
                    )

model_path = '/content/gdrive/My Drive/Trained_Models/ODIR5K-bottleneck/'
checkpoint_path = model_path+'ODIR5K.ckpt'
checkpoint_dir = os.path.dirname(checkpoint_path)

model_save_weights = 'weight'
model_save_name_h5 = 'ODIR5K.h5'
model_save_name_tf = 'ODIR5K_TF'
model.save_weights(model_path)
model.save_weights(model_path+model_save_weights)
model.save(model_path)
model.save(model_path+model_save_name_h5)
model.save(model_path+model_save_name_tf,save_format='tf')

converter = tf.lite.TFLiteConverter.from_saved_model(model_path)
tflite_model = converter.convert()
open(model_path+"ODIR5K.tflite", "wb").write(tflite_model)

acc = history.history['accuracy']
val_acc = history.history['val_accuracy']

loss = history.history['loss']
val_loss = history.history['val_loss']

kappa = history.history['kappa score']
val_kappa = history.history['val_kappa score']

f1 = history.history['F-1 score']
val_f1 = history.history['F-1 score']

auc = history.history['auc']
val_auc = history.history['val_auc']

epochs_training = range(1, len(acc)+1)

plt.plot(epochs_training, acc, 'r', label='Training accuracy')
plt.plot(epochs_training, val_acc, 'y', label='Validation accuracy')
plt.title('Training and validation accuracy')
plt.legend(loc=0)
plt.figure()

plt.plot(epochs_training, loss, 'r', label='Training loss')
plt.plot(epochs_training, val_loss, 'y', label='Validation loss')
plt.title('Training and validation loss')
plt.legend(loc=1)
plt.figure()

plt.plot(epochs_training, kappa, 'r', label='Training kappa score')
plt.plot(epochs_training, val_kappa, 'y', label='Validation kappa score')
plt.title('Training and validation kappa score')
plt.legend(loc=2)
plt.figure()

plt.plot(epochs_training, auc, 'r', label='Training AUC value')
plt.plot(epochs_training, val_auc, 'y', label='Validation AUC value')
plt.title('Training and validation AUC value')
plt.legend(loc=3)
plt.figure()

plt.plot(epochs_training, f1, 'r', label='Training F1 score')
plt.plot(epochs_training, val_f1, 'y', label='Validation F1 score')
plt.title('Training and validation F1 score')
plt.legend(loc=4)
plt.figure()



plt.show()

# import tensorflow as tf
# import os
# import numpy as np

# model_path = '/content/drive/My Drive/Trained_Models/ODIR5K-bottleneck/'
# model_save_name_h5 = 'ODIR5K.h5'
# model = tf.keras.models.load_model(model_path+model_save_name_h5)

label_keys = list(train_generator.class_indices.keys())
label_values = list(train_generator.class_indices.values())

def getkey_indices(val):
  return label_keys[label_values.index(val)]

testlist = os.listdir(testing_path)
testlist.sort()

for ifile in range(0,len(testlist),50):
  img = image.load_img(testing_path+testlist[ifile], target_size=target_size,)
  imgplot = plt.imshow(img)
  imgarray = image.img_to_array(img)
  imgarray = np.expand_dims(imgarray, axis=0)

  images = np.vstack([imgarray])
  classes = model.predict(images, batch_size=8)
  # probability_model = tf.keras.Sequential([model, tf.keras.layers.Softmax()])
  # classes = probability_model.predict(images,batch_size=10)
  print("file :", testing_path+testlist[ifile]," | predicted as :", getkey_indices(np.argmax(classes)), "at :", np.argmax(classes))

testlist = os.listdir(testing_path)

testlist.sort()

for ifile in range(0,10):
  img = image.load_img(testing_path+testlist[ifile], target_size=target_size,)
  imgplot = plt.imshow(img)
  imgarray = image.img_to_array(img)
  imgarray = np.expand_dims(imgarray, axis=0)

  images = np.vstack([imgarray])
  classes = model.predict(images, batch_size=8)
  probability_model = tf.keras.Sequential([model, tf.keras.layers.Softmax()])
  classes = probability_model.predict(images,batch_size=8)
  print("file :", testing_path+testlist[ifile]," | predicted as :", getkey_indices(np.argmax(classes)), "at :", np.argmax(classes), classes)

model.evaluate_generator(validation_generator)

model.predict('/tmp/ODIR-5K/testing/1000_left.jpg')

# for ifile in testlist:
img = tf.keras.preprocessing.image.load_img('/tmp/ODIR-5K/testing/1604_left.jpg', target_size=target_size,)
imgplot = plt.imshow(img)
imgarray = tf.keras.preprocessing.image.img_to_array(img)
imgarray = np.expand_dims(imgarray, axis=0)

images = np.vstack([imgarray])
classes = model.predict_classes(images)
print(classes)
probability_model = tf.keras.Sequential([model, tf.keras.layers.Softmax()])
classes = probability_model.predict(images)
print(classes)
print("file : ", testing_path+testlist[300])
print("predicted as : ", np.argmax(classes))
# np.argmax((probability_model.predict(images) > 0.5).astype("int32"))

# for ifile in testlist:
img = tf.keras.preprocessing.image.load_img('/tmp/ODIR-5K/validation/Abnormalities/1031_left.jpg', target_size=target_size,)
# img = tf.keras.preprocessing.image.load_img('/tmp/ODIR-5K/training/Diabetes/1022_left.jpg', target_size=target_size,)
imgplot = plt.imshow(img)
imgarray = tf.keras.preprocessing.image.img_to_array(img)
imgarray = np.expand_dims(imgarray, axis=0)

images = np.vstack([imgarray])
classes = model.predict(images)
probability_model = tf.keras.Sequential([model, tf.keras.layers.Softmax()])
classes = probability_model.predict(images)
print("file : ", testing_path+testlist[300])
print("predicted as : ", np.argmax(classes))

predictfun = model.make_predict_function

model.predict(images)

testlist = os.listdir(testing_path)

for ifile in testlist:
  img = tf.keras.preprocessing.image.load_img(testing_path+ifile, target_size=target_size,)
  # imgplot = plt.imshow(img)
  imgarray = tf.keras.preprocessing.image.img_to_array(img)
  imgarray = np.expand_dims(imgarray, axis=0)

  images = np.vstack([imgarray])
  classes = model.predict(images, batch_size=8)
  # probability_model = tf.keras.Sequential([model, tf.keras.layers.Softmax()])
  # classes = probability_model.predict(images,batch_size=10)
  print("file :", testing_path+ifile," | predicted as :", getkey_indices(np.argmax(classes)), "at :", np.argmax(classes), " | x", np.argmax((model.predict(images) > 0.05).astype("int32")))
  # print("predicted as : ", classes)

test_dir = '/tmp/ODIR-5K/testing/'

print(len(os.listdir(testing_path)))

# test_datagen = ImageDataGenerator(rescale=1./255)

# test_generator = test_datagen.flow_from_directory(
#         test_dir,
#         target_size=target_size,
#         color_mode="rgb",
#         shuffle = False,
#         class_mode='categorical',
#         batch_size=1)

# filenames = test_generator.filenames
# nb_samples = len(filenames)

# predict = model.predict_generator(test_generator)
# np.argmax(predict[0])
# for i in range (500):
#   print(np.argmax(predict[i]))

os.chdir('/tmp/github')

!git config --global user.email 'azhariharisalhamdi@gmail.com'
!git config --global user.name 'Azhari Haris Al Hamdi'

!git config --global credential.helper store

# from distutils.dir_util import copy_tree
# import shutil

# model = '/content/gdrive/My Drive/Trained_Models/ODIR5K-bottleneck'
# dest = '/content/gdrive/My Drive/ODIR5K/181-280 epochs/ODIR5K-bottleneck'
# # copy_tree(model, '/tmp/ODIR5K-bottleneck')
# shutil.copytree(model, '/tmp/181-280 epochs/ODIR5K-bottleneck')

# Commented out IPython magic to ensure Python compatibility.
from getpass import getpass
# password = getpass('Password:')
# !git clone https://hamdiibnizhar:$password@github.com/hamdiibnizhar/ocular-disease-recognition-5k
# !git clone https://hamdiibnizhar:Foxhfire1@$@github.com/hamdiibnizhar/ocular-disease-recognition-5k
# !git clone https://hamdiibnizhar:Foxhfire1@$@github.com/hamdiibnizhar/ocular-disease-recognition-5k
# !git clone https://github.com/hamdiibnizhar/ocular-disease-recognition-5k.git
!git clone https://0d71dd55ea2142fa56278beae335f7cbeceb80f6@github.com/hamdiibnizhar/ocular-disease-recognition-5k.git
# %cd ocular-disease-recognition-5k
# create a file, then add it to stage

from distutils.dir_util import copy_tree
import shutil

model = '/content/drive/My Drive/Trained_Models/ODIR5K-bottleneck'
dest = '/tmp/github/ocular-disease-recognition-5k/models/ODIR5K-bottleneck'
# copy_tree(model, '/tmp/ODIR5K-bottleneck')
shutil.copytree(model, dest)
# shutil.make_archive('ODIR5K-bottleneck', 'zip', dest)

!sudo apt-get install git-lfs

!git lfs install

!git lfs track "*.psd"

!git add .gitattributes

!git lfs track "*.h5" "*.pb" "*.tflite" "*.data-00000-of-00002" "*.data-00001-of-00002" "*.data-00001-of-00002" "models/ODIR5K-bottleneck/ODIR5K.h5" "models/ODIR5K-bottleneck/ODIR5K_TF/variables/variables.data-00001-of-00002" "models/ODIR5K-bottleneck/.data-00001-of-00002"

!ls models/ODIR5K-bottleneck/assets

!rm -rf /tmp/github/ocular-disease-recognition-5k/models/ODIR5K-bottleneck

!git remote rm origin
!git remote add origin https://hamdiibnizhar:Foxhfire1@$@github.com/hamdiibnizhar/ocular-disease-recognition-5k.git

!git lsf add .

!git commit -m "init"
!git config --global user.email 'azhariharisalhamdi@gmail.com'
!git config --global user.name 'Azhari Haris Al Hamdi'
# !git config --global user.username 'hamdiibnizhar'

!git push origin master

!git push

!rm -rf /tmp/github/ocular-disease-recognition-5k/.lfsconfig