import os
import pandas as pd
from loguru import logger
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


# ============================
# Параметры проекта
# ============================
RAW1_DATA_PATH = "../data/scraped/artefact_catalog_data_1_300.json"
RAW2_DATA_PATH = "../data/scraped/artefact_catalog_data_300_756.json"
PROCESSED_DATA_PATH = "../data/processed/cleaned_dataset.csv"

# ============================
# Функции для загрузки данных
# ============================
def load_file(filepath):
    """
    Функция для загрузки данных из файла JSON.
    Возвращает DataFrame при успешной загрузке или None при ошибке.
    """
    try:
        df = pd.read_json(filepath)
        logger.success(f"Файл {filepath} успешно загружен. Количество строк: {len(df)}")
        return df
    except FileNotFoundError:
        logger.error(f"Ошибка: Файл {filepath} не найден.")
    except pd.errors.EmptyDataError:
        logger.error(f"Ошибка: Файл {filepath} пуст или не содержит данных.")
    except Exception as e:
        logger.error(f"Произошла ошибка при загрузке файла {filepath}: {e}")
    return None


def load_data(filepath1, filepath2):
    """
    Основная функция для загрузки двух файлов и объединения их в один DataFrame.
    """
    logger.info("Загрузка данных ...")

    # Загрузка первого файла
    df1 = load_file(filepath1)
    if df1 is None:
        return None

    # Загрузка второго файла
    df2 = load_file(filepath2)
    if df2 is None:
        return None

    # Объединение данных
    try:
        artefact_catalog_df = pd.concat([df1, df2], ignore_index=True)
        logger.success(f"Итоговый датасет собран. Количество строк: {len(artefact_catalog_df)}")
        return artefact_catalog_df
    except Exception as e:
        logger.error(f"Произошла ошибка при объединении данных: {e}")
        return None


# ============================
# Функция для очистки данных
# ============================
def word_count(text):
    """
    Функция для подсчета количества слов в тексте
    :param text:
    :return:
    """
    if isinstance(text, str):
        return len(word_tokenize(text))
    return 0


def clean_text(text, stop_words):
    """
    Очищает текст:
    - Удаляет числа и специальные символы.
    - Убирает стоп-слова.
    """


    # Удаление чисел и специальных символов
    text = re.sub(r"[^\w\s]", "", text)  # Убираем знаки препинания
    text = re.sub(r"\b\d+\b", "", text)  # Убираем числа

    # Приведение к нижнему регистру
    text = text.lower()

    # Удаление стоп-слов
    words = text.split()
    filtered_words = [word for word in words if word not in stop_words]

    # Соединяем очищенные слова обратно в строку
    return " ".join(filtered_words)


def clean_data(df, stop_words):
    logger.info("Начало очистки данных...")
    # try:
    # Удаляем строки без описания
    initial_length = len(df)
    df = df.dropna(subset=['description'])
    df = df[df['description'].str.strip() != '']
    df['cleaned_description'] = df['description'].apply(lambda x: clean_text(x, stop_words=stop_words))
    cleaned_length = len(df)
    logger.info(f"Удалено строк без описания: {initial_length - cleaned_length}")

    # Удаляем дубликаты
    df = df.drop_duplicates(subset=["title", "url"])
    logger.info(f"Дубликаты удалены. Количество строк после очистки: {len(df)}")

    # Заполняем пропуски в остальных колонках пустыми значениями
    df = df.fillna('')
    logger.success("Очистка данных завершена.")
    return df
    # except Exception as e:
    #     logger.error(f"Ошибка при очистке данных: {e}")
    #     exit(1)


# ============================
# Функция для сохранения данных
# ============================
def save_data(df, output_path):
    logger.info(f"Сохранение очищенных данных в {output_path}...")
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
        logger.success(f"Данные успешно сохранены в {output_path}. Количество строк: {len(df)}")
    except Exception as e:
        logger.error(f"Ошибка при сохранении данных: {e}")
        exit(1)


# ============================
# Основная функция
# ============================
def main():
    # Загрузка стоп-слов
    nltk.download("stopwords")
    stop_words = set(stopwords.words("russian"))
    logger.info("Запуск скрипта предобработки данных...")
    df = load_data(RAW1_DATA_PATH, RAW2_DATA_PATH)
    cleaned_df = clean_data(df, stop_words)
    save_data(cleaned_df, PROCESSED_DATA_PATH)
    logger.info("Скрипт предобработки данных выполнен успешно.")


if __name__ == "__main__":
    main()
