import os
import logging
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler, ConversationHandler
from telegram.error import Conflict
import requests
from bs4 import BeautifulSoup
import re
import helpers

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Загружаем переменные окружения
load_dotenv()
BOT_TOKEN = os.getenv('TG_BOT_TOKEN')

# Инициализация бота
app = Application.builder().token(BOT_TOKEN).build()

# Клавиатура с брендами
brands_keyboard = ReplyKeyboardMarkup([
    ['Aprilia', 'RS', 'TUAREG'],
    ['Honda', 'CB', 'TRANSALP'],
    ['Yamaha', 'XSR', 'XV'],
    ['BMW', 'R', 'S', 'K', 'G', 'F'],
    ['HD', 'RK', 'SG', 'RG', 'FB', 'FTB']
], one_time_keyboard=True, resize_keyboard=True)

# Клавиатура с годами
years_keyboard = ReplyKeyboardMarkup([
    ['2010', '2011', '2012', '2013', '2014'],
    ['2015', '2016', '2017', '2018', '2019'],
    ['2020', '2021', '2022', '2023']
], resize_keyboard=True)

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    logger.info(f"Пользователь {user_id} отправил команду /start")
    context.user_data.clear()  # Очищаем данные пользователя
    context.user_data['step'] = 'select_brand'  # Устанавливаем начальный шаг
    await update.message.reply_text(
        "Привет! Я бот, который поможет найти мотоцикл.\nВыберите значение.",
        reply_markup=brands_keyboard
    )

# Обработчик команды /off
async def off_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    logger.info(f"Пользователь {user_id} отправил команду /off")
    context.user_data.clear()  # Очищаем данные пользователя
    context.user_data['step'] = 'select_brand'  # Сбрасываем шаг
    await update.message.reply_text("Поиск завершён. Чтобы начать заново, используйте /start.", reply_markup=ReplyKeyboardRemove())


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data.get("step")

    if step == "select_brand":
        await select_brand(update, context)
    elif step == "select_year":
        await select_year(update, context)
    else:
        await update.message.reply_text("Пожалуйста, начните с команды /start.")


# Обработчик выбора бренда
async def select_brand(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    brand = update.message.text
    # Пропускаем, если сообщение соответствует формату года
    if re.match(r"^20(0[1-9]|[12]\d|23)$", brand):
        logger.info(f"Сообщение '{brand}' похоже на год, пропускаем в select_brand для пользователя {user_id}")
        return

    logger.info(f"Пользователь {user_id} выбрал бренд: {brand}")

    # Проверяем, соответствует ли текст бренду (по вашему регулярному выражению)
    valid_brands = r"^(Aprilia|RS|TUAREG|Honda|CB|TRANSALP|Yamaha|XSR|XV|BMW|[RSKGF]|HD|RK|SG|RG|FB|FTB)$"
    if not filters.Regex(valid_brands).check_update(update):
        await update.message.reply_text("Пожалуйста, выберите бренд из предложенных.")
        logger.info(f"Пользователь {user_id} выбрал некорректный бренд: {brand}")
        return

    # Сохраняем модель и переходим к следующему шагу
    context.user_data['model'] = brand.lower()
    context.user_data['step'] = 'select_year'

    # Убираем клавиатуру брендов и показываем клавиатуру с годами
    await update.message.reply_text(
        f"Вы выбрали {brand}",
        reply_markup=ReplyKeyboardRemove()
    )
    await update.message.reply_text(
        "Выберите год",
        reply_markup=years_keyboard
    )
    logger.info(f"Отправлено сообщение с выбором года для пользователя {user_id}")

# Обработчик выбора года
async def select_year(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    year = update.message.text
    # Проверяем, соответствует ли текст году (по вашему регулярному выражению)
    if not re.match(r"^20(0[1-9]|[12]\d|23)$", year):
        logger.info(f"Пользователь {user_id} выбрал некорректный год: {year}")
        await update.message.reply_text("Пожалуйста, выберите год из предложенных.")
        return ConversationHandler.END  # Завершаем обработку

    logger.info(f"Пользователь {user_id} выбрал год: {year}")

    # Сохраняем год и переходим к следующему шагу
    context.user_data['year'] = year
    context.user_data['step'] = 'select_price'

    # Формируем инлайн-кнопки для выбора цены
    buttons_price = []
    for i in range(5, 39):
        buttons_price.append(InlineKeyboardButton(f"{i}k", callback_data=f"{i}000"))

    rows = [buttons_price[i:i + 6] for i in range(0, len(buttons_price), 6)]
    price_keyboard = InlineKeyboardMarkup(rows)

    # Убираем клавиатуру годов и показываем инлайн-кнопки с ценами
    await update.message.reply_text(
        f"Вы выбрали {year} год",
        reply_markup=ReplyKeyboardRemove()
    )
    await update.message.reply_text(
        "Выберите максимальную цену:",
        reply_markup=price_keyboard
    )
    logger.info(f"Отправлено сообщение с выбором цены для пользователя {user_id}")
    return ConversationHandler.END  # Завершаем обработку

# Обработчик выбора цены
async def select_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    query = update.callback_query
    await query.answer()

    if context.user_data.get('step') != 'select_price':
        return

    max_price = query.data
    context.user_data['max_price'] = max_price
    logger.info(f"Пользователь {user_id} выбрал максимальную цену: {max_price}")

    # Собираем параметры для поиска
    model = context.user_data.get('model')
    year = context.user_data.get('year')

    # Выполняем поиск
    try:
        url = helpers.create_link(model, year, max_price, sort=True)
        logger.info(f"Сформирован URL для поиска: {url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        bikes = []

        for item in soup.select('.listing-item'):
            title = item.select_one('.listing-item__title')
            price = item.select_one('.listing-item__price')
            link = item.select_one('.listing-item__link')

            if title and price and link:
                title_text = title.get_text(strip=True).lower()
                price_text = price.get_text(strip=True)
                link_href = 'https://moto.av.by' + link['href']

                try:
                    price_value = int(''.join(filter(str.isdigit, price_text)))
                    if price_value > int(max_price):
                        continue
                except ValueError:
                    continue

                bikes.append({'title': title_text, 'price': price_text, 'link': link_href})

        if bikes:
            reply = "Вот что я нашёл:\n\n"
            for bike in bikes[:5]:
                reply += f"{bike['title']}\nЦена: {bike['price']}\nСсылка: {bike['link']}\nСсылка с фильтрами: {url}\n\n"
            await query.message.reply_text(reply)
            logger.info(f"Найдено {len(bikes)} мотоциклов для пользователя {user_id}")
        else:
            await query.message.reply_text("К сожалению, ничего не найдено.")
            logger.warning(f"Мотоциклы не найдены для пользователя {user_id}")
    except requests.Timeout:
        logger.error("Превышено время ожидания запроса")
        await query.message.reply_text("Сайт не отвечает. Попробуй позже.")
    except requests.RequestException as error:
        logger.error(f"Ошибка запроса: {error}")
        await query.message.reply_text("Произошла ошибка при поиске. Попробуй позже.")
    except Exception as error:
        logger.error(f"Неизвестная ошибка: {error}")
        await query.message.reply_text("Произошла неизвестная ошибка. Попробуй позже.")

    # Сбрасываем состояние после поиска
    context.user_data['step'] = 'select_brand'

# Обработчик команды /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    logger.info(f"Пользователь {user_id} отправил команду /help")
    await update.message.reply_text("Я бот для поиска мотоциклов на av.by.\nКоманды:\n/start - начать\n/off - завершить поиск\n/help - помощь")

# Обработчик ошибок
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Произошла ошибка: {context.error}")
    if isinstance(context.error, Conflict):
        logger.error("Конфликт: другой экземпляр бота уже запущен. Останавливаю текущий процесс.")
        await app.stop()
        raise SystemExit("Остановлено из-за конфликта getUpdates")


# Добавляем обработчики
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("off", off_command))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(CallbackQueryHandler(select_price))
app.add_handler(CommandHandler("help", help_command))
app.add_error_handler(error_handler)

# Запуск бота
logger.info("Бот запущен")
app.run_polling()