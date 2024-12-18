# ============================
# Поиск схожих документов
# ============================
import numpy as np
from sklearn.preprocessing import normalize
from loguru import logger


def find_similar_documents(query, topic_model, index, df, top_k=3):
    logger.info(f"Поиск схожих документов по запросу: {query}")
    query_probabilities = topic_model.transform([query])[1][0]  # Получаем распределение тем для запроса
    query_vector = normalize(np.array([query_probabilities]))
    distances, indices = index.search(query_vector, top_k)
    logger.info(f"Найдено {len(indices[0])} похожих экспонатов.")
    results = []
    for idx in indices[0]:
        row = df.iloc[idx]
        results.append({
            "name": row['title'],
            "url": row['url'],
            "authors": row['authors'],
            "description": row['description'][:200]  # Ограничение до 200 символов
        })
    return results


def find_exhibitions(df, top_k=3):
    """
    Поиск топ-K выставок с указанием музея (коллекции).
    """
    logger.info(f"Поиск топ-{top_k} выставок...")

    # Группировка по выставкам и коллекциям
    top_exhibitions = (
        df.groupby(['exhibition', 'collection'])
        .size()
        .sort_values(ascending=False)
        .head(top_k)
        .reset_index()
    )

    # Формирование результатов
    return [
        f"🔹 {row['exhibition']}, {row['collection'] or 'Музей не указан'}"
        for _, row in top_exhibitions.iterrows()
    ]
