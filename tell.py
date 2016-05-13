import pickle


class Tell():
    def __init__(self):
        f = open('tell.pickle', 'rb')
        self.data = pickle.load(f)
        f.close()
    def write(self, content):
        if len(content['message'].split()) < 3:
            content['message'] = 'Use !tell <recipient> <message>.'
            return content
        name = content['message'].split()[1]
        if name == '':
            return
        message = content['message'].split(' ',2)[2]
        tell = {'message':message,'sender':content['name']}
        if name not in self.data.keys():
            self.data[name.lower()] = []
        self.data[name.lower()].append(tell)
        f = open('tell.pickle', 'wb')
        pickle.dump(self.data,f)
        f.close()
        content['message'] = 'Message registered.'
        return content
    def check(self,content):
        buffer = '%s, you have unread messages.' %(content['name'])
        unread_messages = 0
        names_to_delete = []
        newline = '\r\n%s %s :' %(content['type'],dict['channel'])
        for name in self.data.keys():
            if name in content['name'].lower():
                for tell in self.data[name]:
                    buffer += newline + '%s : %s' %(tell['sender'],tell['message'])
                    unread_messages += 1
                    if not name in names_to_delete:
                        names_to_delete.append(name)
        for a in names_to_delete:
            del self.data[a]
        if unread_messages > 0:
            content['message'] = buffer
            f = open('tell.pickle','wb')
            pickle.dump(self.data,f)
            f.close()
            return True,content
        else:
            return False,content

