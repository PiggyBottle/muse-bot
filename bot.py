import ircmodule
import statemanager

###file paths###
dpl = 'D:\Documents\muse-bot\data.pickle'
lpl = 'D:\Documents\muse-bot\logs.pickle'


irc = ircmodule.IRC()
irc.start()
sm = statemanager.StateManager(irc,dpl,lpl)    #putting irc object in to support the use of the irc.send() function in threads

while True:
    dict = irc.inputs.get()
    irc.send(sm.main(dict))
    
