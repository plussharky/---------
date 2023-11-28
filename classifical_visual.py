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

image_width, image_height = 1280, 720
epochs = 80
lot_size = 1  #batch_size 
if K.image_data_format() != 'channels_first':
     input_shape = (image_width, image_height, 3)
else:
     input_shape = (3, image_width, image_height)   

# Загрузка данных из CSV файлов
legitimate_data = pd.read_csv('legitimate.csv', sep='\t', encoding='utf-16')
phishing_data = pd.read_csv('phishing.csv', sep='\t', encoding='utf-16')

# Создание директорий для обучающих и проверочных данных
train_directory_legitimate = 'Dataset/Train/Legitimate'
validation_directory_legitimate = 'Dataset/Validation/Legitimate'
train_directory_phishing = 'Dataset/Train/Phishing'
validation_directory_phishing = 'Dataset/Validation/Phishing'

# Создание обучающих и проверочных директорий для легитимных сайтов
os.makedirs(train_directory_legitimate, exist_ok=True)
os.makedirs(validation_directory_legitimate, exist_ok=True)

# Создание обучающих и проверочных директорий для фишинговых сайтов
os.makedirs(train_directory_phishing, exist_ok=True)
os.makedirs(validation_directory_phishing, exist_ok=True)

# Копирование скриншотов в соответствующие директории для легитимных сайтов
for index, row in legitimate_data.iterrows():
    screenshot_path = row['screenshot_path']
    destination_path = os.path.join(train_directory_legitimate, f"{index}.png")
    shutil.copy(screenshot_path, destination_path)

# Разделение данных на обучающую и проверочную выборку для легитимных сайтов
legitimate_train, legitimate_validation = train_test_split(legitimate_data, test_size=0.2, random_state=42)

# Копирование скриншотов в соответствующие директории для фишинговых сайтов
for index, row in phishing_data.iterrows():
    screenshot_path = row['screenshot_path']
    destination_path = os.path.join(train_directory_phishing, f"{index}.png")
    shutil.copy(screenshot_path, destination_path)

# Разделение данных на обучающую и проверочную выборку для фишинговых сайтов
phishing_train, phishing_validation = train_test_split(phishing_data, test_size=0.2, random_state=42)

# Объединение данных обратно, если это необходимо
train_data = pd.concat([legitimate_train, phishing_train], ignore_index=True)
validation_data = pd.concat([legitimate_validation, phishing_validation], ignore_index=True)

# Создание генераторов данных для обучения и проверки
train_datagen = ImageDataGenerator(rescale=1. / 255)
validation_datagen = ImageDataGenerator(rescale=1. / 255)

train_generator = train_datagen.flow_from_dataframe(
    dataframe=train_data,
    directory=None,
    x_col="screenshot_path",
    y_col="category",  # Замените "label" на ваше фактическое имя столбца меток
    target_size=(image_width, image_height),
    batch_size=lot_size,
    class_mode='binary',
    subset='training')

validation_generator = validation_datagen.flow_from_dataframe(
    dataframe=validation_data,
    directory=None,
    x_col="screenshot_path",
    y_col="category",  # Замените "label" на ваше фактическое имя столбца меток
    target_size=(image_width, image_height),
    batch_size=lot_size,
    class_mode='binary',
    subset='validation')

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
    steps_per_epoch=train_data.shape[0] // lot_size,
    epochs=epochs,
    validation_data=validation_generator,
    validation_steps=validation_data.shape[0] // lot_size)

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
