#!/usr/bin/env python3
""" PubSub Calculator
Usage:
  PubSubCalc.py [test]
  PubSubCalc.py (-h | --help)
Options:
  -h, --help, --test
"""
from docopt import docopt
import redis
import threading
import time
import signal

INPUT_CHANNEL = 'input'
RESULT_CHANNEL = 'output'
SUPPORTED_OPS = ['+', '-', '*', '/']
KILL_CMD = 'DIE'
REDIS_HOST = 'localhost'
REDIS_PORT = 6379


class Listener(threading.Thread):
    def __init__(self, conn, channel):
        try:
            threading.Thread.__init__(self)
            self.redis = conn
            self.pubsub = self.redis.pubsub()
            self.subscribe_and_check(channel)
        except Exception as e:
            print('error on thread init.', e)

    def subscribe_and_check(self, channel):
        self.pubsub.subscribe(channel)
        # check subscption
        res = self.pubsub.get_message()
        while res is None:
            time.sleep(0.001)
            res = self.pubsub.get_message()
        if res['data'] < 1:
            raise Exception('error subscribing to channel', channel)
        print('started Listener on', channel)

    @staticmethod
    def check_and_parse_input(data):
        if len(data) != 3:
            raise Exception('illegal number of args')
        if data[0] not in SUPPORTED_OPS:
            raise Exception('illegal operator. allowed:' + str(SUPPORTED_OPS))
        try:
            float(data[1])
            float(data[2])
        except ValueError as v:
            raise Exception('illegal arg')
        result = '{} {} {}'.format(data[1], data[0], data[2])
        return result

    def calc(self, data):
        # this part could be a switch case or map... which might be more safe.
        # wasnt sure what is prefered by you - thus did what I prefered:
        # more general than restricted yet with some safety checks.
        try:
            # remove multiple and trailing spaces
            input_args = ' '.join(data.split()).strip()
            args = Listener.check_and_parse_input(input_args.split(' '))
            if args:
                result = eval(args)
                res = self.redis.publish(RESULT_CHANNEL, result)
                if (res != 1):
                    raise Exception('error publishing result to channel')
        except Exception as e:
            print('cant calc input msg', data, 'error:', e)

    def exit_gracefully(self):
        print (self, "received kill cmd")
        self.pubsub.unsubscribe()
        self.pubsub.close()

    def run(self):
        try:
            for item in self.pubsub.listen():
                # print (item)
                if (item['type'] != 'message'):
                    continue
                data = str(item['data'], 'utf-8')
                if data == KILL_CMD:
                    self.exit_gracefully()
                    break
                else:
                    self.calc(data)
        except Exception as e:
                print ('error on listener')
                self.exit_gracefully()


def main(args):
    try:
        conn = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
        client = Listener(conn, [INPUT_CHANNEL])
        client.start()
    except Exception as e:
        print('error connecting to REDIS server.', e)
    if (args['test']):
        try:
            print('sanity (legal input), no output should be printed')
            conn.publish('input', '+    15.5  5')
            conn.publish('input', '-   15.7 0.7 ')
            conn.publish('input', '* -3   5')
            conn.publish('input', '/ 30  5')
            print('illegal input')
            conn.publish('input', '! 2 2')
            conn.publish('input', 'a   2  4   ')
            conn.publish('input', '+ 2 self')
            conn.publish('input', '+   a  4   ')
            conn.publish('input', KILL_CMD)
        except Exception as e:
            print('runtime error occured', e)


if __name__ == "__main__":
    arguments = docopt(__doc__)
    main(arguments)
