import os
import regApi as regAPI

#read in the DNS token
with open("token.txt","r") as f:
    token = f.read()
token = token[:len(token)-1]

#read in the registration token
with open("regtoken.txt","r") as f:
    regtoken = f.read()

#pass information to the api call
regAPI.dnsconfig(regtoken,token)

#remove artifacts
os.remove("token.txt")
os.remove("regtoken.txt")

