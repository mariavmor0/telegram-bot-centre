import os
import asyncio
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ConversationHandler, ContextTypes
)
from contextlib import asynccontextmanager

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Публичный HTTPS URL сервера
PHOTO_FILE_ID = "AgACAgIAAxkBAANnaHkYnDmUfqRoOjvW0T3Sp1zyobQAArD8MRsj28lLUn3jra_zLg4BAAMCAAN5AAM2BA"

ASK_VOLUME, ASK_SEASON, ASK_USAGE, ASK_BATH_TYPE, ASK_LAYOUT = range(5)
recommendations = []

welcome_text = (
    "Здравствуй, дорогой покупатель! На связи Оля, руководитель розничного отдела ООО «ТПК Центр тепла»\n\n"
    "Этот бот не заменит очной консультации в нашем магазине, но точно поможет понять, какая печь подойдёт именно вам.\n"
    "После прохождения опроса вас ждёт не только идеальная подборка печей по вашему запросу, но и небольшой сюрприз!"
)

async def lifespan(app: FastAPI):
    print("FastAPI запускается...")
    yield
    print("FastAPI завершает работу...")

app = FastAPI(lifespan=lifespan)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    recommendations.clear()
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Начать подбор!", callback_data="start_survey")]
    ])
    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=PHOTO_FILE_ID,
        caption=welcome_text,
        reply_markup=keyboard
    )
    return ASK_VOLUME

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    recommendations.clear()
    text = "1. Укажите объем вашей парной:"
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("До 10 м³", callback_data='volume_a')],
        [InlineKeyboardButton("11-15 м³", callback_data='volume_b')],
        [InlineKeyboardButton("15-20 м³", callback_data='volume_c')],
        [InlineKeyboardButton("До 24 м³", callback_data='volume_d')],
    ])
    await update.message.reply_text("Давайте начнем заново!\n\n" + text, reply_markup=keyboard)
    return ASK_VOLUME

async def message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Связаться с менеджером", url='https://t.me/Pechi_ct_nsk')]
    ])
    await update.message.reply_text(
        "Если у вас есть вопросы или хотите уточнить детали — свяжитесь с нашим менеджером.",
        reply_markup=keyboard
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "start_survey":
        question = "1. Укажите объем вашей парной:"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("До 10 м³", callback_data='volume_a')],
            [InlineKeyboardButton("11-15 м³", callback_data='volume_b')],
            [InlineKeyboardButton("15-20 м³", callback_data='volume_c')],
            [InlineKeyboardButton("До 24 м³", callback_data='volume_d')],
        ])
        await query.message.reply_text(text=question, reply_markup=keyboard)
        return ASK_VOLUME

    elif data.startswith("volume_"):
        context.user_data["volume"] = data
        question = "2. Уточните сезон использования бани:"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Только в тёплое время года", callback_data='season_a')],
            [InlineKeyboardButton("Круглогодичное использование", callback_data='season_b')],
        ])
        await query.message.reply_text(text=question, reply_markup=keyboard)
        return ASK_SEASON

    elif data.startswith("season_"):
        context.user_data["season"] = data
        question = "3. Какую основную функцию выполняет баня?"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Моечная", callback_data='usage_a')],
            [InlineKeyboardButton("Парная", callback_data='usage_b')],
        ])
        await query.message.reply_text(text=question, reply_markup=keyboard)
        return ASK_USAGE

    elif data.startswith("usage_"):
        context.user_data["usage"] = data
        question = "4. Какой тип пара вы предпочитаете?"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Сухой пар", callback_data='bath_a')],
            [InlineKeyboardButton("Влажный пар", callback_data='bath_b')],
            [InlineKeyboardButton("Компромисс между ними", callback_data='bath_c')],
        ])
        await query.message.reply_text(text=question, reply_markup=keyboard)
        return ASK_BATH_TYPE

    elif data.startswith("bath_"):
        context.user_data["bath_type"] = data
        question = "5. Какая у вас планировка бани?"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Топочная отдельно, моечная и парная вместе", callback_data='layout_a')],
            [InlineKeyboardButton("Все находится в одной комнате", callback_data='layout_b')],
            [InlineKeyboardButton("Все находится в разных комнатах", callback_data='layout_c')],
        ])
        await query.message.reply_text(text=question, reply_markup=keyboard)
        return ASK_LAYOUT


    elif data.startswith("layout_"):
        context.user_data["layout"] = data
        await send_results(update, context)  # <-- передаём Update
        return ConversationHandler.END


async def send_results(update: Update, context: ContextTypes.DEFAULT_TYPE):
    answers = context.user_data

    volume_map = {
        "volume_a": "До 10 м³",
        "volume_b": "11-15 м³",
        "volume_c": "15-20 м³",
        "volume_d": "До 24 м³"
    }
    season_map = {
        "season_a": "Только в тёплое время года",
        "season_b": "Круглогодичное использование"
    }
    usage_map = {
        "usage_a": "Моечная",
        "usage_b": "Парная"
    }
    bath_map = {
        "bath_a": "Сухой пар",
        "bath_b": "Влажный пар",
        "bath_c": "Компромисс между ними"
    }
    layout_map = {
        "layout_a": "Топочная отдельно, моечная и парная вместе",
        "layout_b": "Все находится в одной комнате",
        "layout_c": "Все находится в разных комнатах"
    }

    result_text = (
        "Спасибо за ответы! Вот ваш выбор:\n\n"
        f"🔹 Объём парной: {volume_map.get(answers.get('volume'))}\n"
        f"🔹 Сезон использования: {season_map.get(answers.get('season'))}\n"
        f"🔹 Использование: {usage_map.get(answers.get('usage'))}\n"
        f"🔹 Тип пара: {bath_map.get(answers.get('bath_type'))}\n"
        f"🔹 Планировка: {layout_map.get(answers.get('layout'))}\n\n"
        "Скоро пришлю вам подходящие модели и бонус 🎁"
    )

    await update.effective_message.reply_text(result_text)
    await send_recommendation(update, context)


async def send_recommendation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_data = context.user_data

    volume = user_data.get("volume")
    season = user_data.get("season")
    usage = user_data.get("usage")
    bath_type = user_data.get("bath_type")
    layout = user_data.get("layout")

    recommendation_sent = False

    if (
        volume == "volume_a" and
        season == "season_a" and
        usage == "usage_a" and
        bath_type in ["bath_a", "bath_c"] and
        layout == "layout_b"
    ):
        recommendation_sent = True
        photo_id = "AgACAgIAAxkBAAO4aH4g-S4hgwSlr1U_S59Avl8U66sAAs7uMRvqVPlLkzueBs6fjVEBAAMCAAN5AAM2BA"
        caption = '''Банная печь «Огонь» - идеальный вариант для вашей парной!

Печи этой серии отличаются простотой и надежностью. Верхняя и нижняя плиты имеют гибы, которые улучшают нагрев и защищают от перегрева.

Можно докомплектовать каменками, баками или кожухами.'''
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Печь банная «Огонь»",
                                  url="https://www.center-tepla.ru/catalog/pechi_dlya_bani/pechi_dlya_bani_standart/pech_bannaya_ogon_12_kub_m_md/")]
        ])
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=photo_id,
            caption=caption,
            reply_markup=keyboard
        )
    if (
            volume == "volume_a" and
            season == "season_a" and
            usage == "usage_a" and
            bath_type in ["bath_a", "bath_c"] and
            layout in ["layout_a", "layout_b", "layout_c"]
    ):
        recommendation_sent = True
        photo_id = "AgACAgIAAxkBAAP8aH-EQteieHzKms5xkdUV1idLH7UAAiD4MRuuC_hLkHYjPa0g5akBAAMCAAN4AAM2BA"
        caption = '''Банная печь «Огонь» с аркой и тоннелем — прочная, надёжная и удобная!

Печи этой серии отличаются простотой и надежностью. Печь имеет минимум сварных швов, что говорит о её качестве. 

Верхняя и нижняя плиты имеют гибы. На верхней плите они служат, как ребра жесткости и улучшают нагрев камней. На нижней плите служат, как ребра жесткости и не позволяют углям гореть рядом с боковыми стенками, это предотвращает их перегрев, позволяя углям находиться рядом с колосником, что обеспечивает лучшее горение. 

Также печи серии «Огонь» можно докомплектовать навесными сетками-каменками, навесными баками для воды или конвекционными кожухами.'''
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Печь банная «Огонь» с аркой",
                                  url="https://www.center-tepla.ru/catalog/pechi_dlya_bani/pechi_dlya_bani_standart/pech_bannaya_ogon_s_arkoy_12_kub_m_md/")],
            [InlineKeyboardButton("Печь банная «Огонь» с тоннелем",
                                  url="https://www.center-tepla.ru/catalog/pechi_dlya_bani/pechi_dlya_bani_standart/pech_bannaya_ogon_12_kub_m_md_tonnel/")]
        ])
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=photo_id,
            caption=caption,
            reply_markup=keyboard
        )

    if (
            volume in ["volume_b", "volume_c"] and
            (
                    (season == "season_a") or
                    (season == "season_b" and volume == "volume_b")
            ) and
            usage == "usage_a" and
            bath_type in ["bath_a", "bath_c"] and
            layout in ["layout_a", "layout_c"]
    ):
        recommendation_sent = True
        photo_id = "AgACAgIAAxkBAAP-aH-ESEK4io5BWIkyozA_7I9XkSoAAqr3MRvjqgABSEJSYiDiWte5AQADAgADeQADNgQ"
        caption = '''Банная печь «Огонь» с тоннелем — идеальный вариант для вашей парной!

Печи этой серии отличаются простотой и надежностью. Печь имеет минимум сварных швов, что говорит о её качестве. 

Верхняя и нижняя плиты имеют гибы. На верхней плите они служат, как ребра жесткости и улучшают нагрев камней. На нижней плите служат, как ребра жесткости и не позволяют углям гореть рядом с боковыми стенками, это предотвращает их перегрев, позволяя углям находиться рядом с колосником, что обеспечивает лучшее горение. 

Также печи серии «Огонь» можно докомплектовать навесными сетками-каменками, навесными баками для воды или конвекционными кожухами.'''
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Печь банная «Огонь» с тоннелем",
                                  url="https://www.center-tepla.ru/catalog/pechi_dlya_bani/pechi_dlya_bani_standart/pech_bannaya_ogon_s_tonnelem_18_kub_m_md/")]
        ])
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=photo_id,
            caption=caption,
            reply_markup=keyboard
        )

    if (
            volume in ["volume_c", "volume_d"] and
            (
                    (season == "season_a") or
                    (season == "season_b" and volume == "volume_c")
            ) and
            usage == "usage_a" and
            bath_type in ["bath_a", "bath_c"] and
            layout in ["layout_a", "layout_c"]
    ):
        recommendation_sent = True
        photo_id = "AgACAgIAAxkBAAIBAAFof4RMkVVbj920BlJ5TPYcUNZuTAACIfgxG64L-EsdyOf0FOX39wEAAwIAA3gAAzYE"
        caption = '''Банная печь «Огонь» с тоннелем — идеальный вариант для вашей парной!

Печи этой серии отличаются простотой и надежностью. Печь имеет минимум сварных швов, что говорит о её качестве. 

Верхняя и нижняя плиты имеют гибы. На верхней плите они служат, как ребра жесткости и улучшают нагрев камней. На нижней плите служат, как ребра жесткости и не позволяют углям гореть рядом с боковыми стенками, это предотвращает их перегрев, позволяя углям находиться рядом с колосником, что обеспечивает лучшее горение. 

Также печи серии «Огонь» можно докомплектовать навесными сетками-каменками, навесными баками для воды или конвекционными кожухами.'''
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Печь банная «Огонь» с тоннелем",
                                  url="https://www.center-tepla.ru/catalog/pechi_dlya_bani/pechi_dlya_bani_standart/pech_bannaya_ogon_s_tonnelem_22_kub_m_md/")]
        ])
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=photo_id,
            caption=caption,
            reply_markup=keyboard
        )

    if (
            volume in ["volume_a", "volume_b"] and
            (
                    (season == "season_a") or
                    (season == "season_b" and volume == "volume_a")
            ) and
            usage in ["usage_a", "usage_b"] and
            bath_type in ["bath_a", "bath_c"] and
            layout in ["layout_a", "layout_c"]
    ):
        recommendation_sent = True
        photo_id = "AgACAgIAAxkBAAIBAmh_hFCBzabitcvG3t456c4dnr2hAAIi-DEbrgv4S9TdHm8SAxqTAQADAgADeQADNgQ"
        caption = '''Печь банная «Remix-15» — наша новинка с нестандартным дизайном – прекрасный союзник в создании атмосферы и хорошего жара!

Создана по образу и подобию нашей «Грации». Надёжная печь из стали толщиной 6 мм, быстро прогреет вашу парную и долго будет держать жар. Конструкция печи предусматривает наличие дожига пламени, он обеспечивает подачу дополнительного воздуха в зону горения, это необходимо для полного сгорания топлива, дрова будут сгорать в топке, а не осаживаться в трубе, забивая её, также это позволит экономичнее использовать печь. На боковых стенках печи присутствуют ребра жесткости, которые не позволяют топливу гореть рядом, что предотвращает перегрев печи и ее деформацию при максимальных тепловых нагрузках, также обеспечивая равномерный теплообмен. 

Печь конвекционная и вот одни из ее главных преимуществ: быстрое прогревание парилки, равномерное распределение тепла, потому что конвекционные потоки распределяют тепло по всей парной, а не только в зоне рядом с печкой, защита от ожогов – закрывает раскалённые стенки топки, снижая риск прикосновения к горячему металлу.
'''
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Печь банная «Remix-15»",
                                  url="https://www.center-tepla.ru/catalog/pechi_dlya_bani/pechi_dlya_bani_konvektsiya_/pech_bannaya_remix_15_konvektsiya_panorama/")]
        ])
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=photo_id,
            caption=caption,
            reply_markup=keyboard
        )

    if (
            volume in ["volume_b", "volume_c"] and
            season in ["season_a", "season_b"] and
            usage in ["usage_a", "usage_b"] and
            bath_type in ["bath_a", "bath_c"] and
            layout in ["layout_a", "layout_c"]
    ):
        recommendation_sent = True
        photo_id = "AgACAgIAAxkBAAIBAmh_hFCBzabitcvG3t456c4dnr2hAAIi-DEbrgv4S9TdHm8SAxqTAQADAgADeQADNgQ"
        caption = '''Печь банная «Remix-20» — наша новинка с нестандартным дизайном – прекрасный союзник в создании атмосферы и хорошего жара!

Создана по образу и подобию нашей «Грации». Надёжная печь из стали толщиной 6 мм, быстро прогреет вашу парную и долго будет держать жар. Конструкция печи предусматривает наличие дожига пламени, он обеспечивает подачу дополнительного воздуха в зону горения, это необходимо для полного сгорания топлива, дрова будут сгорать в топке, а не осаживаться в трубе, забивая её, также это позволит экономичнее использовать печь. На боковых стенках печи присутствуют ребра жесткости, которые не позволяют топливу гореть рядом, что предотвращает перегрев печи и ее деформацию при максимальных тепловых нагрузках, также обеспечивая равномерный теплообмен. 

Печь конвекционная и вот одни из ее главных преимуществ: быстрое прогревание парилки, равномерное распределение тепла, потому что конвекционные потоки распределяют тепло по всей парной, а не только в зоне рядом с печкой, защита от ожогов – закрывает раскалённые стенки топки, снижая риск прикосновения к горячему металлу.'''
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Печь банная «Remix-20»",
                                  url="https://www.center-tepla.ru/catalog/pechi_dlya_bani/pechi_dlya_bani_konvektsiya_/pech_bannaya_remix_20_konvektsiya_panorama/")]
        ])
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=photo_id,
            caption=caption,
            reply_markup=keyboard
        )

    if (
            volume in ["volume_a", "volume_b"] and
            season == "season_a" and
            usage in ["usage_a", "usage_b"] and
            bath_type in ["bath_a", "bath_c"] and
            layout == "layout_b"
    ):
        recommendation_sent = True
        photo_id = "AgACAgIAAxkBAAIBBGh_hFPxCkDnzEKEK5bMdRNopQ_gAAIj-DEbrgv4S0NKV_HGrLGtAQADAgADeQADNgQ"
        caption = '''Печь из серии «Евгения» – идеальный выбор для тех, кто ценит настоящее тепло и комфорт. Эта печь – не просто источник жара, а сердце вашей бани!

Оптимальный баланс между прочностью и теплопередачей. Печь быстро нагревается. Конвекционный кожух равномерно распределяет тепло по парной, что означает меньше затраченного времени на прогрев, комфортная температура без перегрева. 

В конструкции печи отбойник пламени, защищающий от прямого огня и увеличивающий срок службы топки и стартового элемента дымохода. Также внутри дожиг пламени, повышающий эффективность сгорания топлива, экономит дрова и производит меньше дыма. Это значит, что баня – чище, экономичнее и теплее. '''
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Печь банная «Евгения» без тоннеля",
                                  url="https://www.center-tepla.ru/catalog/pechi_dlya_bani/pechi_dlya_bani_konvektsiya_/pech_bannaya_evgeniya_14_kub_m_bez_tonnelya/")]
        ])
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=photo_id,
            caption=caption,
            reply_markup=keyboard
        )
    if (
            volume in ["volume_b", "volume_c"] and
            season in ["season_a", "season_b"] and
            usage in ["usage_a", "usage_b"] and
            bath_type in ["bath_a", "bath_c"] and
            isinstance(layout, str) and layout in ["layout_a", "layout_c"]
    ):
        recommendation_sent = True
        photo_id = "AgACAgIAAxkBAAIBBmh_hFbP4J3P1lBt5ocZxYveBVH1AAKs9zEb46oAAUigQ1kTxPqFJQEAAwIAA3kAAzYE"
        caption = (
            "Банная печь серии «Грация» – надёжная и мощная. "
            "Корпус из стали 6 мм, элементы дожига и ребра жёсткости – 8 мм, "
            "что обеспечивает прочность и долговечность. "
            "Система дожига подаёт воздух в зону горения для полного сгорания топлива "
            "и экономии дров. Отбойник в форме уголка облегчает чистку дымохода. "
            "Конвекционный кожух равномерно прогревает парную и защищает от ожогов."
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Грация-20 BLACK со стеклом",
                                  url="https://www.center-tepla.ru/catalog/pechi_dlya_bani/pechi_dlya_bani_konvektsiya_/pech_bannaya_gratsiya_20_black_so_steklom/")],
            [InlineKeyboardButton("Грация-20 BLACK",
                                  url="https://www.center-tepla.ru/catalog/pechi_dlya_bani/pechi_dlya_bani_konvektsiya_/pech_bannaya_gratsiya_20_black/")]
        ])
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=photo_id,
            caption=caption,
            reply_markup=keyboard
        )

    if (
            volume in ["volume_a", "volume_b"] and
            season == "season_a" and
            usage in ["usage_a", "usage_b"] and
            bath_type in ["bath_a", "bath_c"] and
            layout in ["layout_a", "layout_b", "layout_c"]
    ):
        recommendation_sent = True
        photo_id = "AgACAgIAAxkBAAIBBmh_hFbP4J3P1lBt5ocZxYveBVH1AAKs9zEb46oAAUigQ1kTxPqFJQEAAwIAA3kAAzYE"
        caption = '''Печь банная «Грация-15 BLACK» — компактная и мощная!

Сталь 6 мм, дожиг и отбойник — 8 мм. Конвекционный кожух, быстрый нагрев, равномерное распределение тепла и безопасность. Надёжная и экономичная.'''

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Грация-15 BLACK со стеклом",
                                  url="https://www.center-tepla.ru/catalog/pechi_dlya_bani/pechi_dlya_bani_konvektsiya_/pech_bannaya_gratsiya_15_black_so_steklom/")],
            [InlineKeyboardButton("Грация-15 BLACK",
                                  url="https://www.center-tepla.ru/catalog/pechi_dlya_bani/pechi_dlya_bani_konvektsiya_/pech_bannaya_gratsiya_15_black/")]
        ])
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=photo_id,
            caption=caption,
            reply_markup=keyboard
        )

    if (
            volume == "volume_a" and
            season == "season_a" and
            usage in ["usage_a", "usage_b"] and
            bath_type in ["bath_a", "bath_c"] and
            layout in ["layout_a", "layout_b", "layout_c"]
    ):
        recommendation_sent = True
        photo_id = "AgACAgIAAxkBAAIBCGh_hFpq1A8krFtcgJGDq3E6HuKBAAIk-DEbrgv4SyINfd3MHGHtAQADAgADeAADNgQ"
        caption = '''Печь из серии «Евгения» – идеальный выбор для тех, кто ценит настоящее тепло и комфорт. Эта печь – не просто источник жара, а сердце вашей бани!

Оптимальный баланс между прочностью и теплопередачей. Печь быстро нагревается. Конвекционный кожух равномерно распределяет тепло по парной, что означает меньше времени на прогрев, комфортная температура без перегрева. В конструкции печи отбойник пламени, защищающий от прямого огня и увеличивающий срок службы топки и стартового элемента дымохода. 

Также внутри дожиг пламени, повышающий эффективность сгорания топлива, экономит дрова и производит меньше дыма. Это значит, что баня - чище, экономичнее и теплее.
'''
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Печь банная «Евгения Лайт»",
                                  url="https://www.center-tepla.ru/catalog/pechi_dlya_bani/pechi_dlya_bani_konvektsiya_/pech_bannaya_evgeniya_layt_10_kub/")]
        ])
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=photo_id,
            caption=caption,
            reply_markup=keyboard
        )
    if (
            volume in ["volume_a", "volume_b"] and
            season == "season_a" and
            usage in ["usage_a", "usage_b"] and
            bath_type in ["bath_a", "bath_c"] and
            layout in ["layout_a", "layout_b", "layout_c"]
    ):
        recommendation_sent = True
        photo_id = "AgACAgIAAxkBAAIBCmh_hF3gmI-xd4kT65JGbgEJYW4kAAIl-DEbrgv4SxJf-3TNifODAQADAgADeQADNgQ"
        caption = '''Печь из серии «Евгения» – идеальный выбор для тех, кто ценит настоящее тепло и комфорт. Эта печь – не просто источник жара, а сердце вашей бани!

Оптимальный баланс между прочностью и теплопередачей. Печь быстро нагревается. Конвекционный кожух равномерно распределяет тепло по парной, что означает меньше времени на прогрев, комфортная температура без перегрева. В конструкции печи отбойник пламени, защищающий от прямого огня и увеличивающий срок службы топки и стартового элемента дымохода. 

Также внутри дожиг пламени, повышающий эффективность сгорания топлива, экономит дрова и производит меньше дыма. Это значит, что баня - чище, экономичнее и теплее.'''
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Евгения (дверка со стеклом)",
                                  url="https://www.center-tepla.ru/catalog/pechi_dlya_bani/pechi_dlya_bani_konvektsiya_/pech_bannaya_evgeniya_14_kub_m_dverka_so_steklom/")],
            [InlineKeyboardButton("Евгения (дверка без стекла)",
                                  url="https://www.center-tepla.ru/catalog/pechi_dlya_bani/pechi_dlya_bani_konvektsiya_/pech_bannaya_evgeniya_14_kub_m/")]
        ])
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=photo_id,
            caption=caption,
            reply_markup=keyboard
        )

    if (
            volume in ["volume_c", "volume_d"] and
            season in ["season_a", "season_b"] and
            usage in ["usage_a", "usage_b"] and
            bath_type in ["bath_a", "bath_c"] and
            layout in ["layout_a", "layout_b", "layout_c"]
    ):
        recommendation_sent = True
        photo_id = "AgACAgIAAxkBAAIBDGh_hGAdSM8uOV-ENajZ2tnMtoKtAAIm-DEbrgv4SxcxuDqt_4YzAQADAgADeQADNgQ"
        caption = '''Печь, которая греет не только парилку, но и душу, ведь эта печь родом из детства. 

Печь состоит из трех составных частей, которые вы можете поворачивать в любую удобную для вас сторону: основания печи, каменки и бака из нержавеющей стали. Каменка является в печи отбойником пламени. Печь из трубы, а это значит на ней минимум сварных швов. Дно топки имеет два гиба, которые не позволяют топливу находиться рядом со стенками печи и деформировать их. 

Также в топке имеется дожиг пламени, который повышает эффективность сгорания топлива.'''
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Печь банная «Деревенская»",
                                  url="https://www.center-tepla.ru/catalog/pechi_dlya_bani/pechi_dlya_bani_s_bakom/pech_bannaya_derevenskaya_sostavnaya_bak_nerzh_85_l/")],
            [InlineKeyboardButton("Печь банная «Русь»",
                                  url="https://www.center-tepla.ru/catalog/pechi_dlya_bani/pechi_dlya_bani_s_bakom/pech_bannaya_rus_kruglaya_sostavnaya_bak_nerzh_85_litrov/")]
        ])
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=photo_id,
            caption=caption,
            reply_markup=keyboard
        )

    if (
            volume in ["volume_c", "volume_d"] and
            (
                    (season == "season_a") or
                    (season == "season_b" and volume == "volume_c")
            ) and
            usage in ["usage_a", "usage_b"] and
            bath_type in ["bath_a", "bath_b", "bath_c"] and
            layout in ["layout_a", "layout_b", "layout_c"]
    ):
        recommendation_sent = True
        photo_id = "AgACAgIAAxkBAAIBDmh_hGPn2JkWzh2ixqS530WXEjIkAAIn-DEbrgv4S65tBkIsp1m-AQADAgADeQADNgQ"
        caption = '''Печь состоит из двух частей: топки, совмещенной с каменкой и бака из нержавеющей стали. Бак можно повернуть в любую удобную сторону. 

Главной особенностью печи является закрытая каменка, также можно выбрать удобное для вас расположение: слева или справа. Дно топки имеет два гиба, которые не позволяют топливу находиться рядом со стенками печи и деформировать их. 

Также в топке имеется дожиг пламени, который повышает эффективность сгорания топлива. Печь равномерно и быстро прогреет парное помещение и обеспечит мягким паром, создав комфортную температуру.'''
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Печь банная «Сибирячка-24»",
                                  url="https://www.center-tepla.ru/catalog/pechi_dlya_bani/pechi_dlya_bani_s_bakom/pech_bannaya_sibiryachka_24/")]
        ])
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=photo_id,
            caption=caption,
            reply_markup=keyboard
        )

    if (
            volume in ["volume_c", "volume_d"] and
            season in ["season_a", "season_b"] and
            usage in ["usage_a", "usage_b"] and
            bath_type in ["bath_a", "bath_c"] and
            layout == "layout_c"
    ):
        recommendation_sent = True
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo="AgACAgIAAxkBAAIBEGh_hGbBteYmia0xqoEaVIo0EhK_AAIp-DEbrgv4S8dWATjykDu9AQADAgADeQADNgQ",
            caption='''Идеальное готовое решение для бань, где парильное помещение, топочная и моечная находятся в разных комнатах. Она есть в двух вариантах: с левым расположение бака и с правым.

Эта банная печь спроектирована для одновременного обогрева трёх помещений и станет идеальным готовым решением для бань, где парная, мойка и топочная находятся в разных комнатах. Благодаря продуманной конструкции и высоким теплоотдающим характеристикам, она обеспечивает равномерное распределение тепла и комфортную температуру в каждом помещении.
Печь изготовлена из стали толщиной 8 мм, устойчива к высоким температурам и рассчитана на длительную эксплуатацию. 

Преимущества:
	•	Быстрый прогрев и длительное удержание тепла
	•	Надёжная и безопасная конструкция
	•	Бак для горячей воды в комплекте

Идеальный выбор для тех, кто ценит комфорт, надёжность и экономию пространства в банном комплексе.''',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("ТРИО (лев)",
                                      url="https://www.center-tepla.ru/catalog/pechi_dlya_bani/pechi_dlya_bani_s_bakom/pech_bannaya_trio_24_kub_md_so_steklom_lev/")],
                [InlineKeyboardButton("ТРИО (прав)",
                                      url="https://www.center-tepla.ru/catalog/pechi_dlya_bani/pechi_dlya_bani_s_bakom/pech_bannaya_trio_24_kub_md_so_steklom_prav/")]
            ])
        )

    if (
            volume in ["volume_b", "volume_c"] and
            ((season == "season_a" and volume in ["volume_a", "volume_b"]) or
             (season == "season_b" and volume == "volume_b")) and
            usage == "usage_a" and
            bath_type in ["bath_a", "bath_c"] and
            layout in ["layout_a", "layout_b", "layout_c"]
    ):
        recommendation_sent = True
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo="AgACAgIAAxkBAAIBFGh_hG0e5WPITeF9ILSjA3UBa0QFAAIt-DEbrgv4SwehGpaGS8t4AQADAgADeQADNgQ",
            caption='''Печи этой серии отличаются простотой и надежностью. Печь имеет минимум сварных швов, что говорит о её качестве. 

Верхняя и нижняя плиты имеют гибы. На верхней плите они служат, как ребра жесткости и улучшают нагрев камней. На нижней плите служат, как ребра жесткости и не позволяют углям гореть рядом с боковыми стенками, это предотвращает их перегрев, позволяя углям находиться рядом с колосником, что обеспечивает лучшее горение. На печах этой модели приварен бак для воды, они есть, как с левым баком, так и с правыым. 

Также печи серии «Огонь» можно докомплектовать навесными сетками-каменками или конвекционными кожухами.''',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Огонь с тоннелем и баком (лев)",
                                      url="https://www.center-tepla.ru/catalog/pechi_dlya_bani/pechi_dlya_bani_s_bakom/pech_bannaya_ogon_s_tonnelem_i_bakom_lev_18_kub_m_md/")],
                [InlineKeyboardButton("Огонь с тоннелем и баком (прав)",
                                      url="https://www.center-tepla.ru/catalog/pechi_dlya_bani/pechi_dlya_bani_s_bakom/pech_bannaya_ogon_s_tonnelem_i_bakom_prav_18_kub_m_md/")]
            ])
        )

    if (
            volume in ["volume_a", "volume_b"] and
            ((season == "season_a" and volume == "volume_a") or
             (season == "season_b" and volume == "volume_b")) and
            usage == "usage_a" and
            bath_type in ["bath_a", "bath_c"] and
            layout == "layout_b"
    ):
        recommendation_sent = True
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo="AgACAgIAAxkBAAIBEmh_hGnAiASW2M0qWAv40KpP-tCFAAIq-DEbrgv4S8Aruws6VlEiAQADAgADeQADNgQ",
            caption='''Печи этой серии отличаются простотой и надежностью. Печь имеет минимум сварных швов, что говорит о её качестве. 

Верхняя и нижняя плиты имеют гибы. На верхней плите они служат, как ребра жесткости и улучшают нагрев камней. На нижней плите служат, как ребра жесткости и не позволяют углям гореть рядом с боковыми стенками, это предотвращает их перегрев, позволяя углям находиться рядом с колосником, что обеспечивает лучшее горение. На печах этой модели приварен бак для воды, они есть, как с левым баком, так и с правыым. 

Также печи серии «Огонь» можно докомплектовать навесными сетками-каменками или конвекционными кожухами.''',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Огонь с баком (лев)",
                                      url="https://www.center-tepla.ru/catalog/pechi_dlya_bani/pechi_dlya_bani_s_bakom/pech_bannaya_ogon_s_bakom_lev_12_kub_m_md/")],
                [InlineKeyboardButton("Огонь с баком (прав)",
                                      url="https://www.center-tepla.ru/catalog/pechi_dlya_bani/pechi_dlya_bani_s_bakom/pech_bannaya_ogon_s_bakom_prav_12_kub_m_md/")]
            ])
        )

    if (
            volume in ["volume_a", "volume_b"] and
            season in ["season_a", "season_b"] and
            usage in ["usage_a", "usage_b"] and
            bath_type in ["bath_a", "bath_c"] and
            layout in ["layout_a", "layout_b", "layout_c"]
    ):
        recommendation_sent = True
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo="AgACAgIAAxkBAAIBFmh_hHA3jbl0GIU8DMEaqjknySOAAAIu-DEbrgv4S5I8DJe3yRKRAQADAgADeQADNgQ",
            caption='''Наша новинка с нестандартным дизайном – прекрасный союзник в создании атмосферы и хорошего жара. Создана по образу и подобию нашей «Грации». 

Надёжная печь из нержавеющей стали, быстро прогреет вашу парную и долго будет держать жар. Конструкция печи предусматривает наличие дожига пламени, он обеспечивает подачу дополнительного воздуха в зону горения, это необходимо для полного сгорания топлива, дрова будут сгорать в топке, а не осаживаться в трубе, забивая её, также это позволит экономичнее использовать печь. 

На боковых стенках печи присутствуют ребра жесткости, которые не позволяют топливу гореть рядом, что предотвращает перегрев печи и ее деформацию при максимальных тепловых нагрузках, также обеспечивая равномерный теплообмен.''',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Remix-15 INOX. Медь",
                                      url="https://www.center-tepla.ru/catalog/pechi_dlya_bani/pechi_dlya_bani_s_setkoy/pech_bannaya_remix_15_inox_3mm_setka_panorama_med/")],
                [InlineKeyboardButton("Remix-15 INOX. Графит",
                                      url="https://www.center-tepla.ru/catalog/pechi_dlya_bani/pechi_dlya_bani_s_setkoy/pech_bannaya_remix_15_inox_3mm_setka_panorama_grafit/")]
            ])
        )

    if (
            volume == "volume_b" and
            season in ["season_a", "season_b"] and
            usage in ["usage_a", "usage_b"] and
            bath_type in ["bath_a", "bath_c"] and
            layout in ["layout_a", "layout_c"]
    ):
        recommendation_sent = True
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo="AgACAgIAAxkBAAIBGGh_hSL1h6eGlR8QVghJzflDxcdhAAJL-DEbrgv4S8iaXaNxOvQBAQADAgADeAADNgQ",
            caption='''Горизонтальная банная печь из трубы с сеткой-каменкой — это практичное и эффективное решение для настоящей русской бани. 

Изготовленная из прочной толстостенной, печь отлично держит тепло и равномерно прогревает парную. Конструкция горизонтального типа обеспечивает удобную закладку дров и увеличенную площадь теплообмена. 

В верхней части расположена сетка-каменка, изготовленная из арматуры или металлической сетки — она позволяет закладывать большой объём камней, которые долго сохраняют тепло и создают насыщенный пар. 

Преимущества:
	•	высокая теплоотдача и долговечность;
	•	насыщенный пар;
	•	простота в эксплуатации и обслуживании.

Отличный выбор для тех, кто ценит настоящую банную атмосферу и надёжность проверенных конструкций.''',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Печь «Кельты»",
                                      url="https://www.center-tepla.ru/catalog/pechi_dlya_bani/pechi_dlya_bani_s_setkoy/pech_bannaya_kelty_16_kub_m_md/")]
            ])
        )

    if (
            volume == "volume_b" and
            season in ["season_a", "season_b"] and
            usage in ["usage_a", "usage_b"] and
            bath_type in ["bath_a", "bath_c"] and
            layout in ["layout_a", "layout_b"]
    ):
        recommendation_sent = True
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo="AgACAgIAAxkBAAIBGmh_hSZfxrmPNZXtjXeRCs77_wPiAAJM-DEbrgv4Swmf_JCJo8mVAQADAgADeQADNgQ",
            caption = "Банная печь серии «Грация» – надёжная и мощная. Толщина корпуса — 6 мм, элементов дожига и ребер жесткости — 8 мм. Печь оснащена конвекционным кожухом, который ускоряет прогрев и защищает от ожогов."
            ,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("«Грация-15» с сеткой",
                                      url="https://www.center-tepla.ru/catalog/pechi_dlya_bani/pechi_dlya_bani_s_setkoy/pech_bannaya_gratsiya_15_s_setkoy/")],
                [InlineKeyboardButton("«Грация-15» с сеткой и стеклом",
                                      url="https://www.center-tepla.ru/catalog/pechi_dlya_bani/pechi_dlya_bani_s_setkoy/pech_bannaya_gratsiya_15_s_setkoy_i_steklom/")],
                [InlineKeyboardButton("«Грация-15» с сеткой «Лист дуба»",
                                      url="https://www.center-tepla.ru/catalog/pechi_dlya_bani/pechi_dlya_bani_s_setkoy/pech_bannaya_gratsiya_15_s_setkoy_list_duba/")],
                [InlineKeyboardButton("«Грация-15» с сеткой и стеклом «Лист дуба»",
                                      url="https://www.center-tepla.ru/catalog/pechi_dlya_bani/pechi_dlya_bani_s_setkoy/pech_bannaya_gratsiya_15_s_setkoy_list_duba_dverka_so_steklom/")]
            ])
        )

    if (
            volume in ["volume_b", "volume_c"] and
            season in ["season_a", "season_b"] and
            usage in ["usage_a", "usage_b"] and
            bath_type in ["bath_a", "bath_c"] and
            layout in ["layout_a", "layout_c"]
    ):
        recommendation_sent = True
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo="AgACAgIAAxkBAAIBHGh_hSi_Jqyh9T2g46ItiO8G8aC5AAJO-DEbrgv4S8GhrTuzjvn-AQADAgADeQADNgQ",
            caption='''Горизонтальная банная печь из трубы с сеткой-каменкой — это практичное и эффективное решение для настоящей русской бани. 

Изготовленная из прочной толстостенной, печь отлично держит тепло и равномерно прогревает парную.

Конструкция горизонтального типа обеспечивает удобную закладку дров и увеличенную площадь теплообмена. В верхней части расположена сетка-каменка, изготовленная из арматуры или металлической сетки — она позволяет закладывать большой объём камней, которые долго сохраняют тепло и создают насыщенный пар. 

Преимущества:
	•	высокая теплоотдача и долговечность;
	•	насыщенный пар;
	•	простота в эксплуатации и обслуживании.

Отличный выбор для тех, кто ценит настоящую банную атмосферу и надёжность проверенных конструкций.''',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Онега со стеклом",
                                      url="https://www.center-tepla.ru/catalog/pechi_dlya_bani/pechi_dlya_bani_s_setkoy/pech_bannaya_onega_18_kub_m_md_so_steklom/")],
                [InlineKeyboardButton("Онега обычная",
                                      url="https://www.center-tepla.ru/catalog/pechi_dlya_bani/pechi_dlya_bani_s_setkoy/pech_bannaya_onega_18_kub_m_md/")]
            ])
        )

    if (
            volume in ["volume_a", "volume_b"] and
            season in ["season_a", "season_b"] and
            usage in ["usage_a", "usage_b"] and
            bath_type in ["bath_a", "bath_c"] and
            layout in ["layout_a", "layout_b", "layout_c"]
    ):
        recommendation_sent = True
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo="AgACAgIAAxkBAAIBIGh_hS1lOvxfGi_NgV4yMNBw0eaoAAJR-DEbrgv4S3I4kUGew5sCAQADAgADeQADNgQ",
            caption='''Банная печь горизонтального типа из трубы с каменкой в сетке – это надёжный и эффективный вариант для обустройства парной в традиционном стиле. Корпус печи выполнен из толстой металлической трубы, что гарантирует отличную теплопередачу и длительный срок службы.
Горизонтальная форма обеспечивает удобную топку и равномерное распределение тепла по всей парилке. Над корпусом расположена открытая сетчатая каменка – конструкция, позволяющая разместить внушительный объём камней. Благодаря такому размещению, они быстро прогреваются от жара топки и долго удерживают высокую температуру, создавая густой пар.

Особенности модели:
	•	длительное удержание жара;
	•	мощный прогрев и полноценная каменка;
	•	качественный пар без перегрева воздуха;
	•	удобство в эксплуатации и простота монтажа.

Эта модель станет отличным решением для тех, кто ценит надёжность, тепло и настоящий банный дух.''',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Печь банная «Славянка»",
                                      url="https://www.center-tepla.ru/catalog/pechi_dlya_bani/pechi_dlya_bani_s_setkoy/pech_bannaya_slavyanka_14_kub_m_md/")]
            ])
        )

    if (
            volume == "volume_a" and
            season in ["season_a", "season_b"] and
            usage in ["usage_a", "usage_b"] and
            bath_type in ["bath_a", "bath_c"] and
            layout in ["layout_a", "layout_b", "layout_c"]
    ):
        recommendation_sent = True
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo="AgACAgIAAxkBAAIBHmh_hStPUnyo9VnIKu3OjvHfN6ihAAJP-DEbrgv4SyzfOdaQK9USAQADAgADeQADNgQ",
            caption='''Банная печь горизонтального типа из трубы с каменкой в сетке – это надёжный и эффективный вариант для обустройства парной в традиционном стиле. Корпус печи выполнен из толстой металлической трубы, что гарантирует отличную теплопередачу и длительный срок службы.
Горизонтальная форма обеспечивает удобную топку и равномерное распределение тепла по всей парилке. Над корпусом расположена открытая сетчатая каменка – конструкция, позволяющая разместить внушительный объём камней. Благодаря такому размещению, они быстро прогреваются от жара топки и долго удерживают высокую температуру, создавая густой пар.

Особенности модели:
	•	длительное удержание жара;
	•	мощный прогрев и полноценная каменка;
	•	качественный пар без перегрева воздуха;
	•	удобство в эксплуатации и простота монтажа.

Эта модель станет отличным решением для тех, кто ценит надёжность, тепло и настоящий банный дух.''',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Печь банная «Славянка»",
                                      url="https://www.center-tepla.ru/catalog/pechi_dlya_bani/pechi_dlya_bani_s_setkoy/pech_bannaya_slavyanka_12_kub_m_md/")]
            ])
        )

    if (
            volume in ["volume_b", "volume_c"] and
            season in ["season_a", "season_b"] and
            usage in ["usage_a", "usage_b"] and
            bath_type in ["bath_b", "bath_c"] and
            layout in ["layout_a", "layout_c"]
    ):
        recommendation_sent = True
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo="AgACAgIAAxkBAAIBImh_hTCuooUlklLfgt1PV9ZnKKFhAAJU-DEbrgv4S3s7v2yh4zMKAQADAgADeQADNgQ",
            caption='''Конвекционная печь с закрытой каменкой — идеальный баланс между скоростью нагрева и мягким паром.

Эта печь сочетает в себе преимущества конвекции и закрытой каменки, обеспечивая быстрый прогрев парной и при этом давая мягкий, насыщенный пар. Благодаря закрытой каменке тепло накапливается внутри и равномерно передаётся камням, создавая «лёгкий» пар при минимальном расходе воды.

Преимущества:
• Быстрый прогрев помещения за счёт эффективной конвекции
• Экономичный расход дров при высокой теплоотдаче
• Стабильная температура и отсутствие перегрева воздуха обеспечивают комфортное и равномерное прогревание
• Компактность и простота установки''',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Печь банная «Remix-18»",
                                      url="https://www.center-tepla.ru/catalog/pechi_dlya_bani/pechi_dlya_bani_s_zakrytoy_kamenkoy/pech_bannaya_remix_18_reguliruemaya_konvektsiya_panorama_zakrytaya_kamenka/")]
            ])
        )

    if (
            volume in ["volume_b", "volume_c"] and
            season in ["season_a", "season_b"] and
            usage == "usage_b" and
            bath_type in ["bath_b", "bath_c"] and
            layout in ["layout_a", "layout_c"]
    ):
        recommendation_sent = True
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo="AgACAgIAAxkBAAIBJmh_hTtwSc8icN9yMkkk6NX1baONAAJX-DEbrgv4S1GU-4fCgiJeAQADAgADeQADNgQ",
            caption='''Банная печь из нержавеющей стали с закрытой каменкой и сеткой – мощь, стиль и долговечность для вашей парной.

Эта банная печь сочетает в себе надежность высококачественной нержавеющей стали и продуманную конструкцию для создания настоящего «лёгкого» пара. 
Внешняя сетка для камней не только усиливает теплоотдачу и удерживает жар, но и служит декоративным элементом, придающим печи современный внешний вид. Сетка позволяет разместить дополнительное количество камней, а значит – дольше сохранять тепло и получать больше пара без перегрева воздуха.

Печь устойчива к коррозии, перепадам температур и рассчитана на долгий срок службы даже при регулярной эксплуатации. Идеальный выбор для тех, кто ценит настоящую баню и не готов идти на компромиссы в качестве.''',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Печь «DUBOK-20» INOX",
                                      url="https://www.center-tepla.ru/catalog/pechi_dlya_bani/pechi_dlya_bani_s_zakrytoy_kamenkoy/pech_bannaya_dubok_20_inox_3_mm_s_zakrytoy_kamenkoy/")]
            ])
        )

    if (
            volume == "volume_a" and
            season == "season_a" and
            usage in ["usage_a", "usage_b"] and
            bath_type in ["bath_b", "bath_c"] and
            layout in ["layout_a", "layout_b", "layout_c"]
    ):
        recommendation_sent = True
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo="AgACAgIAAxkBAAIBJmh_hTtwSc8icN9yMkkk6NX1baONAAJX-DEbrgv4S1GU-4fCgiJeAQADAgADeQADNgQ",
            caption='''Эта компактная банная печь идеально сочетает в себе стиль, надежность и практичность.

Особенности конструкции:
	•	Закрытая каменка – обеспечивает мягкий пар. Камни нагреваются до высокой температуры, а подача воды внутрь каменки даёт пар без перегрева воздуха.
	•	Сетка для камней – размещается вокруг корпуса печи и увеличивает теплоотдачу, аккумулируя тепло. Дополнительно она играет декоративную роль и повышает безопасность, защищая от случайных ожогов.
	•	Толщина стенок 4 мм – оптимальный баланс между быстрым нагревом и долговечностью. Печь быстро выходит на рабочий режим и долго сохраняет тепло.
	•	Компактные размеры – печь не занимает много места, что удобно для ограниченного пространства дачной бани.''',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Печь «DUBOK-12» INOX",
                                      url="https://www.center-tepla.ru/catalog/pechi_dlya_bani/pechi_dlya_bani_s_zakrytoy_kamenkoy/pech_bannaya_dubok_12_inox_3_mm_s_zakrytoy_kamenkoy/")]
            ])
        )

    if (
            volume in ["volume_a", "volume_b"] and
            season in ["season_a", "season_b"] and
            usage == "usage_b" and
            bath_type in ["bath_b", "bath_c"] and
            layout in ["layout_a", "layout_c"]
    ):
        recommendation_sent = True
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo="AgACAgIAAxkBAAIBJmh_hTtwSc8icN9yMkkk6NX1baONAAJX-DEbrgv4S1GU-4fCgiJeAQADAgADeQADNgQ",
            caption='''Банная печь из нержавеющей стали с закрытой каменкой и сеткой – мощь, стиль и долговечность для вашей парной.

Эта банная печь сочетает в себе надежность высококачественной нержавеющей стали и продуманную конструкцию для создания настоящего «лёгкого» пара. 
Внешняя сетка для камней не только усиливает теплоотдачу и удерживает жар, но и служит декоративным элементом, придающим печи современный внешний вид. Сетка позволяет разместить дополнительное количество камней, а значит – дольше сохранять тепло и получать больше пара без перегрева воздуха.

Печь устойчива к коррозии, перепадам температур и рассчитана на долгий срок службы даже при регулярной эксплуатации. Идеальный выбор для тех, кто ценит настоящую баню и не готов идти на компромиссы в качестве.''',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Печь «DUBOK-16» INOX",
                                      url="https://www.center-tepla.ru/catalog/pechi_dlya_bani/pechi_dlya_bani_s_zakrytoy_kamenkoy/pech_bannaya_dubok_16_inox_3_mm_s_zakrytoy_kamenkoy/")]
            ])
        )
    if (
            volume in ["volume_a", "volume_b"] and
            season == "season_a" and
            usage == "usage_b" and
            bath_type in ["bath_b", "bath_c"] and
            layout in ["layout_a", "layout_b", "layout_c"]
    ):
        recommendation_sent = True
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo="AgACAgIAAxkBAAIBJGh_hTLahOjrM-DrYqt4Nj0oYHJ3AAJV-DEbrgv4SyTrmmn7KvBzAQADAgADeAADNgQ",
            caption='''Банная печь из нержавеющей стали с закрытой каменкой и сеткой – мощь, стиль и долговечность для вашей парной.

Эта банная печь сочетает в себе надежность высококачественной нержавеющей стали и продуманную конструкцию для создания настоящего «лёгкого» пара. 
Внешняя сетка для камней не только усиливает теплоотдачу и удерживает жар, но и служит декоративным элементом, придающим печи современный внешний вид. Сетка позволяет разместить дополнительное количество камней, а значит – дольше сохранять тепло и получать больше пара без перегрева воздуха.

Печь устойчива к коррозии, перепадам температур и рассчитана на долгий срок службы даже при регулярной эксплуатации. Идеальный выбор для тех, кто ценит настоящую баню и не готов идти на компромиссы в качестве.
''',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Печь «Дубок-12»",
                                      url="https://www.center-tepla.ru/catalog/pechi_dlya_bani/pechi_dlya_bani_s_zakrytoy_kamenkoy/pech_bannaya_dubok_12_4_mm_s_zakrytoy_kamenkoy/")]
            ])
        )
    if recommendation_sent:
        print("Отправляем сообщение с рекомендацией")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=(
                "🎁 Обещанный сюрприз – промокод *чатбот* даст **скидку 7%** на любую из банных печей "
                "в нашем розничном магазине.\n\n"
                "Нажми кнопку «Связаться» и наши менеджеры помогут посчитать полный комплект, "
                "необходимый для монтажа, и ответят на все интересующие вопросы."
            ),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Связаться с менеджером", url="https://t.me/Pechi_ct_nsk")]
            ])
        )
    elif not recommendation_sent:
        print("Отправляем сообщение о кастомном заказе")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=(
                "К сожалению, готового варианта под вашу баню нет, "
                "но мы можем сделать печь под заказ, которая идеально впишется в вашу парную.\n\n"
                "Нажмите кнопку «Связаться» и наши менеджеры Вам помогут."
            ),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Связаться с менеджером", url="https://t.me/Pechi_ct_nsk")]
            ])
        )

def get_application():
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_VOLUME: [CallbackQueryHandler(button_handler)],
            ASK_SEASON: [CallbackQueryHandler(button_handler)],
            ASK_USAGE: [CallbackQueryHandler(button_handler)],
            ASK_BATH_TYPE: [CallbackQueryHandler(button_handler)],
            ASK_LAYOUT: [CallbackQueryHandler(button_handler)],
        },
        fallbacks=[CommandHandler("restart", restart)],
    )

    application.add_handler(conv_handler)
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), message))
    application.add_handler(CommandHandler("message", message))

    return application


# --- FastAPI ---
app = FastAPI()
application = get_application()  # создаём через функцию, чтобы хендлеры добавились

@app.post("/")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.update_queue.put(update)
    return {"ok": True}


@app.on_event("startup")
async def startup_event():
    await application.initialize()

    if WEBHOOK_URL:
        # Режим Webhook
        await application.bot.set_webhook(WEBHOOK_URL)
        await application.start()
        print(f"Webhook установлен: {WEBHOOK_URL}")
    else:
        # Режим Polling (локальный тест)
        await application.start()
        asyncio.create_task(application.updater.start_polling())  # ✅ вместо run_polling
        print("Polling запущен")


@app.on_event("shutdown")
async def shutdown_event():
    await application.stop()
    await application.shutdown()
    print("Бот остановлен")