import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import pickle

'''
Known issue: Bot will return Buffer = None in self.loop() if self.data['feed']
is so outdated that it doesn't appear in the RSS xml.

If that happens, manually replace self.data['feed'] with a newer string.
'''



class ANN():
    def __init__(self,irc,annpl):
        self.irc = irc
        self.annpl = annpl
        self.url = "http://www.animenewsnetwork.com/all/rss.xml"
        self.content_template = {'type':'PRIVMSG','channel': self.irc.master,'message':'','private_messaged':False}
        self.new_line_template = '\r\n%s %s :' %(self.content_template['type'],self.content_template['channel'])

        f = open(self.annpl, 'rb')
        self.data = pickle.load(f)
        f.close()
    def loop(self, tree):
        buffer = '%s, you have new ANN posts:' %(self.irc.master)
        new_posts = 0
        feed_number = 1
        for a in tree:
            for feed in a.iter("item"):
                if feed.find("title").text == self.data['feed']:
                    print('same')
                    if new_posts == 0:
                        return None
                    elif new_posts != 0:
                        self.data['feed'] = latest_feed
                        f = open(self.annpl,'wb')
                        pickle.dump(self.data,f)
                        f.close()
                        return buffer
                else:
                    buffer += self.new_line_template + feed.find("title").text
                    new_posts += 1

                    #Update save-file to most recent feed if this is most recent.
                    if feed_number == 1:
                        latest_feed = feed.find('title').text
                    feed_number += 1
    def run(self):
        print('checking ANN\'s RSS feed...')
        try:
            response = urllib.request.urlopen(self.url)
            response= response.read().decode()
            tree = ET.fromstring(response)
            buffer = self.loop(tree)
            if not buffer == None:
                content = self.content_template
                content['message'] = buffer
                self.irc.send(content)
        except Exception as e:
            print(e)
