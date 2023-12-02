from keras.models import Sequential
from keras.layers import Dense, Conv1D, MaxPooling1D, Flatten, Embedding
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def count_words_in_texts(texts):
    words_count = 0
    for text in texts:
        words_count = words_count + len(text.split())

    return words_count

def count_max_len_in_texts(texts):
    max_len = 0
    for text in texts:
        text_len = len(text.split())
        if text_len > max_len:
            max_len = text_len

    return max_len

def clean_array(arr):
    # Удаление значений None и NaN
    cleaned = [str(x) for x in arr if x is not None and str(x).lower() != 'nan']
    return cleaned

def batch_generator(texts, batch_size):
    # Создание бесконечного цикла, чтобы генератор продолжал возвращать данные
    while True:
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]
            data = tokenizer.texts_to_sequences(batch_texts)
            data_pad = pad_sequences(data, maxlen=max_len)
            yield data_pad

# Загрузка данных из CSV-файла
legitime_texts = pd.read_csv('texts.csv', sep='\t', encoding='utf-16', dtype=str)
phishing_texts = pd.read_csv('phishing_texts.csv', sep='\t', encoding='utf-16', dtype=str)

# Извлечение колонки 'text' в массив
legitime_texts_array = legitime_texts['text'].values.tolist()
phishing_texts_array = phishing_texts['text'].values.tolist()

# Очистка массива
legitime_texts_array = clean_array(legitime_texts_array)
phishing_texts_array = clean_array(phishing_texts_array)

# предположим, что у нас есть некоторые данные
texts = legitime_texts_array + phishing_texts_array
legitime_count = len(legitime_texts_array)
phishing_count = len(phishing_texts_array)

words_count = count_words_in_texts(texts)
max_len = count_max_len_in_texts(texts)

tokenizer = Tokenizer(num_words=words_count,
    filters='!–"—#$%&amp;()*+,-./:;<=>?@[\\]^_`{|}~\t\n\r«»',
    lower=True,
    split=' ',
    char_level=False)
tokenizer.fit_on_texts(texts)

data = tokenizer.texts_to_sequences(texts)
data_pad = pad_sequences(data, maxlen=max_len)

X = data_pad
Y = np.array([[1, 0]]*legitime_count + [[0, 1]]*phishing_count)

indeces = np.random.choice(X.shape[0], size=X.shape[0], replace=False)
X = X[indeces]
Y = Y[indeces]

# создание модели
model = Sequential()
model.add(Embedding(words_count, 128, input_length=max_len))
model.add(Conv1D(128, 5, activation='relu'))
model.add(MaxPooling1D(5))
model.add(Flatten())
model.add(Dense(1, activation='sigmoid'))

# компиляция и обучение модели
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
history = model.fit(X, Y, batch_size=32, epochs=20,validation_split=0.2,)

plt.plot(history.history['categorical_accuracy'])
plt.title('Model accuracy')
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend(['Train'], loc='upper left')
plt.show()

model.save_weights('text_weights.h5') #Сохранение весов модели
model.save('text_model.keras') #Сохранение модели