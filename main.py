from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
import random

API_TOKEN = "8428577175:AAHgRq-G99IHfqhuW92YWlZFycwYYgKn458"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

user_data = {}

QUESTIONS = {
    "Відкриття ФОП": [
        {"question": "Який перший крок для відкриття ФОП?",
         "options": ["Подати звітність", "Зареєструватися в ЦНАП", "Відкрити банківський рахунок", "Отримати ліцензію"],
         "answer": "Зареєструватися в ЦНАП",
         "explanation": "Перший крок — це реєстрація фізичної особи-підприємця в ЦНАП або онлайн через Дію."},
        {"question": "Який код діяльності ФОП потрібно обрати?",
         "options": ["Будь-який, який подобається", "Відповідно до виду діяльності", "Тільки 01.11", "Не потрібен"],
         "answer": "Відповідно до виду діяльності",
         "explanation": "КВЕД визначає, чим саме ви займаєтесь, тому його потрібно обирати за вашим видом діяльності."}
    ],
    "Податки та звітність": [
        {"question": "Що таке податкова декларація?",
         "options": ["Щомісячний платіж", "Документ для податкової про доходи", "Ліцензія на діяльність", "Банківський рахунок"],
         "answer": "Документ для податкової про доходи",
         "explanation": "Декларація — це звіт, який подається до податкової про доходи та витрати."},
        {"question": "Як часто ФОП 2 групи сплачує єдиний податок?",
         "options": ["Щодня", "Щомісяця", "Щоквартально", "Раз на рік"],
         "answer": "Щомісяця",
         "explanation": "ФОП 2 групи сплачує єдиний податок щомісяця до 20 числа поточного місяця."}
    ],
    "Фінансова грамотність": [
        {"question": "Що таке бюджет?",
         "options": ["План доходів і витрат", "Банк", "Податкова", "Кредит"],
         "answer": "План доходів і витрат",
         "explanation": "Бюджет — це план, який допомагає контролювати доходи та витрати."},
        {"question": "Що означає термін 'інвестиція'?",
         "options": ["Витрати на покупки", "Вкладання грошей з метою отримати прибуток", "Виплата податків", "Дарування грошей"],
         "answer": "Вкладання грошей з метою отримати прибуток",
         "explanation": "Інвестиції — це спосіб збільшити капітал, вкладаючи гроші у бізнес, акції чи інші активи."}
    ]
}


# === КНОПКИ ===

def main_menu_keyboard():
    buttons = [
        [InlineKeyboardButton(text="▶️ Почати вікторину", callback_data="start_quiz")],
        [InlineKeyboardButton(text="🔄 Змінити вікторину", callback_data="restart")],
        [InlineKeyboardButton(text="ℹ️ Допомога", callback_data="help")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def category_keyboard():
    buttons = [[InlineKeyboardButton(text=cat, callback_data=f"cat_{cat}")] for cat in QUESTIONS.keys()]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def answer_keyboard(options):
    buttons = [
        [InlineKeyboardButton(text=opt, callback_data=f"ans_{i}")]
        for i, opt in enumerate(options)
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)



@dp.message(Command("start"))
async def start_menu(message: types.Message):
    await message.answer("Вітаю у боті SmartFOP! 🎯\nОбери дію нижче:", reply_markup=main_menu_keyboard())


@dp.callback_query(lambda c: c.data == "start_quiz")
async def start_quiz(callback: types.CallbackQuery):
    user_data[callback.from_user.id] = {}
    await callback.message.answer("Оберіть категорію для вікторини:", reply_markup=category_keyboard())


@dp.callback_query(lambda c: c.data == "restart")
async def restart_quiz(callback: types.CallbackQuery):
    user_data[callback.from_user.id] = {}
    await callback.message.answer("Рестартуємо вікторину! 🔄\nОберіть категорію:", reply_markup=category_keyboard())


@dp.callback_query(lambda c: c.data == "help")
async def help_menu(callback: types.CallbackQuery):
    text = (
        "🧩 *Як користуватись ботом:*\n\n"
        "1️⃣ Натисни *Почати вікторину*.\n"
        "2️⃣ Обери категорію запитань.\n"
        "3️⃣ Відповідай на 10 запитань.\n"
        "4️⃣ Після кожного питання отримаєш пояснення.\n"
        "5️⃣ Наприкінці побачиш свій результат.\n\n"
        
        "Наш сайт - https://smartfop.byethost7.com/\n\n"
        "Успіхів! 💪"
    )
    await callback.message.answer(text, parse_mode="Markdown")


@dp.callback_query(lambda c: c.data.startswith("cat_"))
async def choose_category(callback: types.CallbackQuery):
    category = callback.data[4:]
    questions = QUESTIONS[category]
    user_data[callback.from_user.id] = {
        'category': category,
        'questions': random.sample(questions, min(10, len(questions))),
        'current': 0,
        'score': 0
    }
    await send_question(callback.from_user.id)


async def send_question(user_id):
    data = user_data.get(user_id)
    if not data:
        return

    idx = data['current']
    questions = data['questions']

    if idx >= len(questions):
        await bot.send_message(
            user_id,
            f"🎉 Вікторина завершена!\n\nВаш результат: *{data['score']}* з *{len(questions)}*",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard()
        )
        return

    q = questions[idx]
    text = f"❓ Питання {idx + 1} з {len(questions)}:\n\n{q['question']}"
    await bot.send_message(user_id, text, reply_markup=answer_keyboard(q['options']))


@dp.callback_query(lambda c: c.data.startswith("ans_"))
async def answer_question(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    data = user_data.get(user_id)
    if not data:
        await callback.answer("Сесія закінчена або не стартувала.")
        return

    idx = data['current']
    questions = data['questions']

    if idx >= len(questions):
        await callback.answer("Вікторина вже завершена.")
        return

    selected_index = int(callback.data[4:])
    question = questions[idx]
    selected_answer = question['options'][selected_index]

    if selected_answer == question['answer']:
        data['score'] += 1
        text = f"✅ Правильно!\n\n💡 {question['explanation']}"
    else:
        text = (
            f"❌ Неправильно!\n\n"
            f"Правильна відповідь: *{question['answer']}*\n\n"
            f"💡 {question['explanation']}"
        )

    await bot.send_message(user_id, text, parse_mode="Markdown")
    data['current'] += 1
    await send_question(user_id)


if __name__ == "__main__":
    dp.run_polling(bot)
