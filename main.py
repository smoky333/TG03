import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import F, Router
import asyncio
from config import TOKEN

# Инициализация бота и диспетчера
token = TOKEN
bot = Bot(token=TOKEN)
router = Router()
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
dp.include_router(router)

# Создание базы данных и таблицы students
def init_db():
    conn = sqlite3.connect("school_data.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER,
            grade TEXT
        )
        """
    )
    conn.commit()
    conn.close()

# Сохраняем данные студента в базу данных
def save_student(name, age, grade):
    conn = sqlite3.connect("school_data.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO students (name, age, grade) VALUES (?, ?, ?)", (name, age, grade))
    conn.commit()
    conn.close()

# Определение состояний
class Form(StatesGroup):
    name = State()
    age = State()
    grade = State()

# Начало работы с ботом
@router.message(F.text == "/start")
async def send_welcome(message: types.Message, state: FSMContext):
    await message.reply("Привет! Пожалуйста, введите ваше имя.")
    await state.set_state(Form.name)

# Шаг 1: Запрашиваем имя
@router.message(Form.name)
async def ask_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.reply("Отлично! Теперь введите ваш возраст.")
    await state.set_state(Form.age)

# Шаг 2: Запрашиваем возраст
@router.message(Form.age)
async def ask_age(message: types.Message, state: FSMContext):
    try:
        age = int(message.text)
        await state.update_data(age=age)
        await message.reply("Спасибо! Теперь введите ваш класс (grade).")
        await state.set_state(Form.grade)
    except ValueError:
        await message.reply("Пожалуйста, введите корректный возраст (число).")

# Шаг 3: Запрашиваем класс
@router.message(Form.grade)
async def ask_grade(message: types.Message, state: FSMContext):
    data = await state.get_data()
    name = data["name"]
    age = data["age"]
    grade = message.text

    save_student(name, age, grade)
    await message.reply(f"Данные сохранены!\nИмя: {name}\nВозраст: {age}\nКласс: {grade}")
    await state.clear()

# Запуск бота
async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
