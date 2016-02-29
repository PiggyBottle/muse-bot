import pickle





class Money():
    def __init__(self, dpl):
        self.dpl = dpl
    def check(self, name):
        #remember to input name in .lower()
        f = open(self.dpl,'rb')
        data = pickle.load(f)['money']
        f.close()
        if name.lower() in data.keys():
            return data[name.lower()]
        else:
            f = open(self.dpl,'rb')
            data = pickle.load(f)
            f.close()
            data['money'][name.lower()] = 10
            f = open(self.dpl,'wb')
            pickle.dump(data,f)
            f.close()
            return 10
    def report(self, dict):
        dict['message'] = '%s has %d NanoDollars.' %(dict['name'], self.check(dict['name'].lower()))
        return dict
    def set(self, name, amount):
        if amount < 0:
            return
        f = open(self.dpl,'rb')
        data = pickle.load(f)
        f.close()
        if name.lower() in data['money'].keys():
            data['money'][name.lower()] = amount
            f = open(self.dpl,'wb')
            pickle.dump(data,f)
            f.close()
