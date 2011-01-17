import urllib
import urllib2
import time

try:
    import json
except ImportError:
    import simplejson as json

__author__ = 'Brian Ewing'
__version__ = 0.1

class Omegle:
    """ Class for interfacing with Omegle using its HTTP API """
    
    omegle_id = ''
    event_handler = None
    event_loop_running = False
    
    start_url = 'http://promenade.omegle.com/start?rcs=1'
    say_url = 'http://promenade.omegle.com/send'
    events_url = 'http://promenade.omegle.com/events'
    captcha_url = 'http://promenade.omegle.com/recaptcha'
    disconnect_url = 'http://promenade.omegle.com/disconnect'
    
    def __init__(self, event_handler):
        self.event_handler = event_handler
        self.event_handler._set_omegle(self)
    
    def _post_data(self, **kwargs):
        return urllib.urlencode(kwargs)
    
    def _request(self, url, **kwargs):
        if kwargs:
            post_data = self._post_data(**kwargs)
        else:
            post_data = None

        request = urllib2.urlopen(url, post_data)
        response = request.read()
        try:
            response = json.loads(response)
        except ValueError:
            pass
        request.close()
        return response
    
    def start(self):
        """ Start a chat with a random stranger and start polling for events """
        
        omegle_id = self._request(self.start_url)
        self.omegle_id = omegle_id
        if omegle_id:
            self.event_loop()
            self.omegle_id = omegle_id
            return self.omegle_id
        else:
            self.omegle_id = None
            return False
    
    start_chat = start
    
    def disconnect(self):
        """ Tell the Omegle server we want to disconnect and stop polling for events """
        
        if self.omegle_id:
            try:
                self._request(self.disconnect_url, id=self.omegle_id)
            except urllib2.HTTPError:
                pass # Omegle returns an HTTP 404 when already disconnected
            self.omegle_id = None
        self.event_loop_running = False
        return True
    
    def next(self):
        """ Disconnect the current chat (if any) and start a new one """
        
        self.disconnect()
        self.start()
    
    def say(self, message):
        """ Send a message to the current stranger if connected """
        
        if self.omegle_id:
            message = message.strip()
            self._request(self.say_url, msg=message, id=self.omegle_id)
            return True
        else:
            return False
    
    def poll_events(self):
        """ Polls once for events from the Omegle server """
        
        events = self._request(self.events_url, id=self.omegle_id)
        if events:
            for event in events:
                if not self.handle_event(event):
                    break
    
    def event_loop(self, interval=2):
        """ Called by start/start_chat to poll for events every interval seconds and handle them as needed """
        
        self.event_loop_running = True
        while self.event_loop_running:
            self.poll_events()
            time.sleep(interval)
    
    def stop_event_loop(self):
        self.event_loop_running = False
    
    def handle_event(self, event):
        event_type = event[0]
        if event_type == 'waiting':
            self.event_handler.waiting()
        elif event_type == 'connected':
            self.event_handler.connected()
        elif event_type == 'gotMessage':
            message = event[1]
            self.event_handler.message(message)
        elif event_type == 'strangerDisconnected':
            self.disconnect()
            self.event_handler.disconnected()
        elif event_type == 'recaptchaRequired':
            self.event_handler.captcha_required()
        
        return True

class OmegleHandler:
    """ Abstract class for defining Omegle event handlers such as stranger connected, message received, etc """
    
    omegle = None
    
    def _set_omegle(self, omegle):
        """ Called by the Omegle class so event handlers can use the Omegle instance """
        self.omegle = omegle
    
    def waiting(self):
        """ Called when the server tells us we're waiting on a stranger to connect """
    
    def connected(self):
        """ Called when the server reports we're connected with a stranger """
    
    def message(self, message):
        """ Called when a message is received from the connected stranger """
    
    def disconnected(self):
        """ Called when the stranger disconnects """
    
    def captcha_required(self):
        """ Called when the server asks for a captcha """