import ircmodule
import statemanager
import setup


'''
###android file paths###
dpl = '/storage/emulated/0/com.hipipal.qpyplus/scripts3/muse-bot/data.pickle'
lpl = '/storage/emulated/0/com.hipipal.qpyplus/scripts3/muse-bot/logs.pickle'
tpl = '/storage/emulated/0/com.hipipal.qpyplus/scripts3/muse-bot/twitter.pickle'
'''
dpl = 'data.pickle'
lpl = 'logs.pickle'
tpl = 'twitter.pickle'
annpl = 'ann.pickle'

config = setup.main()


irc = ircmodule.IRC(config)
irc.start()
sm = statemanager.StateManager(config,irc,dpl,lpl,tpl,annpl)    #putting irc object in to support the use of the irc.send() function in threads
while True:
    dict = irc.inputs.get()
    irc.send(sm.main(dict))
