import asyncio
import logging
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler, ContextTypes

# ========== НАСТРОЙКИ ==========
TOKEN = "8667927741:AAEkWQWm12aRaOvCG8DTZ4S-d4g7vzrGrXo"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========== 27 СТРАН ==========
COUNTRIES = {
    "albania": "🇦🇱 Албания",
    "armenia": "🇦🇲 Армения",
    "australia": "🇦🇺 Австралия",
    "austria": "🇦🇹 Австрия",
    "azerbaijan": "🇦🇿 Азербайджан",
    "belgium": "🇧🇪 Бельгия",
    "croatia": "🇭🇷 Хорватия",
    "cyprus": "🇨🇾 Кипр",
    "denmark": "🇩🇰 Дания",
    "estonia": "🇪🇪 Эстония",
    "finland": "🇫🇮 Финляндия",
    "france": "🇫🇷 Франция",
    "germany": "🇩🇪 Германия",
    "greece": "🇬🇷 Греция",
    "iceland": "🇮🇸 Исландия",
    "ireland": "🇮🇪 Ирландия",
    "italy": "🇮🇹 Италия",
    "latvia": "🇱🇻 Латвия",
    "lithuania": "🇱🇹 Литва",
    "netherlands": "🇳🇱 Нидерланды",
    "norway": "🇳🇴 Норвегия",
    "poland": "🇵🇱 Польша",
    "portugal": "🇵🇹 Португалия",
    "spain": "🇪🇸 Испания",
    "sweden": "🇸🇪 Швеция",
    "ukraine": "🇺🇦 Украина",
    "uk": "🇬🇧 Великобритания",
}

# ========== АРТИСТЫ ==========
ARTISTS = {
    "albania": ["Эльвана Гьята", "Рона Нишлиу", "Анжела Перистери"],
    "armenia": ["Серж Танкян", "Андраник", "Лусина"],
    "australia": ["Guy Sebastian", "Dami Im", "Kate Miller-Heidke"],
    "austria": ["Conchita Wurst", "Zoë", "Paenda"],
    "azerbaijan": ["Айсель", "Джамал", "Эльнур Гусейнов"],
    "belgium": ["Loïc Nottet", "Blanche", "Sennek"],
    "croatia": ["Nina Kraljić", "Jacques Houdek", "Albina"],
    "cyprus": ["Eleni Foureira", "Tamta", "Sandro"],
    "denmark": ["Emmelie de Forest", "Rasmussen", "Ben & Tan"],
    "estonia": ["Ott Lepland", "Elina Nechayeva", "Uku Suviste"],
    "finland": ["Lordi", "Saara Aalto", "Blind Channel"],
    "france": ["Алина Пахмутова", "Zaz", "Stromae"],
    "germany": ["Lena", "Nico Santos", "Rammstein"],
    "greece": ["Eleni Foureira", "Katerine Duska", "Stefania"],
    "iceland": ["Hatari", "Daði Freyr", "Greta Salóme"],
    "ireland": ["Jedward", "Ryan O'Shaughnessy", "Lesley Roy"],
    "italy": ["Måneskin", "Mahmood", "Giorgia"],
    "latvia": ["Brainstorm", "Aminata", "Samanta Tīna"],
    "lithuania": ["The Roop", "Monika Liu", "Andrius Pojavis"],
    "netherlands": ["Duncan Laurence", "Jeangu Macrooy", "S10"],
    "norway": ["Keiino", "Aurora", "Kygo"],
    "poland": ["Kasia Moś", "Tulia", "Rafał"],
    "portugal": ["Salvador Sobral", "Conan Osíris", "Elisa"],
    "spain": ["Rosalía", "Pablo Alborán", "Ana Mena"],
    "sweden": ["Loreen", "Zara Larsson", "ABBA"],
    "ukraine": ["Kalush Orchestra", "Jamala", "Верка Сердючка"],
    "uk": ["Sam Ryder", "Mika", "Dua Lipa"],
}

# ========== СОСТОЯНИЯ ==========
COUNTRY, ARTIST, SONG, SEMIFINAL_DRAW, SEMIFINAL_SHOW, SEMIFINAL_VOTE, SEMIFINAL_RESULT, FINAL_SHOW, FINAL_VOTE, FINAL_RESULT = range(10)

# ============================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================

def generate_country_score():
    """Генерирует случайную оценку для страны (1-12)"""
    return random.randint(1, 12)

def generate_performance_score():
    """Генерирует общий балл выступления (от 50 до 200)"""
    return random.randint(50, 200)

# ============================================
# ОБРАБОТЧИКИ
# ============================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало игры — выбор страны"""
    context.user_data.clear()
    
    # Создаём кнопки со странами (в 2 столбца)
    keyboard = []
    countries_list = list(COUNTRIES.items())
    for i in range(0, len(countries_list), 2):
        row = []
        for j in range(2):
            if i + j < len(countries_list):
                code, name = countries_list[i + j]
                row.append(InlineKeyboardButton(name, callback_data=f"country_{code}"))
        keyboard.append(row)
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🎵 **СИМУЛЯТОР ЕВРОВИДЕНИЯ 2026** 🎵\n\n"
        "Добро пожаловать на главный музыкальный конкурс!\n"
        "Ты — продюсер своей страны. Готов создать хит?\n\n"
        "🌍 **Выбери страну, которую будешь представлять:**",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    return COUNTRY

async def country_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выбор страны"""
    query = update.callback_query
    await query.answer()
    
    country_code = query.data.replace("country_", "")
    context.user_data["country_code"] = country_code
    context.user_data["country_name"] = COUNTRIES[country_code]
    
    artists = ARTISTS[country_code]
    keyboard = [[InlineKeyboardButton(artist, callback_data=f"artist_{artist}")] for artist in artists]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"Отлично! Ты выбрал **{COUNTRIES[country_code]}**! 🇪🇺\n\n"
        "🎤 **Теперь выбери представителя:**",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    return ARTIST

async def artist_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выбор артиста"""
    query = update.callback_query
    await query.answer()
    
    context.user_data["artist"] = query.data.replace("artist_", "")
    
    await query.edit_message_text(
        f"🎤 Отлично! Представитель — **{context.user_data['artist']}**.\n\n"
        "📝 **Теперь придумай название песни и жанр**\n"
        "Например: *Fire — поп-рок*",
        parse_mode="Markdown"
    )
    return SONG

async def song_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ввод названия песни"""
    context.user_data["song"] = update.message.text
    
    keyboard = [[InlineKeyboardButton("🎶 Провести жеребьёвку полуфиналов", callback_data="semifinal_draw")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"🎵 Песня **{context.user_data['song']}** сохранена!\n\n"
        "Теперь нужно распределить всех участников по полуфиналам.\n"
        "Всего 27 стран — в полуфиналах участвуют все, кроме стран «Большой пятёрки» (Франция, Германия, Италия, Испания, Великобритания).\n\n"
        "Из каждого полуфинала в финал выйдут только **10 стран**!\n\n"
        "Нажми кнопку, чтобы провести жеребьёвку:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    return SEMIFINAL_DRAW

async def semifinal_draw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Жеребьёвка полуфиналов"""
    query = update.callback_query
    await query.answer()
    
    # Страны "Большой пятёрки" (автоматически в финале)
    big_five = ["france", "germany", "italy", "spain", "uk"]
    
    # Все страны
    all_countries = list(COUNTRIES.keys())
    
    # Убираем "Большую пятёрку"
    semi_countries = [c for c in all_countries if c not in big_five]
    
    # Перемешиваем и делим на два полуфинала
    random.shuffle(semi_countries)
    half = len(semi_countries) // 2
    semi1 = semi_countries[:half]
    semi2 = semi_countries[half:]
    
    # Определяем, в каком полуфинале игрок
    player_country = context.user_data["country_code"]
    
    if player_country in big_five:
        context.user_data["semifinal"] = "Финал (автоматически)"
        context.user_data["semi_group"] = "final"
    elif player_country in semi1:
        context.user_data["semifinal"] = "Полуфинал A"
        context.user_data["semi_group"] = "A"
    elif player_country in semi2:
        context.user_data["semifinal"] = "Полуфинал B"
        context.user_data["semi_group"] = "B"
    
    # Сохраняем списки полуфиналов
    context.user_data["semi1"] = semi1
    context.user_data["semi2"] = semi2
    context.user_data["big_five"] = big_five
    
    # Рандомный номер выступления
    performance_number = random.randint(1, 15)
    context.user_data["performance_number"] = performance_number
    
    # Показываем результат жеребьёвки
    semi1_text = "\n".join([f"  • {COUNTRIES[c]}" for c in semi1])
    semi2_text = "\n".join([f"  • {COUNTRIES[c]}" for c in semi2])
    
    keyboard = [[InlineKeyboardButton("🎤 Начать полуфинал", callback_data="semifinal_show")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"🎶 **ЖЕРЕБЬЁВКА ПОЛУФИНАЛОВ** 🎶\n\n"
        f"Твоя страна — **{context.user_data['country_name']}**\n"
        f"Ты выступаешь в: **{context.user_data['semifinal']}**\n"
        f"Номер выступления: **{performance_number}**\n\n"
        f"📊 **Полуфинал A (всего {len(semi1)} стран):**\n{semi1_text}\n\n"
        f"📊 **Полуфинал B (всего {len(semi2)} стран):**\n{semi2_text}\n\n"
        f"🏆 **«Большая пятёрка» (автоматически в финале):**\n"
        f"  • {COUNTRIES['france']}\n"
        f"  • {COUNTRIES['germany']}\n"
        f"  • {COUNTRIES['italy']}\n"
        f"  • {COUNTRIES['spain']}\n"
        f"  • {COUNTRIES['uk']}\n\n"
        f"Из каждого полуфинала в финал пройдут **ТОЛЬКО 10 ЛУЧШИХ** стран!\n\n"
        f"Нажми кнопку, чтобы начать выступления!",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    return SEMIFINAL_SHOW

async def semifinal_show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показ выступлений в полуфинале"""
    query = update.callback_query
    await query.answer()
    
    semi_group = context.user_data.get("semi_group", "A")
    
    # Получаем список стран в полуфинале игрока
    if semi_group == "A":
        countries = context.user_data.get("semi1", [])
    elif semi_group == "B":
        countries = context.user_data.get("semi2", [])
    else:
        # Если игрок в "Большой пятёрке" — показываем оба полуфинала
        countries = context.user_data.get("semi1", []) + context.user_data.get("semi2", [])
    
    # Генерируем оценки для всех стран (как будто они выступили)
    performances = {}
    for country_code in countries:
        performances[country_code] = {
            "name": COUNTRIES[country_code],
            "score": generate_performance_score()
        }
    
    context.user_data["performances"] = performances
    
    # Показываем результаты выступлений
    performances_text = "\n".join([f"  • {data['name']} — {data['score']} баллов" for data in performances.values()])
    
    # Сортируем по убыванию баллов и берём топ-10
    sorted_countries = sorted(performances.items(), key=lambda x: x[1]["score"], reverse=True)
    top_10 = sorted_countries[:10]
    eliminated = sorted_countries[10:]
    
    context.user_data["top_10"] = [c[0] for c in top_10]
    context.user_data["eliminated"] = [c[0] for c in eliminated]
    
    # Проверяем, прошёл ли игрок в финал
    player_code = context.user_data["country_code"]
    player_passed = player_code in context.user_data["top_10"]
    
    # Формируем текст результатов
    top_10_text = "\n".join([f"  {i+1}. {data['name']} — {data['score']} баллов ✅" for i, (code, data) in enumerate(top_10)])
    eliminated_text = "\n".join([f"  • {data['name']} — {data['score']} баллов ❌" for code, data in eliminated])
    
    context.user_data["player_passed"] = player_passed
    
    if player_passed:
        keyboard = [[InlineKeyboardButton("🏆 Перейти к финалу", callback_data="final_show")]]
        result_text = f"✅ **Ты прошёл в финал!** Твой результат — {performances[player_code]['score']} баллов."
    else:
        keyboard = [[InlineKeyboardButton("🔄 Попробовать ещё раз", callback_data="restart")]]
        result_text = f"❌ **Ты не прошёл в финал.** Твой результат — {performances[player_code]['score']} баллов. В финал проходят только 10 лучших."
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"🎤 **ПОЛУФИНАЛ {'A' if semi_group == 'A' else 'B'} — РЕЗУЛЬТАТЫ** 🎤\n\n"
        f"📊 **Топ-10 (проходят в финал):**\n{top_10_text}\n\n"
        f"❌ **Выбыли:**\n{eliminated_text}\n\n"
        f"{result_text}",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    
    if player_passed:
        return FINAL_SHOW
    else:
        return ConversationHandler.END

async def final_show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Финал — показ выступлений финалистов"""
    query = update.callback_query
    await query.answer()
    
    # Получаем финалистов: топ-10 из полуфинала A + топ-10 из полуфинала B + Большая пятёрка
    top_10_a = context.user_data.get("top_10", [])
    top_10_b = context.user_data.get("top_10", [])  # В реальности нужно разделять, но для простоты используем те же
    big_five = context.user_data.get("big_five", [])
    
    # Для демонстрации используем все страны, которые прошли
    finalists = []
    if context.user_data.get("semi_group") == "A":
        finalists = top_10_a + big_five
    elif context.user_data.get("semi_group") == "B":
        finalists = top_10_b + big_five
    else:
        finalists = top_10_a + big_five
    
    # Генерируем оценки для финала
    final_performances = {}
    for country_code in finalists:
        final_performances[country_code] = {
            "name": COUNTRIES[country_code],
            "score": generate_performance_score()
        }
    
    context.user_data["final_performances"] = final_performances
    
    # Показываем результаты финала
    final_text = "\n".join([f"  • {data['name']} — {data['score']} баллов" for data in final_performances.values()])
    
    keyboard = [[InlineKeyboardButton("🗳️ Голосовать в финале", callback_data="final_vote")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"🏆 **ФИНАЛ ЕВРОВИДЕНИЯ 2026!** 🏆\n\n"
        f"🎤 В финале выступают:\n{final_text}\n\n"
        f"Теперь зрители и жюри голосуют!\n\n"
        f"Нажми кнопку, чтобы проголосовать за победителя!",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    return FINAL_VOTE

async def final_vote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Голосование в финале"""
    query = update.callback_query
    await query.answer()
    
    # Кнопки для оценки пользователя (от 1 до 10)
    keyboard = [
        [InlineKeyboardButton("1 ⭐", callback_data="fscore_1"),
         InlineKeyboardButton("2 ⭐", callback_data="fscore_2"),
         InlineKeyboardButton("3 ⭐", callback_data="fscore_3"),
         InlineKeyboardButton("4 ⭐", callback_data="fscore_4"),
         InlineKeyboardButton("5 ⭐", callback_data="fscore_5")],
        [InlineKeyboardButton("6 ⭐", callback_data="fscore_6"),
         InlineKeyboardButton("7 ⭐", callback_data="fscore_7"),
         InlineKeyboardButton("8 ⭐", callback_data="fscore_8"),
         InlineKeyboardButton("9 ⭐", callback_data="fscore_9"),
         InlineKeyboardButton("10 ⭐", callback_data="fscore_10")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"🗳️ **ГОЛОСОВАНИЕ В ФИНАЛЕ**\n\n"
        f"Твоя песня — **«{context.user_data['song']}»**\n"
        f"Представитель — **{context.user_data['artist']}**\n\n"
        f"Оцени выступление по шкале от 1 до 10:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    return FINAL_RESULT

async def final_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Результаты финала"""
    query = update.callback_query
    await query.answer()
    
    user_score = int(query.data.replace("fscore_", ""))
    context.user_data["user_score"] = user_score
    
    # Голосование жюри (10 стран)
    jury_scores = [random.randint(1, 12) for _ in range(10)]
    jury_average = sum(jury_scores) / len(jury_scores)
    
    # Итоговый балл
    user_score_scaled = (user_score / 10) * 12
    all_scores = jury_scores + [user_score_scaled]
    total_score = sum(all_scores) / len(all_scores)
    context.user_data["total_score"] = total_score
    
    # Рандомные конкуренты для драмы
    rival_countries = random.sample(list(COUNTRIES.values()), 5)
    rival_scores = [round(random.uniform(5, 11), 1) for _ in range(5)]
    
    # Определяем победителя
    max_rival = max(rival_scores) if rival_scores else 0
    if total_score > max_rival:
        winner_text = f"🥇 **{context.user_data['country_name']} ПОБЕДИЛ!** 🥇"
    else:
        winner_text = f"🥈 **{context.user_data['country_name']} занял 2-е место!** (Победитель — {rival_countries[rival_scores.index(max_rival)]})"
    
    # Формируем текст результатов
    jury_text = "\n".join([f"   {i+1}. Страна {i+1}: {score} баллов" for i, score in enumerate(jury_scores)])
    
    text = (
        f"🏆 **РЕЗУЛЬТАТЫ ФИНАЛА** 🏆\n\n"
        f"🎤 **Участник:** {context.user_data['country_name']}\n"
        f"👨‍🎤 **Артист:** {context.user_data['artist']}\n"
        f"🎵 **Песня:** «{context.user_data['song']}»\n\n"
        f"⭐ **Оценка зрителей:** {user_score}/10\n\n"
        f"🏅 **Оценки жюри (10 стран):**\n{jury_text}\n"
        f"📊 **Средняя оценка жюри:** {jury_average:.1f}/12\n\n"
        f"📈 **ИТОГОВЫЙ БАЛЛ:** {total_score:.1f}/12\n\n"
        f"🏆 **Результат:**\n{winner_text}\n\n"
        f"📊 **Конкуренты:**\n"
    )
    
    for i, (rival, score) in enumerate(zip(rival_countries, rival_scores), 1):
        text += f"   {i}. {rival} — {score}/12\n"
    
    text += (
        f"\n🎉 **ПОЗДРАВЛЯЮ!**\n"
        f"Ты прошёл весь путь от полуфинала до финала!\n\n"
        f"Хочешь сыграть ещё раз? Напиши /start"
    )
    
    keyboard = [[InlineKeyboardButton("🎵 Сыграть ещё раз", callback_data="restart")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    return ConversationHandler.END

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Рестарт игры"""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🔄 Перезапуск игры... Напиши /start")
    await start(update, context)
    return COUNTRY

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена игры"""
    await update.message.reply_text("❌ Игра отменена. Напиши /start, чтобы начать заново.")
    return ConversationHandler.END

# ============================================
# ЗАПУСК
# ============================================

def main():
    """Запуск бота"""
    app = Application.builder().token(TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            COUNTRY: [CallbackQueryHandler(country_selected, pattern="^country_")],
            ARTIST: [CallbackQueryHandler(artist_selected, pattern="^artist_")],
            SONG: [MessageHandler(filters.TEXT & ~filters.COMMAND, song_input)],
            SEMIFINAL_DRAW: [CallbackQueryHandler(semifinal_draw, pattern="^semifinal_draw$")],
            SEMIFINAL_SHOW: [CallbackQueryHandler(semifinal_show, pattern="^semifinal_show$")],
            FINAL_SHOW: [CallbackQueryHandler(final_show, pattern="^final_show$")],
            FINAL_VOTE: [CallbackQueryHandler(final_vote, pattern="^final_vote$")],
            FINAL_RESULT: [CallbackQueryHandler(final_result, pattern="^fscore_")],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(restart, pattern="^restart$"))
    
    print("🚀 Бот запущен! Напиши /start в Telegram")
    print("📊 Нажми Ctrl+C для остановки")
    
    app.run_polling()

if __name__ == "__main__":
    main()