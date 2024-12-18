# ============================
# Загрузка данных, модели и FAISS индекса
# ============================
import pandas as pd
from bertopic import BERTopic
from loguru import logger
import pickle


def load_data(filepath):
    logger.info(f"Загрузка данных из {filepath}...")
    try:
        df = pd.read_csv(filepath)
        logger.success("Файл успешно загружен.")
        logger.info(f"Данные загружены: {len(df)} строк с описаниями")
        return df
    except FileNotFoundError:
        logger.error(f"Ошибка: Файл {filepath} не найден.")
        exit(1)
    except pd.errors.EmptyDataError:
        logger.error("Ошибка: Файл пуст или не содержит данных.")
        exit(1)
    except Exception as e:
        logger.error(f"Произошла ошибка при загрузке данных: {e}")
        exit(1)

def load_topic_model(model_path):
    logger.info(f"Загрузка BERTopic модели из {model_path}...")
    try:
        topic_model = BERTopic.load(model_path)
        logger.success("Модель успешно загружена!")
        return topic_model
    except FileNotFoundError:
        logger.error(f"Ошибка: Модель не найдена по пути {model_path}.")
        exit(1)
    except Exception as e:
        logger.error(f"Произошла ошибка при загрузке модели: {e}")
        exit(1)

def load_faiss_index(index_path):
    logger.info(f"Загрузка FAISS индекса из {index_path}...")
    try:
        with open(index_path, "rb") as f:
            index = pickle.load(f)
        logger.success("Индекс FAISS успешно загружен!")
        return index
    except FileNotFoundError:
        logger.error(f"Ошибка: FAISS индекс не найден по пути {index_path}.")
        exit(1)
    except Exception as e:
        logger.error(f"Произошла ошибка при загрузке FAISS индекса: {e}")
        exit(1)