import telepot
import random
import time
import os

import netifaces
import re
from time import gmtime, strftime
from textwrap import dedent

from subprocess import PIPE, Popen

from json import load
from urllib2 import urlopen

import logging

try:
	### load config file from current directory
	config = load(open('config_home_bot.json'))

	### allowed chat IDs
	lubent_chatID = config["allowed_telegram_chat_id"]

	### create Telegram bot
	bot = telepot.Bot(config["telegram_bot_key"])

except Exception as e:
	print(e)

def risp(msg):
	chat_id = msg['chat']['id']
	sender = msg['from']
	sender_id = msg['from']['id']
	sender_username = msg['from']['username']
	sender_firstname = msg['from']['first_name']
	sender_lastname = msg['from']['last_name']
	cmd = msg['text']

	if sender['id'] != int(lubent_chatID):
		logging.warning('Unauthorized user tryed to access to TorrentBot. TelegramID=%s - %s %s (%s)', sender_username, sender_firstname, sender_lastname, sender_id)
		bot.sendMessage(chat_id, "You are not allowed to use this bot")
		Termination()

	if cmd == '/start':
		Start(msg)
	elif cmd == '/help':
		PrintHelp(msg)
	elif cmd == '/random':
		AskRandom(msg)
	elif cmd == '/showPrivateIP':
		ShowPrivateIp(msg)
	elif cmd == '/showPublicIP':
		ShowPublicIp(msg)
	elif cmd == '/torrents':
		TorrentList(msg)
	elif cmd == '/shutdown':
		ShutdownHomeServer(msg)
	elif cmd == '/reboot':
		RebootHomeServer(msg)
	elif cmd == '/torrentStart':
		StartTorrentService(msg)
	elif cmd == '/torrentStop':
		StopTorrentService(msg)
	elif cmd == '/statistics':
		TorrentServiceStatistics(msg)
	elif cmd == '/whoami':
		WhoAmI(msg)
	elif cmd == '/chat_id':
		ChatID(msg)
	elif cmd == '/tortoiseON':
		AlternativeSpeedON(msg)
	elif cmd == '/tortoiseOFF':
		AlternativeSpeedOFF(msg)
	else:
		UnknownCommand(msg)

def Start(msg):
	chat_id = msg['chat']['id']
	sender = msg['from']
	logging.info('%s(%s) started a new chat with Lubent Home Bot', sender['username'], sender['id'])
	bot.sendMessage(chat_id, "Welcome")
	bot.sendMessage(chat_id, "Use /help to print menu")

def cmdline(command):
    process = Popen(
        args=command,
        stdout=PIPE,
        shell=True
    )
    return process.communicate()[0]

def PrintHelp(msg):
	chat_id = msg['chat']['id']
	sender = msg['from']
	h = dedent("""Menu for Lubent Home Bot:
	/help prints help menu
	/random for a random number
	/showPrivateIP LAN IP
	/showPublicIP public IP
	/whoami your username\n
	/chat_id your Telegram chatID\n
	/dashListenerON for Dash Buttons
	/dashListenerOFF for Dash Buttons\n
	/switchandoON web server
	/switchandoOFF web server\n
	/reboot home server
	/shutdown home server""")
	bot.sendMessage(chat_id, h)
	logging.info('%s(%s) printed help menu', sender['username'], sender['id'])

def UnknownCommand(msg):
	chat_id = msg['chat']['id']
	sender = msg['from']
	bot.sendMessage(chat_id, "I don't know this command")
	logging.error('%s(%s) typed unknown command: "%s"', sender['username'], sender['id'], msg['text'])

def AskRandom(msg):
	chat_id = msg['chat']['id']
	sender = msg['from']
	number = random.randint(1,1000)
	bot.sendMessage(chat_id, number)
	logging.info('%s(%s) asked a new random number: %s', sender['username'], sender['id'], str(number))

def ShowPrivateIp(msg):
	chat_id = msg['chat']['id']
	sender = msg['from']
	netifaces.ifaddresses('eth0')
	ip = netifaces.ifaddresses('eth0')[2][0]['addr']
	bot.sendMessage(chat_id, "The torrent server is connected at " + ip)
	logging.info('%s(%s) read telegram server PrivateIP: %s', sender['username'], sender['id'], ip)

def ShowPublicIp(msg):
	chat_id = msg['chat']['id']
	sender = msg['from']
	ip = load(urlopen('http://httpbin.org/ip'))['origin']
	bot.sendMessage(chat_id, "The torrent server is connected at " + ip)
	logging.info('%s(%s) read telegram server PublicIP: %s', sender['username'], sender['id'], ip)

def WhoAmI(msg):
	chat_id = msg['chat']['id']
	sender = msg['from']
	bot.sendMessage(chat_id, "You are " + sender['first_name'] + " (" + sender['username'] + ")")
	logging.info('%s(%s) asked his/her name: %s %s', sender['username'], sender['id'], sender['first_name'], sender['last_name'])

def ChatID(msg):
	chat_id = msg['chat']['id']
	sender = msg['from']
	bot.sendMessage(chat_id, "Your chatID is " + str(chat_id))
	logging.info('%s(%s) asked his/her chatID: %s', sender['username'], sender['id'], str(chat_id))

def ShutdownHomeServer(msg):
	chat_id = msg['chat']['id']
	sender = msg['from']

	try:
		bot.sendMessage(chat_id, "Shutting down...")
		logging.info('%s(%s) shutdown Home server', sender['username'], sender['id'])
		os.system("sudo shutdown now")

	except Exception, e:
		print("Exception generated while shutting down: " + str(e))
		bot.sendMessage(chat_id, "Operation failed")
		logging.error('%s(%s) tried to shutdown Home server but operation failed: %s', sender['username'], sender['id'], str(e))

def RebootHomeServer(msg):
	chat_id = msg['chat']['id']
	sender = msg['from']

	try:
		bot.sendMessage(chat_id, "Rebooting...")
		logging.info('%s(%s) reboot Home server', sender['username'], sender['id'])
		os.system("sudo reboot now")

	except Exception, e:
		print ("Exception generated while rebooting: " + str(e))
		bot.sendMessage(chat_id, "Operation failed")
		logging.error('%s(%s) tried to reboot Home server but operation failed: %s', sender['username'], sender['id'], str(e))

def Termination():
	quit()

def main():
	try:
		### create logger
		logging.basicConfig(filename='homeBot.log', format='%(asctime)s - %(levelname)s: %(message)s', level=logging.INFO)
		logging.info('Home server turned ON')

		bot.sendMessage(lubent_chatID, "Home server turned ON")
		bot.message_loop(risp)

		while 1:
			time.sleep(10)

	except KeyboardInterrupt:
		### to intercept CTRL+C interrupt
		logging.info('Home server turned OFF with keyboard interrupt')
		print("\nQuitting...")
	except Exception, e:
		logging.error('Runtime Exception: ' + str(e))

if __name__ == "__main__":
	main()
