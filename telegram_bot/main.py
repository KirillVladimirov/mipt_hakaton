# ============================
# Telegram-бот
# ============================
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from loguru import logger
from downloader import load_data, load_faiss_index, load_topic_model
from search import find_similar_documents, find_exhibitions


# ============================
# Параметры проекта
# ============================
DATA_PATH = "../data/processed/cleaned_dataset.csv"
INDEX_PATH = "../models/faiss_index/faiss_index.pkl"
MODEL_PATH = "../models/bertopic_model/bertopic_model.pkl"
BERT_MODEL_PATH = "../models/bert_model/fine_tuned_model"

# ============================
# Обработчики команд
# ============================

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("/start команда отправлена")
    await update.message.reply_text("Привет! Отправьте мне описание экспоната или новость из мира искусства, и я найду схожие экспонаты и выставки.")


# Обработчик команды /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("/help команда отправлена")
    await update.message.reply_text("Отправьте текст с описанием экспоната, и я покажу подходящие результаты.")


# Обработчик команды /about
async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("/about команда отправлена")
    await update.message.reply_text("Этот бот использует BERTopic для поиска схожих экспонатов и выставок.")


# Обработчик текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    logger.info(f"Получено сообщение: {query}")
    exhibits = find_similar_documents(query, topic_model, probabilities_index, df)
    print(exhibits)
    exhibitions = find_exhibitions(df)
    print(exhibitions)

    response = "🎨 *Топ-3 экспоната:*\n"
    for exhibit in exhibits:
        response += f"🔹 [{exhibit['name']}]({exhibit['url']})\n"
        if exhibit['authors']:
            response += f"   *Авторы*: {exhibit['authors']}\n"
        response += f"   {exhibit['description']}...\n\n"

    response += "🏰 *Топ-3 выставки:*\n" + "\n".join(exhibitions)
    logger.info("Отправка результатов пользователю.")
    await update.message.reply_text(response, parse_mode="Markdown")


# ============================
# Основная функция
# ============================
if __name__ == "__main__":
    logger.info("Запуск Telegram-бота...")
    TOKEN = "7585876266:AAHtSMHVpgIFNr2EqSg7yvBmXOwmszgPJLo"

    # Подготовка данных и модели с обработкой ошибок
    df = load_data(DATA_PATH)
    topic_model = load_topic_model(MODEL_PATH)
    probabilities_index = load_faiss_index(INDEX_PATH)

    # Инициализация бота
    logger.info("Telegram-бот готов к запуску.")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("about", about_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Бот запущен...")
    app.run_polling()
