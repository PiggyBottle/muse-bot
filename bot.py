import ircmodule
import statemanager

irc = ircmodule.IRC()
irc.start()
sm = statemanager.StateManager(irc)    #putting irc object in to support the use of the irc.send() function in threads

while True:
    dict = irc.inputs.get()
    irc.send(sm.main(dict))
    
