class Member():

    def __init__(self, websocket, name, sid):
        self.websocket = websocket
        self.name = name
        self.sid = sid

    def get_websocket(self):
        return self.websocket
    
    def get_name(self):
        return self.name
    
    def get_sid(self):
        return self.sid
    
    def kill_websocket(self) -> bool:
        try:
            if self.websocket.open:
                self.websocket.close()
            return True
        except:
            return False
        
    def update_name(self, name):
        self.name = name

    def update_sid(self, sid):
        self.sid = sid