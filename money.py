import pickle
import math




class Money():
    def __init__(self, dpl):
        self.dpl = dpl
        self.state = None
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
    def check_debt(self, name):
        f = open(self.dpl,'rb')
        data = pickle.load(f)['loan']
        f.close()
        if not name.lower() in data.keys():
            return 0
        return data[name.lower()]
    def report(self, content):
        content['message'] = '%s has %d NanoDollars.' %(dict['name'], self.check(dict['name'].lower()))
        return content
    def pay_debt(self, content):
        if len(content['message']) <= 5:
            content['message'] = 'Type $pay <amount>.'
            return content
        try:
            payment = math.ceil(int(content['message'][5:]))
            if payment < 1:
                content['message'] = 'Invalid number'
                return content
        except:
            content['message'] = 'That is not a number!'
            return content
        name = content['name'].lower()
        debt = self.check_debt(name)
        if debt < 1:
            content['message'] = 'You have no debt to pay!'
            return content
        money = self.check(name)
        f = open(self.dpl,'rb')
        data = pickle.load(f)
        f.close()
        #pay>money but money>debt, pay<money and pay>debt, pay<money but pay<debt, pay>money and pay<debt
        ###full payment###
        if payment >= debt and money > debt:
            money -= debt
            data['money'][name] = money
            del data['loan'][name]
            content['message'] = 'You have paid your debt in full and have %d NanoDollars left.' %(money)
            f = open(self.dpl,'wb')
            pickle.dump(data,f)
            f.close()
        ###partial payment###
        elif payment < debt and money > payment:
            money -= payment
            debt -= payment
            data['money'][name] = money
            data['loan'][name] = debt
            f = open(self.dpl,'wb')
            pickle.dump(data,f)
            f.close()
            content['message'] = 'You have made a partial payment of %d NanoDollars. You now have %d NanoDollars and %d NanoDollars of debt remaining.' %(payment, money, debt)
        else:
            content['message'] = 'Your payment has been rejected as you must have at least 1 NanoDollar remaining at the end of the transaction. (Beta: report bugs through !tell if you suspect that something is wrong, and include what happened.)'
        return content



    def set(self, name, amount):    #used for blackjack
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
    def loan(self, content):
        command = content['message']
        if self.state == None:
            self.recipient = content['name'].lower()
            if len(command) < 7:
                content['message'] = 'Type $loan <number>.' 
                return content,False
            try:
                self.loan_amount = math.ceil(int(command[6:]))
                if self.loan_amount > 50:
                    content['message'] = 'You cannot loan more than 50 NanoDollars!'
                    return content,False
                elif self.loan_amount < 1:
                    content['message'] = 'Minimum loan is 1 NanoDollar!'
                    return content,False
            except:
                content['message'] = 'That is not a number!'
                return content,False
            f = open(self.dpl,'rb')
            data = pickle.load(f)
            f.close()
            if self.recipient not in data['money'].keys():
                content['message'] = 'Create an account with $money first!'
                return content,False
            elif self.recipient in data['loan'].keys():
                content['message'] = 'You cannot $loan when you\'re in $debt!'
                return content,False
            self.money = data['money'][self.recipient]
            if self.money > 10:
                content['message'] = 'You do not need a $loan!'
                return content,False
            self.state = 'loan'
            content['message'] = 'You are taking a loan of %d NanoDollars, and will owe %d NanoDollars. Type Y/n to continue. (Note that going into debt heavily restricts your rights.)' %(self.loan_amount, math.ceil(self.loan_amount*1.1))
            self.timeout = 0
            return content,True
        elif self.state == 'loan':
            if not content['name'].lower() == self.recipient:
                if self.timeout < 15:
                    self.timeout += 1
                    return None,False
                else:
                    content['message'] = 'Transaction timed out.'
                    return content,True
            if command.lower() == 'n':
                content['message'] = 'Transaction cancelled.'
                return content,True
            elif command == 'Y':
                f = open(self.dpl,'rb')
                data = pickle.load(f)
                f.close()
                data['money'][self.recipient] += self.loan_amount
                data['loan'][self.recipient] = math.ceil(self.loan_amount*1.1)
                f = open(self.dpl,'wb')
                pickle.dump(data,f)
                f.close()
                content['message'] = 'Transaction complete.'
                return content,True
            elif command == 'y':
                content['message'] = 'For security reasons, you are required to capitilize your decision.'
                return content,False
            else:
                return None, False

        
