# pubsub-calc

basic calculator using redis pub-sub.
receives input on 'input' channel (using Redis pub/sub), legal input would be '+ 2 3', '* 4 2'....
calculates and publishes the result to 'output' channel.

in order to kill it - publish 'DIE' into the 'input' channel.

#prereqs - 
pip install docopt redis
working redis server on localhost:6379

# usage
  PubSubCalc.py [test]
  



# was developed and tested on WIN32 machine.
