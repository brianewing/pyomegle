import time, webbrowser, random
from omegle import Omegle, OmegleHandler

class ExampleBot(OmegleHandler):
    random_words = ('yourself', 'too', 'lol', 'moo')
    def message(self, message):
        timestamp = time.strftime('%H:%M:%S')
        print '[%s] Stranger: %s' % (timestamp, message)
        
        message_parts = message.split()
        if len(message_parts) <= 2:
            message_send = ' '.join(message_parts) + '!'
            message_send = message_send.capitalize()
        else:
            message_parts = message_parts[:-1]
            last_word = random.choice(self.random_words)
            if message[-1:] in ('?', '!', ')', '"', "'"):
                last_word += message[-1:]
            message_parts.append(last_word)
            message_send = ' '.join(message_parts)
        self.omegle.say(message_send)
        print '[%s] Me: %s' % (timestamp, message_send)
    
    def disconnected(self):
        print '=> Stranger disconnected! :-('
        raw_input('=> Press enter for a new stranger...')
        self.omegle.next()
    
    def captcha_required(self):
        print '=> Omegle wants a captcha, launching browser...'
        webbrowser.open('http://www.omegle.com')
    
    def waiting(self):
        print '=> Waiting for a stranger...'
    
    def connected(self):
        print '=> Connected to a stranger'

if __name__ == '__main__':
    event_handler = ExampleBot()
    omegle = Omegle(event_handler)
    print '=> Running'
    try:
        omegle.start_chat()
    except KeyboardInterrupt:
        print '=> Bye bye'
        omegle.disconnect()