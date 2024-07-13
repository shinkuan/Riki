


class RCMessage:
    def __init__(self, msg_id, msg_type, msg_data):
        self.msg_id: int = msg_id
        self.msg_type: int = msg_type
        self.msg_data: dict = msg_data

    def __str__(self):
        return f"Message: {self.msg_id} {self.msg_type} {self.msg_data}"