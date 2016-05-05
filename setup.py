from ConfigParser import ConfigParser as confp
import sys
import os

# Constants
path = sys.path[0]
config = os.path.join(path, 'setup.cfg')

def channels(reader):
    chandict = {}
    # Read in the channel names and passwords, separating them into lists
    channames = reader.get('channels', 'names').split(",")
    chanpass = reader.get('channels', 'password').split(",")
    for a in range(0,len(channames)):
        chandict[channames[a]] = chanpass[a]
    return chandict

def server(reader):
    # Read in the name of the bot and its password
    bot = reader.get('server', 'botname')
    botpass = reader.get('server', 'password')
    return {bot:botpass}

def email(reader):
    # Read in the email address and password of the user
    email = reader.get('email', 'address')
    emailpass = reader.get('email', 'password')
    return {email:emailpass}

def main():
    # Create the config reading object
    reader = confp()
    reader.read(config)
    chan = channels(reader)
    botserv = server(reader)
    emailinf = email(reader)

if __name__ == '__main__':
    main()
