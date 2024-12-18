import pandas as pd
import numpy as np
import faiss
from bertopic import BERTopic
from sklearn.preprocessing import normalize
from loguru import logger
import pickle


# ============================
# Параметры скрипта
# ============================
DATA_PATH = "../data/processed/cleaned_dataset.csv"
TOPIC_MODEL_PATH = "../models/bertopic_model/bertopic_model.pkl"
INDEX_PATH = "../models/faiss_index/faiss_index.pkl"


# ============================
# Функция загрузки данных
# ============================
def load_data(filepath):
    logger.info(f"Загрузка данных из {filepath}...")
    try:
        df = pd.read_csv(filepath)
        logger.success("Файл успешно загружен.")
        logger.info(f"Данные загружены: {len(df)} строк с описаниями.")
        return df
    except FileNotFoundError:
        logger.error(f"Ошибка: Файл {filepath} не найден.")
        exit(1)
    except Exception as e:
        logger.error(f"Произошла ошибка при загрузке данных: {e}")
        exit(1)


# ============================
# Функция загрузки BERTopic модели
# ============================
def load_topic_model(model_path):
    logger.info(f"Загрузка BERTopic модели из {model_path}...")
    try:
        topic_model = BERTopic.load(model_path)
        logger.success("Модель BERTopic успешно загружена!")
        return topic_model
    except FileNotFoundError:
        logger.error(f"Ошибка: Модель не найдена по пути {model_path}.")
        exit(1)
    except Exception as e:
        logger.error(f"Произошла ошибка при загрузке модели: {e}")
        exit(1)


# ============================
# Построение FAISS индекса и сохранение в файл
# ============================
def build_and_save_faiss_index(df, topic_model, output_path):
    logger.info("Начало построения FAISS индекса...")
    try:
        # Генерация вероятностей тем
        probabilities = topic_model.probabilities_
        if probabilities is None:
            logger.error(
                "Ошибка: Вероятности тем отсутствуют. Убедитесь, что модель BERTopic была обучена с сохранением вероятностей.")
            exit(1)

        # Нормализация и построение индекса
        probabilities_matrix = normalize(np.array(probabilities))
        index = faiss.IndexFlatL2(probabilities_matrix.shape[1])
        index.add(probabilities_matrix)
        logger.success("FAISS индекс успешно построен!")

        # Сохранение индекса в файл
        with open(output_path, "wb") as f:
            pickle.dump(index, f)
        logger.success(f"FAISS индекс сохранен в {output_path}.")
    except Exception as e:
        logger.error(f"Произошла ошибка при построении или сохранении FAISS индекса: {e}")
        exit(1)


# ============================
# Основная функция
# ============================
def main():
    logger.info("Запуск скрипта построения FAISS индекса...")

    # Загрузка данных
    df = load_data(DATA_PATH)

    # Загрузка модели BERTopic
    topic_model = load_topic_model(TOPIC_MODEL_PATH)

    # Построение и сохранение FAISS индекса
    build_and_save_faiss_index(df, topic_model, INDEX_PATH)

    logger.info("Скрипт построения FAISS индекса успешно завершен.")


if __name__ == "__main__":
    main()
