from aiogram import Bot, types
from aiogram.utils.helper import Helper
from aiogram.utils import executor
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.exceptions import MessageIsTooLong
from loguru import logger
from random import randint
from pymemcache.client import base
import ipinfo
import pprint
import pyexcel
import re
import yaml
import requests
import time
import asyncio



logger.add("info.json", format="{time} {level} {message}", level="INFO", rotation="5 MB", compression="zip", serialize=True)

with open("config.yaml") as f:
    yamldata = yaml.load(f,Loader=yaml.FullLoader)

client = base.Client((yamldata['memcached_ip'], yamldata['memcached_port']))

def get_org(ipfo):
    try:
        return ipfo.org
    except AttributeError:
        return "Not found"

def get_host(ipfo):
    try:
        return ipfo.hostname
    except AttributeError:
        return "Not found"

def appender(inp,out):
    out = []
    if(inp != []):
        for a in inp:
            out.append(a)
        return out
    else:
        return out


def check_host(userinpt):
    result = []
    ips = re.findall(r"\d+\.\d+\.\d+\.\d+",userinpt)
    host = re.findall(r"[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)", userinpt)
    result = appender(ips, result)
    logger.debug(ips)
    #result = appender(host, result)
    if result != []:
        return result
    else:
        return None

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
        ri = str(randint(0,1000))
        if message.from_user.username == None:
            uname = str(message.chat.id)+"_"+time.strftime('%Y-%m-%d', time.localtime(int(time.time())))+f'({ri})'+".xls"
        else:
            uid = message['from']['username']
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
        data['addr'] = check_host(message.text)
        logger.debug(len(data['addr']))

        userinfo = client.get(str(message.chat.id))
        logger.debug("USERINFO:"+str(userinfo))
        if data['addr'] == None:
            #[-] просто нету айпих в сообщении
            await bot.send_message(message.chat.id, "Host/IP not found!\nRead /help and try again")
            await state.finish()
        elif (len(data['addr'])>100):
            #[-] дохуя айпих в месаге
            await bot.send_message(message.chat.id,'Слишком много айпи в одном сообщении!')
            await state.finish()
        elif (userinfo != None and int(userinfo)>100):
            #[-] если пользователь есть в мемкахе и у него статус больше 100
            await bot.send_message(message.chat.id, "Упс!\nВы просканили больше 100 айпи\nПриходите через час :3")
        else:
            #[+] если юзера нету в мемкахе
            msg_res = ""
            try:
                if userinfo == None:
                    count = len(data['addr'])
                else:
                    count = int(userinfo) + len(data['addr'])

                client.set(str(message.chat.id), str(count), 3600)
                await asyncio.sleep(1)
                new_user_count = client.get(str(message.chat.id))
                logger.debug("NEW USER COUNT:"+str(new_user_count))
            except Exception as e:
                logger.error(e)

            for host in data['addr']:
                logger.info(str(message.chat.id)+":"+str(host))
                try:
                    tmp = handler.getDetails(host)
                    msg_res += \
                        f"""Hostname: {get_host(tmp)}\nOrganization: {get_org(tmp)}\nIP:{tmp.ip}\nCity: {tmp.city}\nCountry:{tmp.country}\nRegion: {tmp.region}\n\n"""
                except requests.exceptions.HTTPError:
                    logger.error(str(message.chat.id)+":"+str(host))
                    await message.reply("Invalid host/ip: "+ host)
                except Exception as e:
                    whoid = message.chat.id
                    logger.error(f"{whoid}:{e}")

            try:
                await message.reply(msg_res)
                await state.finish()
            except MessageIsTooLong:
                await message.reply("Слишком много айпи в одном сообщении!\nДавай по очереди...")
            else:
                await state.finish()

if __name__ == "__main__":
    executor.start_polling(dp,skip_updates=True)
