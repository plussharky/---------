import numpy
import os
import keras
import tensorflow
import shutil
import pandas as pd
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten, BatchNormalization, Activation
from keras.layers import Conv2D, MaxPooling2D
from keras import backend as K
from keras.preprocessing.image import ImageDataGenerator
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

def count_files_in_directory(path):
    # Счетчик общего количества файлов
    total_image_count = 0

    # Проходим по всем поддиректориям в директории
    for root, dirs, files in os.walk(path):
        # Считаем количество файлов в текущей поддиректории
        image_count = len(files)
        
        # Прибавляем к общему счетчику
        total_image_count += image_count

    return total_image_count

image_width, image_height = 1280, 720
epochs = 80
lot_size = 1  #batch_size 
tain_path = './Dataset/Train/'
valid_path = './Dataset/Validation/'
if K.image_data_format() != 'channels_first':
     input_shape = (image_width, image_height, 3)
else:
     input_shape = (3, image_width, image_height)   

train_items_count = count_files_in_directory(tain_path)
valid_items_count = count_files_in_directory(valid_path)

# Создание директорий для обучающих и проверочных данных
train_directory_legitimate = 'Dataset/Train/Legitimate'
validation_directory_legitimate = 'Dataset/Validation/Legitimate'
train_directory_phishing = 'Dataset/Train/Phishing'
validation_directory_phishing = 'Dataset/Validation/Phishing'

# Создание генераторов данных для обучения и проверки
train_datagen = ImageDataGenerator(
    rescale=1./255,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True)

validation_datagen = ImageDataGenerator(rescale=1./255)

train_generator = train_datagen.flow_from_directory(
    './Dataset/Train/',
    target_size=(image_width, image_height),
    batch_size=lot_size,
    class_mode='binary')

validation_generator = validation_datagen.flow_from_directory(
    './Dataset/Validation/',
    target_size=(image_width, image_height),
    batch_size=lot_size,
    class_mode='binary')

# Определение модели и компиляция
model = Sequential()
model.add(Conv2D(32, (3, 3), activation='relu', input_shape=input_shape))
model.add(MaxPooling2D((2, 2)))
model.add(Conv2D(64, (3, 3), activation='relu'))
model.add(MaxPooling2D((2, 2)))
model.add(Conv2D(128, (3, 3), activation='relu'))
model.add(MaxPooling2D((2, 2)))
model.add(Flatten())
model.add(Dense(512, activation='relu'))
model.add(Dense(1, activation='sigmoid'))
model.compile(loss='binary_crossentropy', optimizer='rmsprop', metrics=['accuracy'])

# Обучение модели
history = model.fit(
    train_generator,
    steps_per_epoch=train_items_count // lot_size,
    epochs=epochs,
    validation_data=validation_generator,
    validation_steps=valid_items_count // lot_size)

# Вывод графика обучения
plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('Model accuracy')
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend(['Train', 'Validation'], loc='upper left')
plt.show()

# Сохранение модели
model.save('phishing_detection_model.h5')
