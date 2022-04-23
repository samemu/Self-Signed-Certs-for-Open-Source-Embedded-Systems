#Here is a script to automate the API requests for the registration server
#this script will require super powers as i have not confiured certbot to run in a safe space
#also, this script does not make use of the certbot library so you must have certbot installed on the local machine
#the certbot library seems like it may be difficult to use so i opted for the approach where i run certbot through popen
#whilst certbot is running, we utilize a manual authentication hook to grab the DNS TXT record challenge and upload this to the registration server
#if i have time i would like to step away from running certbot and utilize the certbot library
#I am not a good programmer so please dont judge my usage of hacks and various other things to beat this beast into shape :D
#the code is mostly undocumented but relatively simple.
#you need authenitcate.sh, CertbotSubTest.py, and this "regApi.py" all in the same directory


import subprocess
import os
import requests

#some global things
certEmail = "cmccoy5@emich.edu"
authDomain = "https://api.cmccoy1.click:8443"
domain = ".cmccoy1.click"

#a listing of all the API endpoints being utilized by the script's libraries
urlStr = {
    "subscribe": "/subscribe",      #subscribes a new name to your domain, requires a name and returns the domain token. we can also set various descriptors and modes here
    "unsubscribe": "/unsubscribe",  #removes an endpoint from your domain, requires the domain token and optionally the reclamation token
    "check": "/connectivity-check", #tests the connectivity of the domains, requires nothing
    "dnsconfig": "/dnsconfig",      #configures the Let's Encrypt DNS challenge, requires the domain token and the TXT challenge from Let's Encrypt
    "info": "/info",                #retrieves a json representation of the domain, requires the domain token
    "reclaim": "/reclaim",          #reclaims a domain, requires the name of the domain to be reclaimed
    "ping": "/ping",                #pings the domain, requires the domain token
    "setemail": "/setemail",        #sets the email, requires the domain token and the email address
    "verify": "/verifyemail",       #verify emails, requires verification uuid
    "revoke": "/revokeemail",       #revoke emails, requires domain token
}

#subs a domain
def subscribeDomain(subName):
    payload = {'name': subName}
    r = requests.get(authDomain + urlStr["subscribe"], params=payload)
    status = r.status_code
    data = r.json()
    regToken = data["token"]
    return status, regToken

#unsubs a domain
def unsubscribeDomain(regToken):
    payload = {"token": regToken}
    r = requests.get(authDomain + urlStr["unsubscribe"], params=payload)
    return r.status_code

#configures DNS challenge
def dnsConfig(regToken,challenge):
    payload = {"token": regToken, "challenge": challenge}
    requests.get(authDomain + urlStr["dnsconfig"], params=payload)

#retireves info about domain
def getInfo(regToken):
    payload = {"token": regToken}
    r = requests.get(authDomain + urlStr["info"], params=payload)
    return r.json()

#pings the domain
def pingDomain(regToken):
    payload = {"token": regToken}
    r = requests.get(authDomain+urlStr["ping"], params=payload)
    return r.status_code

#sets an email for the domain
def setEmail(regToken, email):
    payload = {"token": regToken, "email": email}
    r = requests.get(authDomain + urlStr["setemail"], params=payload)
    return r.status_code

#i dont have a good idea of what this really means by uuid but im going to implement it anyway
def verifyEmail(sVer):
    payload = {"s": sVer}
    r = requests.get(authDomain + urlStr["verify"], params=payload)
    return r.status_code

#revokes an email
def revokeEmail(regToken):
    payload = {"token": regToken}
    r = requests.get(authDomain + urlStr["revoke"],params=payload)
    return r.status_code

#reclaims a domain
def reclaimDomain(name):
    payload = {"name": name}
    r = requests.get(authDomain + urlStr["reclaim"], params=payload)
    return r.status_code


if __name__ == "__main__":
    subName = input("Enter a name for the subdomain you wish to register: ")
    print("registering: " + subName + domain)

    #register our domain
    status, regToken = subscribeDomain(subName)

    print("NAME: " + str(subName) + "\n" + "TOKEN: " + str(regToken) + "\n" + "STATUS: " + str(status))

    #write the registration token for later use with DNS config
    with open("regtoken.txt","w") as f:
        f.write(regToken)

    #this is to grab our work directory as all out scripts should live here with us
    pwd = os.getcwd()
    authHook = pwd + "/authenticate.sh"

    #this the meat and potatoes of the DNS config portion
    #retrieves the TXT challenge for the DNS challenge
    runCMD = subprocess.Popen(
        ["certbot", "--text", "--agree-tos", "--email", certEmail, "-d", subName + domain,
         "--preferred-challenge", "dns", "--manual", "--manual-auth-hook",
         authHook, "--expand", "--renew-by-default",
         "--manual-public-ip-logging-ok", "certonly"])