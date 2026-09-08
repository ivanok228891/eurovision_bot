import asyncio
import logging
import random
import os
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler, ContextTypes

# ========== НАСТРОЙКИ ==========
TOKEN = os.environ.get('TELEGRAM_TOKEN')
if not TOKEN:
    raise ValueError("❌ Токен не найден! Установи переменную TELEGRAM_TOKEN в Render")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========== ВСЕ СТРАНЫ ==========
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

# ========== КРУТЫЕ АРТИСТЫ ==========
ARTISTS = {
    "albania": ["🎤 Эльвана Гьята", "🎤 Рона Нишлиу", "🎤 Анжела Перистери"],
    "armenia": ["🎤 Серж Танкян", "🎤 Андраник", "🎤 Лусина"],
    "australia": ["🎤 Guy Sebastian", "🎤 Dami Im", "🎤 Kate Miller-Heidke"],
    "austria": ["🎤 Conchita Wurst", "🎤 Zoë", "🎤 Paenda"],
    "azerbaijan": ["🎤 Айсель", "🎤 Джамал", "🎤 Эльнур Гусейнов"],
    "belgium": ["🎤 Loïc Nottet", "🎤 Blanche", "🎤 Sennek"],
    "croatia": ["🎤 Nina Kraljić", "🎤 Jacques Houdek", "🎤 Albina"],
    "cyprus": ["🎤 Eleni Foureira", "🎤 Tamta", "🎤 Sandro"],
    "denmark": ["🎤 Emmelie de Forest", "🎤 Rasmussen", "🎤 Ben & Tan"],
    "estonia": ["🎤 Ott Lepland", "🎤 Elina Nechayeva", "🎤 Uku Suviste"],
    "finland": ["🎤 Lordi", "🎤 Saara Aalto", "🎤 Blind Channel"],
    "france": ["🎤 Алина Пахмутова", "🎤 Zaz", "🎤 Stromae"],
    "germany": ["🎤 Lena", "🎤 Nico Santos", "🎤 Rammstein"],
    "greece": ["🎤 Eleni Foureira", "🎤 Katerine Duska", "🎤 Stefania"],
    "iceland": ["🎤 Hatari", "🎤 Daði Freyr", "🎤 Greta Salóme"],
    "ireland": ["🎤 Jedward", "🎤 Ryan O'Shaughnessy", "🎤 Lesley Roy"],
    "italy": ["🎤 Måneskin", "🎤 Mahmood", "🎤 Giorgia"],
    "latvia": ["🎤 Brainstorm", "🎤 Aminata", "🎤 Samanta Tīna"],
    "lithuania": ["🎤 The Roop", "🎤 Monika Liu", "🎤 Andrius Pojavis"],
    "netherlands": ["🎤 Duncan Laurence", "🎤 Jeangu Macrooy", "🎤 S10"],
    "norway": ["🎤 Keiino", "🎤 Aurora", "🎤 Kygo"],
    "poland": ["🎤 Kasia Moś", "🎤 Tulia", "🎤 Rafał"],
    "portugal": ["🎤 Salvador Sobral", "🎤 Conan Osíris", "🎤 Elisa"],
    "spain": ["🎤 Rosalía", "🎤 Pablo Alborán", "🎤 Ana Mena"],
    "sweden": ["🎤 Loreen", "🎤 Zara Larsson", "🎤 ABBA"],
    "ukraine": ["🎤 Kalush Orchestra", "🎤 Jamala", "🎤 Верка Сердючка"],
    "uk": ["🎤 Sam Ryder", "🎤 Mika", "🎤 Dua Lipa"],
}

# ========== СЦЕНАРИИ ФИНАЛА ==========
FINAL_SCENARIOS = [
    {
        "name": "🔥 Эпичный рок-финал",
        "description": "Гитары, дым, свет — все взрывается!",
        "bonus": 20
    },
    {
        "name": "💃 Танцевальный марафон",
        "description": "Ритм заставляет всех танцевать!",
        "bonus": 15
    },
    {
        "name": "🎭 Драматичная баллада",
        "description": "Слёзы зрителей и овации!",
        "bonus": 25
    },
    {
        "name": "🚀 Космическое шоу",
        "description": "Лазеры, проекции и невесомость!",
        "bonus": 30
    },
    {
        "name": "🎪 Цирковое представление",
        "description": "Акробаты, огонь и магия!",
        "bonus": 18
    }
]

# ========== ДОПОЛНИТЕЛЬНЫЕ ЭЛЕМЕНТЫ ==========
PROPS = [
    "🔥 Пиротехника",
    "✨ Дымовая завеса",
    "🎆 Фейерверк",
    "💡 Световое шоу",
    "🎭 Театральные маски",
    "🌊 Водные эффекты",
    "🎈 Воздушные шары",
    "⚡ Спецэффекты молний"
]

# ========== СОСТОЯНИЯ ==========
COUNTRY, ARTIST, SONG, SCENARIO, SEMIFINAL_DRAW, SEMIFINAL_SHOW, FINAL_SHOW, FINAL_VOTE, FINAL_RESULT, PROPS_SELECT = range(10)

# ============================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================

def generate_performance_score():
    return random.randint(50, 200)

def generate_jury_score():
    return random.randint(1, 12)

def get_random_props():
    return random.sample(PROPS, random.randint(1, 4))

def get_scenario_bonus(scenario_name):
    for s in FINAL_SCENARIOS:
        if s["name"] == scenario_name:
            return s["bonus"]
    return 0

# ============================================
# ГЛАВНЫЕ ФУНКЦИИ
# ============================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🎯 СТАРТ — выбор страны"""
    context.user_data.clear()
    
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
        "🎵 **СИМУЛЯТОР ЕВРОВИДЕНИЯ 2026 — МЕГА-ВЕРСИЯ!** 🎵\n\n"
        "🌟 **Добро пожаловать в самое крутое музыкальное шоу!**\n"
        "Ты — продюсер своей страны. Создай незабываемое выступление!\n\n"
        "🏆 **Что тебя ждет:**\n"
        "✅ Выбор страны и артиста\n"
        "✅ Создание песни с нуля\n"
        "🔥 Выбор эпичного сценария финала\n"
        "💥 Спецэффекты и пиротехника\n"
        "🎯 Голосование жюри и зрителей\n"
        "🏆 Грандиозный финал!\n\n"
        "🌍 **Выбери свою страну:**",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    return COUNTRY

async def country_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🌍 Выбор страны"""
    query = update.callback_query
    await query.answer()
    
    country_code = query.data.replace("country_", "")
    context.user_data["country_code"] = country_code
    context.user_data["country_name"] = COUNTRIES[country_code]
    
    artists = ARTISTS[country_code]
    keyboard = [[InlineKeyboardButton(artist, callback_data=f"artist_{artist}")] for artist in artists]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"🇪🇺 Отлично! Ты представляешь **{COUNTRIES[country_code]}**!\n\n"
        "🎤 **Теперь выбери артиста, который будет представлять страну:**",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    return ARTIST

async def artist_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🎤 Выбор артиста"""
    query = update.callback_query
    await query.answer()
    
    context.user_data["artist"] = query.data.replace("artist_", "")
    
    await query.edit_message_text(
        f"👨‍🎤 Отлично! Артист **{context.user_data['artist']}** готов!\n\n"
        "📝 **Придумай название песни и жанр**\n"
        "Например: *«Fire» — поп-рок*\n"
        "Или: *«Любовь и небо» — баллада*\n\n"
        "✍️ Напиши название своей песни:",
        parse_mode="Markdown"
    )
    return SONG

async def song_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🎵 Ввод песни"""
    context.user_data["song"] = update.message.text
    
    # Показываем сценарии финала
    keyboard = []
    for scenario in FINAL_SCENARIOS:
        keyboard.append([InlineKeyboardButton(
            f"🎬 {scenario['name']} (+{scenario['bonus']} баллов)", 
            callback_data=f"scenario_{scenario['name']}"
        )])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"🎵 **Песня «{context.user_data['song']}» сохранена!**\n\n"
        "🎬 **Теперь выбери СЦЕНАРИЙ для твоего финального выступления!**\n"
        "От этого зависит, как пройдет твой номер!\n\n"
        "🔥 Чем круче сценарий — тем больше бонусных баллов!",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    return SCENARIO

async def scenario_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🎬 Выбор сценария"""
    query = update.callback_query
    await query.answer()
    
    scenario_name = query.data.replace("scenario_", "")
    context.user_data["scenario"] = scenario_name
    bonus = get_scenario_bonus(scenario_name)
    context.user_data["scenario_bonus"] = bonus
    
    # Выбор спецэффектов
    keyboard = []
    for prop in PROPS[:6]:  # Показываем 6 случайных
        keyboard.append([InlineKeyboardButton(f"💥 {prop}", callback_data=f"prop_{prop}")])
    keyboard.append([InlineKeyboardButton("✅ Без спецэффектов", callback_data="prop_none")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"🎬 **Выбран сценарий: {scenario_name}**\n"
        f"⚡ **Бонус к баллам: +{bonus}**\n\n"
        "💥 **Теперь выбери спецэффекты для выступления!**\n"
        "(Можно выбрать несколько)",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    return PROPS_SELECT

async def props_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """💥 Выбор спецэффектов"""
    query = update.callback_query
    await query.answer()
    
    prop = query.data.replace("prop_", "")
    
    if prop == "none":
        context.user_data["props"] = []
    else:
        if "props" not in context.user_data:
            context.user_data["props"] = []
        if prop not in context.user_data["props"]:
            context.user_data["props"].append(prop)
    
    # Показываем выбранные эффекты
    props_text = "\n".join([f"💥 {p}" for p in context.user_data.get("props", [])]) if context.user_data.get("props") else "❌ Без спецэффектов"
    
    keyboard = [
        [InlineKeyboardButton("🎶 Перейти к жеребьевке!", callback_data="semifinal_draw")],
        [InlineKeyboardButton("🔄 Добавить еще эффект", callback_data="add_more_props")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"💥 **Спецэффекты выбраны:**\n{props_text}\n\n"
        "🎶 **Теперь проведем жеребьевку полуфиналов!**\n"
        "Нажми кнопку ниже, чтобы узнать, с кем ты будешь соревноваться.",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    return SEMIFINAL_DRAW

async def add_more_props(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🔄 Добавить еще эффекты"""
    query = update.callback_query
    await query.answer()
    
    keyboard = []
    for prop in PROPS:
        if prop not in context.user_data.get("props", []):
            keyboard.append([InlineKeyboardButton(f"💥 {prop}", callback_data=f"prop_{prop}")])
    keyboard.append([InlineKeyboardButton("✅ Готово!", callback_data="props_done")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "💥 **Выбери дополнительные спецэффекты:**",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    return PROPS_SELECT

async def props_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """✅ Завершение выбора эффектов"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [[InlineKeyboardButton("🎶 Провести жеребьевку!", callback_data="semifinal_draw")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    props_text = "\n".join([f"💥 {p}" for p in context.user_data.get("props", [])]) if context.user_data.get("props") else "❌ Без спецэффектов"
    
    await query.edit_message_text(
        f"💥 **Итоговые спецэффекты:**\n{props_text}\n\n"
        "🎶 **Теперь проведем жеребьевку полуфиналов!**\n"
        "Нажми кнопку ниже:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    return SEMIFINAL_DRAW

async def semifinal_draw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🎶 Жеребьевка полуфиналов"""
    query = update.callback_query
    await query.answer()
    
    big_five = ["france", "germany", "italy", "spain", "uk"]
    all_countries = list(COUNTRIES.keys())
    semi_countries = [c for c in all_countries if c not in big_five]
    
    random.shuffle(semi_countries)
    half = len(semi_countries) // 2
    semi1 = semi_countries[:half]
    semi2 = semi_countries[half:]
    
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
    
    context.user_data["semi1"] = semi1
    context.user_data["semi2"] = semi2
    context.user_data["big_five"] = big_five
    
    performance_number = random.randint(1, 15)
    context.user_data["performance_number"] = performance_number
    
    semi1_text = "\n".join([f"  • {COUNTRIES[c]}" for c in semi1])
    semi2_text = "\n".join([f"  • {COUNTRIES[c]}" for c in semi2])
    
    keyboard = [[InlineKeyboardButton("🎤 Начать полуфинал!", callback_data="semifinal_show")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"🎶 **ЖЕРЕБЬЕВКА ПОЛУФИНАЛОВ** 🎶\n\n"
        f"🇪🇺 Твоя страна — **{context.user_data['country_name']}**\n"
        f"🎭 Ты выступаешь в: **{context.user_data['semifinal']}**\n"
        f"🔢 Номер выступления: **{performance_number}**\n\n"
        f"📊 **Полуфинал A ({len(semi1)} стран):**\n{semi1_text}\n\n"
        f"📊 **Полуфинал B ({len(semi2)} стран):**\n{semi2_text}\n\n"
        f"🏆 **«Большая пятерка» (в финале):**\n"
        f"  • {COUNTRIES['france']}\n"
        f"  • {COUNTRIES['germany']}\n"
        f"  • {COUNTRIES['italy']}\n"
        f"  • {COUNTRIES['spain']}\n"
        f"  • {COUNTRIES['uk']}\n\n"
        f"🎯 **В финал проходят только 10 стран из каждого полуфинала!**\n\n"
        f"🔥 Готов? Начинаем!",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    return SEMIFINAL_SHOW

async def semifinal_show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🎤 Полуфинал — выступления"""
    query = update.callback_query
    await query.answer()
    
    semi_group = context.user_data.get("semi_group", "A")
    
    if semi_group == "A":
        countries = context.user_data.get("semi1", [])
    elif semi_group == "B":
        countries = context.user_data.get("semi2", [])
    else:
        countries = context.user_data.get("semi1", []) + context.user_data.get("semi2", [])
    
    performances = {}
    for country_code in countries:
        performances[country_code] = {
            "name": COUNTRIES[country_code],
            "score": generate_performance_score()
        }
    
    context.user_data["performances"] = performances
    
    sorted_countries = sorted(performances.items(), key=lambda x: x[1]["score"], reverse=True)
    top_10 = sorted_countries[:10]
    eliminated = sorted_countries[10:]
    
    context.user_data["top_10"] = [c[0] for c in top_10]
    context.user_data["eliminated"] = [c[0] for c in eliminated]
    
    player_code = context.user_data["country_code"]
    player_passed = player_code in context.user_data["top_10"]
    
    top_10_text = "\n".join([f"  {i+1}. {data['name']} — {data['score']} баллов ✅" for i, (code, data) in enumerate(top_10)])
    eliminated_text = "\n".join([f"  • {data['name']} — {data['score']} баллов ❌" for code, data in eliminated])
    
    context.user_data["player_passed"] = player_passed
    
    if player_passed:
        keyboard = [[InlineKeyboardButton("🏆 ПЕРЕЙТИ В ФИНАЛ!", callback_data="final_show")]]
        result_text = f"🎉 **ТЫ ПРОШЕЛ В ФИНАЛ!** 🎉\nТвой результат — {performances[player_code]['score']} баллов!"
    else:
        keyboard = [[InlineKeyboardButton("🔄 Попробовать еще раз", callback_data="restart")]]
        result_text = f"😢 **Ты не прошел в финал.**\nТвой результат — {performances[player_code]['score']} баллов.\nВ финал проходят только 10 лучших."
    
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
    """🏆 Финал — грандиозное шоу"""
    query = update.callback_query
    await query.answer()
    
    top_10 = context.user_data.get("top_10", [])
    big_five = context.user_data.get("big_five", [])
    finalists = list(set(top_10 + big_five))
    
    # Добавляем бонус от сценария
    scenario_bonus = context.user_data.get("scenario_bonus", 0)
    props_count = len(context.user_data.get("props", []))
    props_bonus = props_count * 5
    
    final_performances = {}
    for country_code in finalists:
        score = generate_performance_score()
        if country_code == context.user_data["country_code"]:
            score += scenario_bonus + props_bonus  # Бонус игроку!
        final_performances[country_code] = {
            "name": COUNTRIES[country_code],
            "score": score
        }
    
    context.user_data["final_performances"] = final_performances
    
    final_text = "\n".join([f"  • {data['name']} — {data['score']} баллов" + (" ⭐" if data['name'] == context.user_data['country_name'] else "") for data in final_performances.values()])
    
    # Показываем бонусы игрока
    bonus_text = f"🔥 **Бонусы игрока:**\n"
    bonus_text += f"🎬 Сценарий: +{scenario_bonus}\n"
    bonus_text += f"💥 Спецэффекты ({props_count} шт): +{props_bonus}\n"
    bonus_text += f"📊 Итого бонусов: +{scenario_bonus + props_bonus}\n\n"
    
    keyboard = [[InlineKeyboardButton("🗳️ ГОЛОСОВАТЬ!", callback_data="final_vote")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"🏆 **ГРАНДИОЗНЫЙ ФИНАЛ ЕВРОВИДЕНИЯ 2026!** 🏆\n\n"
        f"🎤 **Выступление твоего артиста:**\n"
        f"👨‍🎤 {context.user_data['artist']}\n"
        f"🎵 «{context.user_data['song']}»\n"
        f"🎬 Сценарий: {context.user_data.get('scenario', 'Классический')}\n\n"
        f"{bonus_text}"
        f"🎶 **Результаты финала:**\n{final_text}\n\n"
        f"⚡ **Нажми кнопку, чтобы проголосовать!**",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    return FINAL_VOTE

async def final_vote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🗳️ Голосование в финале"""
    query = update.callback_query
    await query.answer()
    
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
        f"🗳️ **ГОЛОСОВАНИЕ В ФИНАЛЕ!** 🗳️\n\n"
        f"🎤 Твоя песня — **«{context.user_data['song']}»**\n"
        f"👨‍🎤 Артист — **{context.user_data['artist']}**\n\n"
        f"⭐ **Оцени выступление от 1 до 10:**",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    return FINAL_RESULT

async def final_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🏆 Итоговые результаты"""
    query = update.callback_query
    await query.answer()
    
    user_score = int(query.data.replace("fscore_", ""))
    context.user_data["user_score"] = user_score
    
    # Голоса жюри (10 стран)
    jury_scores = [generate_jury_score() for _ in range(10)]
    jury_average = sum(jury_scores) / len(jury_scores)
    
    # Итоговый балл
    user_score_scaled = (user_score / 10) * 12
    total_score = (jury_average + user_score_scaled + context.user_data.get("scenario_bonus", 0) + len(context.user_data.get("props", [])) * 5) / 3
    context.user_data["total_score"] = round(total_score, 1)
    
    # Конкуренты
    rival_countries = random.sample(list(COUNTRIES.values()), 5)
    rival_scores = [round(random.uniform(5, 11), 1) for _ in range(5)]
    
    max_rival = max(rival_scores) if rival_scores else 0
    if total_score > max_rival:
        winner_text = f"🥇 **{context.user_data['country_name']} — ПОБЕДИТЕЛЬ ЕВРОВИДЕНИЯ 2026!** 🥇"
    elif total_score == max_rival:
        winner_text = f"🤝 **Ничья!** {context.user_data['country_name']} и {rival_countries[rival_scores.index(max_rival)]} — разделяют победу!"
    else:
        winner_text = f"🥈 **{context.user_data['country_name']} занял 2-е место!**\n🥇 Победитель — {rival_countries[rival_scores.index(max_rival)]}"
    
    jury_text = "\n".join([f"   {i+1}. Страна {i+1}: {score}/12" for i, score in enumerate(jury_scores)])
    
    text = (
        f"🏆 **ИТОГИ ЕВРОВИДЕНИЯ 2026** 🏆\n\n"
        f"🎤 **Участник:** {context.user_data['country_name']}\n"
        f"👨‍🎤 **Артист:** {context.user_data['artist']}\n"
        f"🎵 **Песня:** «{context.user_data['song']}»\n"
        f"🎬 **Сценарий:** {context.user_data.get('scenario', 'Классический')}\n\n"
        f"⭐ **Оценка зрителей:** {user_score}/10\n"
        f"🏅 **Оценки жюри (10 стран):**\n{jury_text}\n"
        f"📊 **Средняя оценка жюри:** {jury_average:.1f}/12\n\n"
        f"🔥 **Бонусы:**\n"
        f"  • Сценарий: +{context.user_data.get('scenario_bonus', 0)}\n"
        f"  • Спецэффекты: +{len(context.user_data.get('props', [])) * 5}\n\n"
        f"📈 **ИТОГОВЫЙ БАЛЛ:** {total_score:.1f}/12\n\n"
        f"🏆 **Результат:**\n{winner_text}\n\n"
        f"📊 **Конкуренты:**\n"
    )
    
    for i, (rival, score) in enumerate(zip(rival_countries, rival_scores), 1):
        text += f"   {i}. {rival} — {score}/12\n"
    
    text += (
        f"\n🎉 **ПОЗДРАВЛЯЮ С ПРОХОЖДЕНИЕМ ИГРЫ!** 🎉\n"
        f"Ты создал легендарное выступление!\n\n"
        f"🔄 Напиши /start, чтобы сыграть снова!"
    )
    
    keyboard = [[InlineKeyboardButton("🎵 Сыграть снова!", callback_data="restart")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    return ConversationHandler.END

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🔄 Рестарт"""
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("🔄 Перезапуск... Напиши /start")
    await start(update, context)
    return COUNTRY

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """❌ Отмена"""
    await update.message.reply_text("❌ Игра отменена. Напиши /start, чтобы начать заново!")
    return ConversationHandler.END

# ============================================
# ЗАПУСК
# ============================================

def main():
    app = Application.builder().token(TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            COUNTRY: [CallbackQueryHandler(country_selected, pattern="^country_")],
            ARTIST: [CallbackQueryHandler(artist_selected, pattern="^artist_")],
            SONG: [MessageHandler(filters.TEXT & ~filters.COMMAND, song_input)],
            SCENARIO: [CallbackQueryHandler(scenario_selected, pattern="^scenario_")],
            PROPS_SELECT: [
                CallbackQueryHandler(props_selected, pattern="^prop_"),
                CallbackQueryHandler(add_more_props, pattern="^add_more_props$"),
                CallbackQueryHandler(props_done, pattern="^props_done$")
            ],
            SEMIFINAL_DRAW: [CallbackQueryHandler(semifinal_draw, pattern="^semifinal_draw$")],
            SEMIFINAL_SHOW: [CallbackQueryHandler(semifinal_show, pattern="^semifinal_show$")],
            FINAL_SHOW: [CallbackQueryHandler(final_show, pattern="^final_show$")],
            FINAL_VOTE: [CallbackQueryHandler(final_vote, pattern="^final_vote$")],
            FINAL_RESULT: [CallbackQueryHandler(final_result, pattern="^fscore_")],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        per_message=True
    )
    
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(restart, pattern="^restart$"))
    app.add_handler(CallbackQueryHandler(semifinal_draw, pattern="^semifinal_draw$"))
    
    print("🚀 МЕГА-БОТ ЗАПУЩЕН!")
    print("🌟 Евровидение 2026 — ИМБОВАЯ ВЕРСИЯ!")
    print("📊 Напиши /start в Telegram")
    
    try:
        app.run_polling()
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main()
