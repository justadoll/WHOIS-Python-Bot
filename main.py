from aiogram import Bot, types
from aiogram.utils.helper import Helper
from aiogram.utils import executor
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from loguru import logger
import yaml
import whois
logger.add("info.json", format="{time} {level} {message}", level="INFO", rotation="5 MB", compression="zip", serialize=True)

hz = ["domain_name","emails","address"]

with open("config.yaml") as f:
    data = yaml.load(f,Loader=yaml.FullLoader)


class Curwhois(StatesGroup):
    addr = State()

def parse_wis(data,ip):
    res_str = ""
    res_str += "IP: "+ ip + '\n'
    res_str += "City: "+ str(data.city) + '\n'
    res_str += "State: "+data.state + '\n'
    res_str += "Country: "+str(data.country) + '\n'
    if check_type(data.domain_name) == True:
        for i in data.domain_name:
            res_str += "Domain name: "+ i + '\n'
    else:
        res_str += "Domain name: "+ data.domain_name + '\n'
    if check_type(data.emails) == True:
        for i in data.emails:
            res_str += "Email: "+ i + '\n'
    else:
        res_str += "Email: "+ data.emails + '\n'
    if check_type(data.address) == True:
        for i in data.adderss:
            res_str += "Address: "+ i + '\n'
    else:
        res_str += "Address: "+str(data.address) + '\n'
    return res_str


def check_type(data):
    if type(data) == list:
        return True
    else:
        return False


bot = Bot(token=data['token'])
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    logger.info('Cancelling state' + str(current_state))
    await state.finish()
    await message.reply('Cancelled')

@dp.message_handler(commands=['start'])
async def start(msg:types.Message):
    await msg.reply(data['messages'][0])


@dp.message_handler(commands=['help'])
async def start(msg:types.Message):
    await msg.reply(data['messages'][2])


@dp.message_handler(commands=['whois'])
async def proccess_whois(message: types.Message):
    await Curwhois.addr.set()
    await message.reply(data['messages'][1])

@dp.message_handler(state=Curwhois.addr)
async def process_set_ip(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['addr'] = message.text
        tmpaddr = whois.whois(data['addr'])
        await message.reply(parse_wis(tmpaddr,data['addr']))
        await state.finish()


if __name__ == "__main__":
    executor.start_polling(dp)
