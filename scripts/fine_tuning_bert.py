from transformers import (
    AutoTokenizer,
    AutoModelForMaskedLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling)
from datasets import Dataset
import pandas as pd
from loguru import logger


# ============================
# Параметры скрипта
# ============================
DATA_PATH = "../data/processed/cleaned_dataset.csv"
BERT_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
BERT_MODEL_PATH = "../models/bert_model/fine_tuned_model"


# ============================
# Функция загрузки данных
# ============================
def load_data(filepath):
    logger.info(f"Загрузка данных из {filepath}...")
    try:
        df = pd.read_csv(filepath)
        logger.success("Файл успешно загружен.")
        logger.info(f"Данные загружены: {len(df)} строк с описаниями.")
        descriptions = df['description'].tolist()
        return descriptions
    except FileNotFoundError:
        logger.error(f"Ошибка: Файл {filepath} не найден.")
        exit(1)
    except Exception as e:
        logger.error(f"Произошла ошибка при загрузке данных: {e}")
        exit(1)


# ============================
# Функция для сохранения обновленной модели
# ============================
def save_model(model, tokenizer, output_path):
    logger.info(f"Сохранение обновленной модели в {output_path}...")
    try:
        model.save_pretrained(BERT_MODEL_PATH)
        tokenizer.save_pretrained(BERT_MODEL_PATH)
        logger.success(f"Модель успешно дообучена и сохранена! {output_path}")
    except Exception as e:
        logger.error(f"Произошла ошибка при сохранении модели: {e}")
        exit(1)


# ============================
# Основная функция
# ============================
def main():
    logger.info(f"Запуск скрипта дообучения модели {BERT_MODEL_NAME}...")

    # Подготовка корпуса текстов
    descriptions = load_data(DATA_PATH)

    # Загрузка модели и токенизатора
    tokenizer = AutoTokenizer.from_pretrained(BERT_MODEL_NAME)
    model = AutoModelForMaskedLM.from_pretrained(BERT_MODEL_NAME)

    # Преобразование текстов
    raw_dataset = Dataset.from_dict({"text": descriptions})
    tokenized_dataset = raw_dataset.map(
        lambda x: tokenizer(x["text"], truncation=True, padding="max_length", max_length=512),
        batched=True)

    # Дата-коллатор для Masked Language Modeling
    data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=True, mlm_probability=0.15)

    # Параметры обучения
    training_args = TrainingArguments(
        output_dir="./fine_tuned_model",
        evaluation_strategy="epoch",
        save_strategy="epoch",
        per_device_train_batch_size=4,  # Reduce batch size to fit GPU memory
        gradient_accumulation_steps=2,  # Accumulate gradients to simulate larger batch size
        num_train_epochs=3,
        learning_rate=5e-5,
        weight_decay=0.01,
        logging_dir="./logs",
        logging_steps=50,
        save_total_limit=2,
        report_to="tensorboard",  # Включаем TensorBoard
        fp16=True  # Enable mixed precision training to save memory
    )

    # Trainer для дообучения
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
        eval_dataset=tokenized_dataset,  # Adding eval_dataset to fix the error
        data_collator=data_collator
    )

    # Запуск обучения
    trainer.train()

    # Сохранение модели и токенизатора
    save_model(model, tokenizer, BERT_MODEL_PATH)

    logger.info(f"Скрипт дообучения модели {BERT_MODEL_NAME} успешно завершен.")


if __name__ == "__main__":
    main()