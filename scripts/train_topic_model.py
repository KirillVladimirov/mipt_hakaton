import os
import pandas as pd
import numpy as np
from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from loguru import logger
import hdbscan
# ============================
# Параметры скрипта
# ============================
DATA_PATH = "../data/processed/cleaned_dataset.csv"
MODEL_PATH = "../models/bertopic_model/bertopic_model.pkl"
BERT_MODEL_PATH = "../models/bert_model/fine_tuned_model"
EMBEDDING_PATH = "../data/processed/embeddings_and_indices.npz"


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
# Функция загрузки существующей модели
# ============================
def load_bert_model(model_path):
    logger.info(f"Загрузка существующей модели BERTopic из {model_path}...")
    try:
        embedding_model = SentenceTransformer(model_path)
        logger.success("Модель BERT успешно загружена.")
        return embedding_model
    except FileNotFoundError:
        logger.error(f"Ошибка: Модель не найдена по пути {model_path}.")
        exit(1)
    except Exception as e:
        logger.error(f"Произошла ошибка при загрузке модели: {e}")
        exit(1)


def get_embeddings(bert_model, df, embedding_path):
    if os.path.exists(embedding_path):
        logger.info(f"Файл существует: {embedding_path}")
        embeddings = np.load(embedding_path)
        embeddings = embeddings["embeddings"]
        logger.success(f"Эмбеддинги загружены: {embeddings.shape}.")
    else:
        logger.success("Начинаю расчет эмбеддингов.")
        docs = df['description'].tolist()
        embeddings = bert_model.encode(docs, show_progress_bar=True)
        logger.success(f"Эмбеддинги расчитаны: {embeddings.shape}.")
    return embeddings


# ============================
# Функция для дообучения модели
# ============================
def train_bertopic_model(bert_model, df, embeddings):
    logger.info("Начало обучения модели...")
    try:
        cleaned_docs = df['cleaned_description'].astype(str).tolist()
        hdbscan_model = hdbscan.HDBSCAN(min_cluster_size=30, prediction_data=True)

        topic_model = BERTopic(embedding_model=bert_model, hdbscan_model=hdbscan_model,
                               calculate_probabilities=True)
        logger.info(f"Размер документов: {len(cleaned_docs)}, размер эмбеддингов: {embeddings.shape}")
        assert embeddings.shape[0] == len(cleaned_docs)
        topics, probs = topic_model.fit_transform(cleaned_docs, embeddings=embeddings)
        topic_info = topic_model.get_topic_info()
        print("Информация о темах:")
        print(topic_info[["Topic", "Count", "Name"]].to_markdown())
        return topic_model
        logger.success("Модель успешно обучена.")
    except Exception as e:
        logger.error(f"Произошла ошибка при обучении модели: {e}")
        exit(1)


# ============================
# Функция для сохранения обновленной модели
# ============================
def save_model(topic_model, output_path):
    logger.info(f"Сохранение обновленной модели в {output_path}...")
    try:
        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        topic_model.save(output_path)
        logger.success(f"Обновленная модель сохранена в {output_path}.")
    except Exception as e:
        logger.error(f"Произошла ошибка при сохранении модели: {e}")
        exit(1)


# ============================
# Основная функция
# ============================
def main():
    logger.info("Запуск скрипта дообучения модели BERTopic...")

    # Шаг 1: Загрузка новых данных
    df = load_data(DATA_PATH)

    # Шаг 2: Загрузка существующей модели
    bert_model = load_bert_model(BERT_MODEL_PATH)

    # Шаг 3: Получение эмбеддингов
    embeddings = get_embeddings(bert_model, df, EMBEDDING_PATH)

    # Шаг 3: Дообучение модели
    topic_model = train_bertopic_model(bert_model, df, embeddings)

    # Шаг 4: Сохранение обновленной модели
    save_model(topic_model, MODEL_PATH)

    logger.info("Скрипт дообучения модели BERTopic успешно завершен.")


if __name__ == "__main__":
    main()
