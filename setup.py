#from ConfigParser import ConfigParser as confp
import configparser
import sys
import os

# Constants
path = sys.path[0]
config = os.path.join(path, 'setup.cfg')

def channels(reader):
    chanlist = []
    channames = reader.get('channels', 'names').split(",")
    chanpass = reader.get('channels', 'password').split(",")
    for name,password in zip(channames,chanpass):
        dict = {'name':name,'password':password}
        chanlist.append(dict)
    return chanlist
####################################
    chandict = {}
    # Read in the channel names and passwords, separating them into lists
    channames = reader.get('channels', 'names').split(",")
    chanpass = reader.get('channels', 'password').split(",")
    for a in range(0,len(channames)):
        chandict[channames[a]] = chanpass[a]
    return chandict

def server(reader):
    # Read in the name of the bot and its password
    botname = reader.get('server', 'botname')
    botpass = reader.get('server', 'password')
    return botname,botpass

def email(reader):
    # Read in the email address and password of the user
    email = reader.get('email', 'address')
    emailpass = reader.get('email', 'password')
    return email,emailpass

def master(reader):
    # Read the nickname of the bot's master
    master = reader.get('master', 'nick')
    return master

def main():
    # Create the config reading object
    reader = configparser.ConfigParser()
    reader.read(config)
    chan = channels(reader)
    botname,botpass = server(reader)
    emailaddr,emailpass = email(reader)
    masternick = master(reader)
    configs = {'name':botname,'password':botpass, 'email':{'address':emailaddr,'password':emailpass}, 'master':masternick, 'channels':chan}
    return(configs)

if __name__ == '__main__':
    main()
