# main.py - Бот "Абитуриенту ДТПА"
import asyncio
import logging
import re
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode

# 🔹 Импорт настроек из config.py
from config import BOT_TOKEN, ADMIN_ID, COLLEGE_SITE

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

# ================= ДАННЫЕ ТЕХНИКУМА =================
COLLEGE_INFO = {
    "name": "ГБПОУ «Донецкий техникум промышленной автоматики им. А.В. Захарченко»",
    "address": "283086, г. Донецк, ул. Горького, д. 163",
    "phone_admission": "+7 (949) 728-81-67",
    "phone_accounting": "+7 (949) 321-64-71",
    "phone_hr": "+7 (949) 516-39-12",
    "email": "info@dontpa.ru",
    # ✅ Используем COLLEGE_SITE из config.py
    "site": COLLEGE_SITE,
    "slogan": "🚀 Твоё будущее в мире автоматики и IT начинается здесь!"
}

SPECIALTIES = [
    {
        "code": "09.02.07",
        "name": "Информационные системы и программирование",
        "profiles": ["Программист", "Веб-разработка"],
        "duration": "3г 10м (9 кл) / 2г 10м (11 кл)",
        "jobs": "программист, веб-разработчик, тестировщик, системный администратор",
        "form": "очная, бюджет/контракт"
    },
    {
        "code": "09.02.10",
        "name": "Обеспечение информационной безопасности ТКС",
        "profiles": ["Защита информации"],
        "duration": "3г 10м (9 кл) / 2г 10м (11 кл)",
        "jobs": "IT-специалист по безопасности, монтажник оборудования связи",
        "form": "очная, бюджет/контракт"
    },
    {
        "code": "09.02.01",
        "name": "Компьютерные системы и комплексы",
        "profiles": ["Техническая эксплуатация"],
        "duration": "3г 10м (9 кл) / 2г 10м (11 кл)",
        "jobs": "системный администратор, наладчик компьютерных сетей",
        "form": "очная, бюджет/контракт"
    },
    {
        "code": "09.02.02",
        "name": "Сетевое и системное администрирование",
        "profiles": ["Администрирование сетей"],
        "duration": "3г 10м (9 кл) / 2г 10м (11 кл)",
        "jobs": "сетевой администратор, техник по обслуживанию сетей",
        "form": "очная, бюджет/контракт"
    },
    {
        "code": "15.02.14",
        "name": "Техническая эксплуатация роботизированного производства",
        "profiles": ["Робототехника", "Автоматизация"],
        "duration": "3г 10м (9 кл) / 2г 10м (11 кл)",
        "jobs": "робототехник, наладчик ЧПУ, программист станков",
        "form": "очная, бюджет/контракт"
    },
    {
        "code": "38.02.01",
        "name": "Экономика и бухгалтерский учёт",
        "profiles": ["По отраслям"],
        "duration": "2г 10м (11 кл)",
        "jobs": "бухгалтер, экономист, финансовый аналитик",
        "form": "очная, бюджет/контракт"
    },
    {
        "code": "38.02.07",
        "name": "Банковское дело",
        "profiles": ["Финансы"],
        "duration": "2г 10м (11 кл)",
        "jobs": "специалист банка, кредитный эксперт, финансовый контролёр",
        "form": "очная, бюджет/контракт"
    },
    {
        "code": "42.02.01",
        "name": "Реклама",
        "profiles": ["Маркетинг"],
        "duration": "2г 10м (11 кл)",
        "jobs": "рекламный агент, копирайтер, бренд-менеджер, дизайнер",
        "form": "очная, бюджет/контракт"
    }
]

ADMISSION_RULES = f"""
📋 <b>Правила приёма в ДТПА им. А.В. Захарченко (2026)</b>

✅ <b>Кто может поступать:</b>
• Выпускники 9 и 11 классов
• Лица с СПО/ВПО (на ускоренное обучение)

📄 <b>Документы для подачи:</b>
1. Заявление (лично/Госуслуги/МФЦ)
2. Аттестат об образовании (оригинал/копия)
3. Паспорт + копия
4. 6 фото 3×4 см
5. Мед. справка 086/у (по треб.)
6. Документы о льготах (при наличии)

🎯 <b>Зачисление:</b>
• По среднему баллу аттестата (конкурсный рейтинг)
• Вступительные испытания: только творческой направленности (при необходимости)
• Целевое обучение — по договору с предприятием

🔗 Подать заявление: {COLLEGE_SITE}/admission
"""

DATES_INFO = f"""
📅 <b>Сроки приёма документов — 2026</b>

🟢 <b>Начало приёма:</b> 20 июня 2026
🔴 <b>Окончание приёма:</b> 15 августа 2026, 12:00
📜 <b>Приказы о зачислении:</b> 18–25 августа 2026

⏰ Режим работы приёмной комиссии:
Пн–Пт: 09:00–17:00, Сб: 09:00–14:00

📍 Адрес: г. Донецк, ул. Горького, 163
📞 Телефон: {COLLEGE_INFO['phone_admission']}
"""

# ================= КЛАВИАТУРЫ =================
def main_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎓 Специальности", callback_data="spec_list")],
        [InlineKeyboardButton(text="📋 Правила приёма", callback_data="admission")],
        [InlineKeyboardButton(text="📅 Сроки и документы", callback_data="dates")],
        [InlineKeyboardButton(text="🎮 Викторина по ДТПА", callback_data="quiz_start")],
        [InlineKeyboardButton(text="📍 Контакты и адрес", callback_data="contacts")],
        [InlineKeyboardButton(text="✉️ Задать вопрос", callback_data="feedback")]
    ])

def specialties_keyboard():
    kb = []
    for i, spec in enumerate(SPECIALTIES):
        kb.append([InlineKeyboardButton(
            text=f"{spec['code']} {spec['name'][:40]}...",
            callback_data=f"spec_{i}"
        )])
    kb.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_main")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

def quiz_keyboard(options: list):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=opt, callback_data=f"quiz_ans_{i}")]
        for i, opt in enumerate(options)
    ])

# ================= FSM ДЛЯ ОБРАТНОЙ СВЯЗИ =================
class FeedbackState(StatesGroup):
    waiting_question = State()

# ================= ХЕНДЛЕРЫ =================

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        f"👋 <b>Привет! Я бот «Абитуриенту ДТПА»</b>\n\n"
        f"{COLLEGE_INFO['slogan']}\n\n"
        f"🏫 {COLLEGE_INFO['name']}\n"
        f"🌐 {COLLEGE_INFO['site']}\n\n"
        f"Выберите раздел меню:",
        reply_markup=main_keyboard(),
        parse_mode=ParseMode.HTML
    )

@dp.callback_query(F.data == "back_main")
async def back_main(call: types.CallbackQuery):
    await call.message.edit_text(
        "🔙 Главное меню:",
        reply_markup=main_keyboard(),
        parse_mode=ParseMode.HTML
    )
    await call.answer()

# 🔹 Специальности
@dp.callback_query(F.data == "spec_list")
async def show_specialties(call: types.CallbackQuery):
    await call.message.edit_text(
        "🎓 <b>Специальности ДТПА им. А.В. Захарченко</b>\n"
        "Нажмите на интересующую специальность:",
        reply_markup=specialties_keyboard(),
        parse_mode=ParseMode.HTML
    )
    await call.answer()

@dp.callback_query(F.data.regexp(r"^spec_\d+$"))
async def show_spec_detail(call: types.CallbackQuery):
    idx = int(call.data.split("_")[1])
    spec = SPECIALTIES[idx]
    text = (
        f"🔹 <b>{spec['code']} {spec['name']}</b>\n"
        f"📌 Профиль: {', '.join(spec['profiles'])}\n"
        f"⏱ Срок обучения: {spec['duration']}\n"
        f"💼 Будущие профессии: {spec['jobs']}\n"
        f"📚 Форма: {spec['form']}\n\n"
        f"ℹ️ Подробнее: {COLLEGE_INFO['site']}"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 К списку", callback_data="spec_list")],
        [InlineKeyboardButton(text="🏠 В меню", callback_data="back_main")]
    ])
    await call.message.edit_text(text, reply_markup=kb, parse_mode=ParseMode.HTML)
    await call.answer()

# 🔹 Правила приёма
@dp.callback_query(F.data == "admission")
async def show_admission(call: types.CallbackQuery):
    await call.message.edit_text(ADMISSION_RULES, reply_markup=main_keyboard(), parse_mode=ParseMode.HTML)
    await call.answer()

# 🔹 Сроки
@dp.callback_query(F.data == "dates")
async def show_dates(call: types.CallbackQuery):
    await call.message.edit_text(DATES_INFO, reply_markup=main_keyboard(), parse_mode=ParseMode.HTML)
    await call.answer()

# 🔹 Контакты
@dp.callback_query(F.data == "contacts")
async def show_contacts(call: types.CallbackQuery):
    text = (
        f"📍 <b>Контакты ДТПА</b>\n\n"
        f"🏢 {COLLEGE_INFO['name']}\n"
        f"🗺 Адрес: {COLLEGE_INFO['address']}\n\n"
        f"📞 <b>Телефоны:</b>\n"
        f"• Приёмная комиссия: {COLLEGE_INFO['phone_admission']}\n"
        f"• Бухгалтерия: {COLLEGE_INFO['phone_accounting']}\n"
        f"• Отдел кадров: {COLLEGE_INFO['phone_hr']}\n"
        f"• Канцелярия: +7 (949) 359-15-62\n\n"
        f"✉️ Email: {COLLEGE_INFO['email']}\n"
        f"🌐 Сайт: {COLLEGE_INFO['site']}\n\n"
        f"<i>🗺 Открыть на карте:</i>\n"
        f"https://yandex.ru/maps/?text=Донецк+ул+Горького+163"
    )
    await call.message.edit_text(text, reply_markup=main_keyboard(), parse_mode=ParseMode.HTML)
    await call.answer()

# 🔹 Викторина
QUIZ_QUESTIONS = [
    {
        "q": "Какой срок обучения на специальности «Программист» после 9 класса?",
        "options": ["2 года", "3 года 10 месяцев", "4 года"],
        "correct": 1,
        "explain": "✅ Верно! После 9 класса обучение длится 3 года 10 месяцев."
    },
    {
        "q": "Зачисление на бюджет в ДТПА проходит по...",
        "options": ["результатам ЕГЭ", "среднему баллу аттестата", "собеседованию"],
        "correct": 1,
        "explain": "✅ Правильно! Рейтинг формируется по среднему баллу аттестата."
    },
    {
        "q": "До какого числа можно подать документы в 2026 году?",
        "options": ["1 июля", "15 августа", "30 августа"],
        "correct": 1,
        "explain": "✅ Верно! Приём документов заканчивается 15 августа 2026 в 12:00."
    }
]

@dp.callback_query(F.data == "quiz_start")
async def quiz_start(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(quiz_index=0, score=0)
    await send_quiz_question(call, 0, state)

async def send_quiz_question(call: types.CallbackQuery, index: int, state: FSMContext):
    if index >= len(QUIZ_QUESTIONS):
        data = await state.get_data()
        score = data.get("score", 0)
        await call.message.edit_text(
            f"🎉 <b>Викторина завершена!</b>\n"
            f"Ваш результат: {score} из {len(QUIZ_QUESTIONS)}\n\n"
            f"{'🏆 Отлично!' if score == len(QUIZ_QUESTIONS) else '👍 Хорошо!' if score >= 2 else '📚 Повторите информацию на сайте'}",
            reply_markup=main_keyboard(),
            parse_mode=ParseMode.HTML
        )
        await state.clear()
        await call.answer()
        return
    
    q = QUIZ_QUESTIONS[index]
    await call.message.edit_text(
        f"🎮 <b>Вопрос {index+1}/{len(QUIZ_QUESTIONS)}</b>\n\n{q['q']}",
        reply_markup=quiz_keyboard(q["options"]),
        parse_mode=ParseMode.HTML
    )
    await call.answer()

@dp.callback_query(F.data.regexp(r"^quiz_ans_\d+$"))
async def quiz_answer(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    idx = data.get("quiz_index", 0)
    score = data.get("score", 0)
    
    user_ans = int(call.data.split("_")[2])
    correct = QUIZ_QUESTIONS[idx]["correct"]
    
    if user_ans == correct:
        score += 1
        await call.message.edit_text(
            QUIZ_QUESTIONS[idx]["explain"],
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="➡️ Следующий вопрос", callback_data="quiz_next")]
            ]),
            parse_mode=ParseMode.HTML
        )
    else:
        await call.message.edit_text(
            f"❌ Неверно. {QUIZ_QUESTIONS[idx]['explain']}\n\n"
            f"Правильный ответ: {QUIZ_QUESTIONS[idx]['options'][correct]}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="➡️ Следующий вопрос", callback_data="quiz_next")]
            ]),
            parse_mode=ParseMode.HTML
        )
    
    await state.update_data(quiz_index=idx+1, score=score)
    await call.answer()

@dp.callback_query(F.data == "quiz_next")
async def quiz_next(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await send_quiz_question(call, data["quiz_index"], state)

# 🔹 Обратная связь
@dp.callback_query(F.data == "feedback")
async def start_feedback(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(
        "✉️ <b>Обратная связь</b>\n\n"
        "Напишите ваш вопрос ниже. Администратор приёмной комиссии ответит в рабочее время.\n\n"
        "⚠️ <i>Мы не собираем персональные данные без вашего согласия и не передаём их третьим лицам.</i>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_main")]
        ]),
        parse_mode=ParseMode.HTML
    )
    await state.set_state(FeedbackState.waiting_question)
    await call.answer()

@dp.message(FeedbackState.waiting_question)
async def process_feedback(message: types.Message, state: FSMContext):
    # Сохраняем вопрос в файл
    with open("data/feedback_log.txt", "a", encoding="utf-8") as f:
        f.write(f"[{message.date}] @{message.from_user.username}: {message.text}\n")
    
    # Уведомляем админа (если настроен)
    if ADMIN_ID:
        try:
            await bot.send_message(
                ADMIN_ID,
                f"📩 <b>Новый вопрос от абитуриента:</b>\n"
                f"👤 @{message.from_user.username} ({message.from_user.id})\n"
                f"💬 {message.text}",
                parse_mode=ParseMode.HTML
            )
        except:
            pass
    
    await message.answer(
        "✅ Спасибо! Ваш вопрос принят. Ожидайте ответа в рабочее время.\n"
        f"📞 Экстренно: {COLLEGE_INFO['phone_admission']}",
        reply_markup=main_keyboard()
    )
    await state.clear()

# 🔹 Этический фильтр (п. 5.3 Порядка)
BANNED_PATTERNS = [
    r'дурак|тупой|идиот|бред|лох|придурок|мразь',
    r'наци|расизм|дискримин',
    r'взлом|хак|спам|рассылка'
]

@dp.message(~StateFilter(FeedbackState.waiting_question))
async def handle_unknown(message: types.Message):
    text_lower = message.text.lower()
    
    # Проверка на неэтичный контент
    for pattern in BANNED_PATTERNS:
        if re.search(pattern, text_lower, re.I):
            await message.answer(
                "🤝 Пожалуйста, общайтесь уважительно. Я готов помочь по вопросам поступления в ДТПА!\n"
                "Используйте кнопки меню или команду /start",
                reply_markup=main_keyboard()
            )
            return
    
    # Проверка на запрос персональных данных
    if any(kw in text_lower for kw in ["паспорт", "снилс", "адрес прописки", "номер карты"]):
        await message.answer(
            "🔒 Я не запрашиваю и не храню персональные данные.\n"
            "Для подачи документов используйте официальный сайт или приёмную комиссию:\n"
            f"📞 {COLLEGE_INFO['phone_admission']}",
            reply_markup=main_keyboard()
        )
        return
    
    await message.answer(
        "🔍 Я пока не понял ваш вопрос. Попробуйте:\n"
        "• Использовать кнопки меню ниже\n"
        "• Написать /start для главного меню\n"
        "• Задать вопрос через раздел «✉️ Обратная связь»",
        reply_markup=main_keyboard()
    )

# ================= ЗАПУСК =================
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())