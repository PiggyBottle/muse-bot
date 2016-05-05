import pickle

def main():
    data = {}
    print('Welcome to startup manager!')
    print('This setup will create the essential pickle files for Muse-chan to run properly.')
    print('First, let\'s setup \"config.pickle\", which holds information for Muse-chan to join IRC channels and authenticate herself. Do you want to continue?')
    answer = input('y/n\n')
    if not answer == 'n':
        config()

def config():
    for a in range(5):
        print()
    config = {}
    name = input('What do you want the bot\'s name to be?\n')
    password = input('What is its nickserv password?\n')
    master = input('What is the nick of the bot\'s master? (Your personal nick)\n')
    email_address = input('What is the email address that the bot will use? (Blank if none)\n')
    email_password = input('What is the password for the email address? (Blank if none)\n')
    no_of_channels = int(input('How many channels will the bot join?\n'))
    config['channels'] = []
    for a in range(no_of_channels):
        channel = {}
        channel_name = input('What is the name of the channel?\n')
        channel_password = ''
        channel_password = input('What is the password? (blank if none)\n')
        channel['name'] = channel_name
        channel['password'] = channel_password
        config['channels'].append(channel)
    for a in range(5):
        print()
    print('Please confirm the following details:')
    print('Name: %s' %(name))
    print('Password: %s' %(password))
    print('Master : %s' %(master))
    print('Email address: %s' %(email_address))
    print('Email password: %s' %(email_password))
    for a in config['channels']:
        print('Channel name: %s, Password: %s' %(a['name'], a['password']))
    confirmation = input('Is that all? Type \'n\' to restart.\n')
    if not confirmation == 'n':
        config['name'] = name
        config['password'] = password
        config['master'] = master
        config['email'] = {}
        config['email']['address'] = email_address
        config['email']['password'] = email_password
        f = open('config.pickle', 'wb')
        pickle.dump(config,f)
        f.close()
        input('Done!')
        for a in range(5):
            print()
        return










if __name__ == '__main__':
    main()



