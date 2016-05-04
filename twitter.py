import urllib.request
import urllib.parse
import json
import oauth2 as oauth
import threading
import time
import pickle

'''inspired by https://raw.githubusercontent.com/uwescience/datasci_course_materials/master/assignment1/twitterstream.py '''

class Twitter(threading.Thread):
    def __init__(self, irc, tpl):
        threading.Thread.__init__(self)
        self.irc = irc
        self.tpl = tpl
        self.api_key = 'WiJMPiiEXSchOlHqbtXCNKQSV'
        self.api_secret = 'Fcb2nEPwupqc2bKkVEgOBMcJOiHTDcyz71uFazMO9QF5TW84nd'
        self.access_token_key = "2839460820-7E54B2kkY0kEeX1jYU6xEC4SIEkjYF1MxOZEObs"
        self.access_token_secret = "pbKjDh0GSpNpc3ua1wc97HXRNnD5FDXNbVcDAwDcP4jhI"
        self.signature_method_hmac_sha1 = oauth.SignatureMethod_HMAC_SHA1()
        self.http_method = "GET"
        self.url = "https://api.twitter.com/1.1/statuses/user_timeline.json"
        self.oauth_token = oauth.Token(key=self.access_token_key, secret=self.access_token_secret)
        self.oauth_consumer = oauth.Consumer(key=self.api_key, secret=self.api_secret)

        f = open(self.tpl, 'rb')
        self.data = pickle.load(f)
        f.close()


        self.dict_template = {'type':'PRIVMSG','channel': self.irc.master,'message':'','private_messaged':False}
        self.new_line_template = '\r\n%s %s :' %(self.dict_template['type'],self.dict_template['channel'])

    def run(self):
        while True:
            time.sleep(30)
            print('checking twitter...')
            try:
                buffer = '%s, you have unread tweets:' %(self.irc.master)
                new_tweets = 0
                for user in self.data.keys():
                    req = oauth.Request.from_consumer_and_token(self.oauth_consumer,
                                                token=self.oauth_token,
                                                http_method=self.http_method,
                                                http_url=self.url,
                                                parameters=self.data[user]['parameters'])
                    req.sign_request(self.signature_method_hmac_sha1, self.oauth_consumer, self.oauth_token)
                    url = req.to_url()
                    response = urllib.request.urlopen(url)
                    response = json.loads(response.read().decode())
                    max_id = 0
                    for a in response:
                        if a['id'] <= self.data[user]['id']:
                            break
                        if not a['in_reply_to_status_id']:
                            buffer += self.new_line_template + '%s: %s' %(a['user']['name'], a['text'])
                            new_tweets += 1
                            if a['id'] > max_id:
                                max_id = a['id']
                    if max_id > self.data[user]['id']:
                        self.data[user]['id'] = max_id
                if new_tweets > 0:
                    f = open(self.tpl, 'wb')
                    pickle.dump(self.data,f)
                    f.close()
                    dict = self.dict_template
                    dict['message'] = buffer
                    self.irc.send(dict)
                    print('sent')
            except:
                pass










'''

api_key = 'WiJMPiiEXSchOlHqbtXCNKQSV'
api_secret = 'Fcb2nEPwupqc2bKkVEgOBMcJOiHTDcyz71uFazMO9QF5TW84nd'
access_token_key = "2839460820-7E54B2kkY0kEeX1jYU6xEC4SIEkjYF1MxOZEObs"
access_token_secret = "pbKjDh0GSpNpc3ua1wc97HXRNnD5FDXNbVcDAwDcP4jhI"
signature_method_hmac_sha1 = oauth.SignatureMethod_HMAC_SHA1()
http_method = "GET"
url = "https://api.twitter.com/1.1/statuses/user_timeline.json"
parameters = {'screen_name':'nqrse', 'count':10}


oauth_token    = oauth.Token(key=access_token_key, secret=access_token_secret)
oauth_consumer = oauth.Consumer(key=api_key, secret=api_secret)

req = oauth.Request.from_consumer_and_token(oauth_consumer,
                                            token=oauth_token,
                                            http_method=http_method,
                                            http_url=url,
                                            parameters=parameters)
req.sign_request(signature_method_hmac_sha1, oauth_consumer, oauth_token)
headers = req.to_header()
print(headers)
url = req.to_url()
print(url)

response = urllib.request.urlopen(url)#, urllib.parse.urlencode(parameters).encode())
response = json.loads(response.read().decode())

for a in response:
    print(a['user']['name'], a['text'])
'''
'''
f = open('tweets.txt','wb')
for a in response:
    print('entered')
    string = str(a['user']['name'] + a['text']+'\r\n').encode()
    f.write(string)
f.close()
'''

