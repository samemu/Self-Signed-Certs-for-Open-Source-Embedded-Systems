#grab the TXT token
echo "$CERTBOT_VALIDATION" > token.txt

#call a separate script to run the dnsConfig function from regApi.py
python3 "$PWD/CertbotSubTest.py"
