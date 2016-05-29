import pickle


class NDAcademy():
    def __init__(self,emailer,ndapl,irc):
        self.emailer = emailer
        self.ndapl = ndapl
        self.irc = irc
        self.commandlist = []

    def execute(self):
        pass
    def is_a_valid_command(self, message):
        found = False
        for command in self.commandlist:
            if message.startswith(command):
                found = True
                break
        return found
    def check_attendance(self, namelist):
        #Just in case bot didn't join ND Academy channel
        if not '#ndacademy' in namelist.keys():
            return






