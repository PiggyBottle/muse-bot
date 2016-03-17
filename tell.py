import pickle


class Tell():
    def __init__(self):
        f = open('tell.pickle', 'rb')
        self.data = pickle.load(f)
        f.close()
    def write(self, dict):
        if len(dict['message'].split()) < 3:
            dict['message'] = 'Use !tell <recipient> <message>.'
            return dict
        name = dict['message'].split()[1]
        if name == '':
            return
        message = dict['message'].split(' ',2)[2]
        tell = {'message':message,'sender':dict['name']}
        if name not in self.data.keys():
            self.data[name.lower()] = []
        self.data[name.lower()].append(tell)
        f = open('tell.pickle', 'wb')
        pickle.dump(self.data,f)
        f.close()
        dict['message'] = 'Message registered.'
        return dict
    def check(self,dict):
        buffer = '%s, you have unread messages.' %(dict['name'])
        unread_messages = 0
        names_to_delete = []
        newline = '\r\n%s %s :' %(dict['type'],dict['channel'])
        for name in self.data.keys():
            if name in dict['name'].lower():
                for tell in self.data[name]:
                    buffer += newline + '%s : %s' %(tell['sender'],tell['message'])
                    unread_messages += 1
                    if not name in names_to_delete:
                        names_to_delete.append(name)
        for a in names_to_delete:
            del self.data[a]
        if unread_messages > 0:
            dict['message'] = buffer
            f = open('tell.pickle','wb')
            pickle.dump(self.data,f)
            f.close()
            return True,dict
        else:
            return False,dict

