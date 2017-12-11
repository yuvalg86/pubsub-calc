# pubsub-calc

basic calculator using redis pub-sub.

# prereqs
* pip install docopt redis
* working redis server on localhost:6379 [should be args in next version]

# usage
  PubSubCalc.py [test]
receives input on 'input' channel (using Redis pub/sub), legal input would be '+ 2 3', '* 4 2'....
calculates and publishes the result to 'output' channel.

in order to kill it - publish 'DIE' into the 'input' channel.



*was developed and tested on WIN32 machine.*
