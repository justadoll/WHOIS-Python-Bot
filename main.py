from aiogram import Bot, types
from aiogram.utils.helper import Helper
from aiogram.utils import executor
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import yaml
import whois

with open("config.yaml") as f:
    data = yaml.load(f,Loader=yaml.FullLoader)
    print(data)


class Curwhois(StatesGroup):
    addr = State()


bot = Bot(token=data['token'])
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(commands=['start'])
async def start(msg:types.Message):
    await bot.send_message(msg.chat.id, data['messages'][0])
    #tmp = whois.whois("46.174.164.132")


@dp.message_handler(commands=['whois'])
async def proccess_whois(message: types.Message):
    await Curwhois.addr.set()
    await bot.send_message(message.chat.id, data['messages'][1])

@dp.message_handler(state=Curwhois.addr)
async def process_set_ip(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['addr'] = message.text
        print(data['addr'])
        await state.finish()


if __name__ == "__main__":
    executor.start_polling(dp)
