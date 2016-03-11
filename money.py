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
    def report(self, dict):
        dict['message'] = '%s has %d NanoDollars.' %(dict['name'], self.check(dict['name'].lower()))
        return dict
    def pay_debt(self, dict):
        if len(dict['message']) <= 5:
            dict['message'] = 'Type $pay <amount>.'
            return dict
        try:
            payment = math.ceil(int(dict['message'][5:]))
            if payment < 1:
                dict['message'] = 'Invalid number'
                return dict
        except:
            dict['message'] = 'That is not a number!'
            return dict
        name = dict['name'].lower()
        debt = self.check_debt(name)
        if debt < 1:
            dict['message'] = 'You have no debt to pay!'
            return dict
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
            dict['message'] = 'You have paid your debt in full and have %d NanoDollars left.' %(money)
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
            dict['message'] = 'You have made a partial payment of %d NanoDollars. You now have %d NanoDollars and %d NanoDollars of debt remaining.' %(payment, money, debt)
        else:
            dict['message'] = 'Your payment has been rejected as you must have at least 1 NanoDollar remaining at the end of the transaction. (Beta: report bugs through !tell if you suspect that something is wrong, and include what happened.)'
        return dict



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
    def loan(self, dict):
        command = dict['message']
        if self.state == None:
            self.recipient = dict['name'].lower()
            if len(command) < 7:
                dict['message'] = 'Type $loan <number>.' 
                return dict,False
            try:
                self.loan_amount = math.ceil(int(command[6:]))
                if self.loan_amount > 50:
                    dict['message'] = 'You cannot loan more than 50 NanoDollars!'
                    return dict,False
                elif self.loan_amount < 1:
                    dict['message'] = 'Minimum loan is 1 NanoDollar!'
                    return dict,False
            except:
                dict['message'] = 'That is not a number!'
                return dict,False
            f = open(self.dpl,'rb')
            data = pickle.load(f)
            f.close()
            if self.recipient not in data['money'].keys():
                dict['message'] = 'Create an account with $money first!'
                return dict,False
            elif self.recipient in data['loan'].keys():
                dict['message'] = 'You cannot $loan when you\'re in $debt!'
                return dict,False
            self.money = data['money'][self.recipient]
            if self.money > 10:
                dict['message'] = 'You do not need a $loan!'
                return dict,False
            self.state = 'loan'
            dict['message'] = 'You are taking a loan of %d NanoDollars, and will owe %d NanoDollars. Type Y/n to continue. (Note that going into debt heavily restricts your rights.)' %(self.loan_amount, math.ceil(self.loan_amount*1.1))
            self.timeout = 0
            return dict,True
        elif self.state == 'loan':
            if not dict['name'].lower() == self.recipient:
                if self.timeout < 15:
                    self.timeout += 1
                    return None,False
                else:
                    dict['message'] = 'Transaction timed out.'
                    return dict,True
            if command.lower() == 'n':
                dict['message'] = 'Transaction cancelled.'
                return dict,True
            elif command == 'Y':
                f = open(self.dpl,'rb')
                data = pickle.load(f)
                f.close()
                data['money'][self.recipient] += self.loan_amount
                data['loan'][self.recipient] = math.ceil(self.loan_amount*1.1)
                f = open(self.dpl,'wb')
                pickle.dump(data,f)
                f.close()
                dict['message'] = 'Transaction complete.'
                return dict,True
            elif command == 'y':
                dict['message'] = 'For security reasons, you are required to capitilize your decision.'
                return dict,False
            else:
                return None, False

        
