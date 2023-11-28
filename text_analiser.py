import language_tool_python

def check_text(text):
    tool = language_tool_python.LanguageTool('ru-RU')
    matches = tool.check(text)
    for match in matches:
        print(f"Ошибка: {match.ruleId}, Сообщение: {match.message}")
        print(f"Исправление: {match.replacements}")

text = "Ваш текст для проверки"
check_text(text)

from keras.models import Sequential
from keras.layers import Dense, Conv1D, MaxPooling1D, Flatten, Embedding
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences

# предположим, что у нас есть некоторые данные
texts = ["Обновите пароль", "Введите данные карты", ...]  # тексты веб-страниц
labels = [1, 1, ...]  # 1 для фишинговых сайтов, 0 для нормальных сайтов

# подготовка данных
tokenizer = Tokenizer(num_words=5000)
tokenizer.fit_on_texts(texts)
sequences = tokenizer.texts_to_sequences(texts)
data = pad_sequences(sequences, maxlen=400)

# создание модели
model = Sequential()
model.add(Embedding(5000, 50, input_length=400))
model.add(Conv1D(128, 5, activation='relu'))
model.add(MaxPooling1D(5))
model.add(Flatten())
model.add(Dense(1, activation='sigmoid'))

# компиляция и обучение модели
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
model.fit(data, labels, validation_split=0.2, epochs=10)