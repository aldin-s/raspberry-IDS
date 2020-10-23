path_validMacs = path_logs+"knownMACs.lan"
path_newMacs = path_logs+"discoveredMACs.lan.log"

config = ConfigParser.RawConfigParser()
config.read('ids.cfg')
fromEmail = config.get('Config', 'fromEmail')
toEmail = config.get('Config', 'toEmail')
pwd = config.get('Config', 'pwd')
smtpServer = config.get('Config', 'smtpServer')
smtpPort = config.get('Config', 'smtpPort')

cmd_discoverdMacs= """sudo arp-scan -l | sed '1,2d' | head --lines=-3 | awk ' { print $2,$1,$3} ' """
hostname = socket.gethostname()

def sendMail(toMail,msg, subject):
        smtp = smtplib.SMTP(smtpServer, smtpPort)
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login(fromEmail, pwd)
	      header = "To: %s\nFrom: %s\nSubject:%s\n" % (toMail, fromEmail, subject)
        smtp.sendmail(fromEmail, toMail, header+msg)
        smtp.quit()

def main():

	subject="New MACs discovered"
        t=time.strftime("%d-%m-%Y %X")

	with open(path_validMacs) as f:
		lines = f.read().splitlines()

	validMacs = map (lambda x: x.upper(),  lines)
	
	(stdout, stderr) = Popen(cmd_discoverdMacs, stdout=PIPE, shell=True).communicate()
	discoverdMacs=stdout.split()	
	
	macIpVendor={}	

	for idx, elem in enumerate(discoverdMacs):
		if (idx%3==0):
			macIpVendor[elem.upper()]=[discoverdMacs[idx+1], discoverdMacs[idx+2]]	

	discoverdMacs = macIpVendor.keys()
	newMacs=[]

	with open(path_newMacs, 'a') as fLog:
		for x in discoverdMacs:
			if x not in validMacs:
				fLog.write('%s %s %s %s \n'%(t, x, macIpVendor[x][0], macIpVendor[x][1]))
				newMacs.append("\t".join([x, macIpVendor[x][0], macIpVendor[x][1]]))
	
	strNewMacs="MAC\tIP\tVendor"+"\n"+'\n'.join(newMacs)

	if (len(newMacs)>0):
		sendMail(toEmail,"\n".join(["%s discovered new MACs on %s"%(hostname, t),"", strNewMacs]),subject)
	

if __name__ == "__main__":
    main()
