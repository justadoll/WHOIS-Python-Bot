from aiogram import Bot, types
from aiogram.utils.helper import Helper
from aiogram.utils import executor
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from loguru import logger
from random import randint
import ipinfo
import pprint
import pyexcel
import re
import yaml
import requests
import time

logger.add("info.json", format="{time} {level} {message}", level="INFO", rotation="5 MB", compression="zip", serialize=True)

with open("config.yaml") as f:
    yamldata = yaml.load(f,Loader=yaml.FullLoader)


def get_org(ipfo):
    try:
        return ipfo.org
    except AttributeError:
        return "Not found"

class Curwhois(StatesGroup):
    addr = State()


class Single_whois(StatesGroup):
    addr = State()
bot = Bot(token=yamldata['token'])
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
ipinf_api = yamldata['config_api']
handler = ipinfo.getHandler(ipinf_api)

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
    await msg.reply(yamldata['messages'][0])


@dp.message_handler(commands=['help'])
async def start(msg:types.Message):
    await msg.reply(yamldata['messages'][2])


@dp.message_handler(commands=['whois'])
async def proccess_whois(message: types.Message):
    await Curwhois.addr.set()
    await message.reply(yamldata['messages'][1])

@dp.message_handler(state=Curwhois.addr)
async def process_set_ip(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['addr'] = message.text
        ip_list = data['addr'].split('\n')
        uid = message['from']['username']
        ri = str(randint(0,1000))
        uname = uid+"_"+time.strftime('%Y-%m-%d', time.localtime(int(time.time())))+f'({ri})'+".xls"
        arr = []
        logger.info(uname+'\n'+str(message.chat.id))
        for ip in ip_list:
            try:
                ipres = handler.getDetails(ip).all
                arr.append(ipres)
            except requests.exceptions.HTTPError:
                await message.reply('\''+ip+'\''+'\n'+yamldata['messages'][3])
                logger.error(f"{message.chat.id}:{ip}")
        pyexcel.save_as(records=arr,dest_file_name="files/"+uname)
        with open('files/'+uname,"rb") as f:
            await bot.send_document(message.chat.id,f)
        await state.finish()


@dp.message_handler(commands=['get_provider'])
async def proccess_whois(message: types.Message):
    await Single_whois.addr.set()
    await message.reply(yamldata['messages'][4])

@dp.message_handler(state=Single_whois.addr)
async def process_set_ip(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['addr'] = message.text
        msg_res = ""
        ip_list = data['addr'].split('\n')
        #logger.info()
        for ip in ip_list:
            try:
                tmp = handler.getDetails(ip)
                msg_res += "Organization: "+get_org(tmp)+"\n"
                msg_res += "IP:"+tmp.ip+"\nCity: "+ tmp.city+"\nCountry:"+tmp.country+"\nRegion: "+tmp.region+"\n\n"
            except requests.exceptions.HTTPError:
                await message.reply("Invalid ip: "+ ip)

        await message.reply(msg_res)
        await state.finish()




if __name__ == "__main__":
    executor.start_polling(dp)
