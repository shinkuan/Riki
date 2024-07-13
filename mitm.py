import mitmproxy.addonmanager
import mitmproxy.http
import mitmproxy.log
import mitmproxy.tcp
import mitmproxy.websocket
from mitmproxy import proxy, options, ctx
from mitmproxy.tools.dump import DumpMaster

import json
from my_logger import logger

from rc_message import RCMessage
from manager import Manager

activated_flows = [] # store all flow.id ([-1] is the recently opened)
messages_dict = dict() # flow.id -> Queue[flow_msg]
manager_dict = dict() # flow.id -> Manager
stop = False


class ClientWebSocket:

    def __init__(self):
        pass

    def websocket_start(self, flow: mitmproxy.http.HTTPFlow):
        assert isinstance(flow.websocket, mitmproxy.websocket.WebSocketData)
        global activated_flows,messages_dict,manager_dict
        
        activated_flows.append(flow.id)
        messages_dict[flow.id]=[]
        manager_dict[flow.id] = Manager()

    def websocket_message(self, flow: mitmproxy.http.HTTPFlow):
        assert isinstance(flow.websocket, mitmproxy.websocket.WebSocketData)
        global activated_flows,messages_dict,manager_dict

        # Convert first 4 byte to int
        msg_len = int.from_bytes(flow.websocket.messages[-1].content[:4], byteorder='big')
        # Check if the message is complete
        if len(flow.websocket.messages[-1].content) != msg_len:
            logger.warning(f"Message is not complete, expected {msg_len} bytes, got {len(flow.websocket.messages[-1].content)} bytes")
            logger.warning(f"Message: {flow.websocket.messages[-1].content.hex(' ')}")
            return
        # Check next 4 byte is 00 0f 00 01
        if flow.websocket.messages[-1].content[4:8] != b'\x00\x0f\x00\x01':
            logger.warning("Message is unknown format, expected 00 0f 00 01")
            logger.warning(f"Message: {flow.websocket.messages[-1].content.hex(' ')}")
            return
        # Convert next 4 byte to int
        msg_id = int.from_bytes(flow.websocket.messages[-1].content[8:12], byteorder='big')
        # Convert next 2 byte to int
        msg_type = int.from_bytes(flow.websocket.messages[-1].content[12:14], byteorder='big')
        # Check next 1 byte is 01
        if flow.websocket.messages[-1].content[14] != 1:
            logger.warning("Message is unknown format, expected 01")
            logger.warning(f"Message: {flow.websocket.messages[-1].content.hex(' ')}")
            return
        # Load json data from the rest of the message
        # if there are no data, it will be empty
        if len(flow.websocket.messages[-1].content) == 15:
            msg_data = {}
        else:
            msg_data = json.loads(flow.websocket.messages[-1].content[15:].decode('utf-8'))

        msg = {
            "msg_id": msg_id,
            "msg_type": msg_type,
            "msg_data": msg_data
        }
        if flow.websocket.messages[-1].from_client:
            logger.info(f" -> {msg}")
        else:
            logger.info(f" <- {msg}")

        rc_msg = RCMessage(msg_id, msg_type, msg_data)
        manager_dict[flow.id].put(rc_msg)

        messages_dict[flow.id].append(flow.websocket.messages[-1].content)

    def websocket_end(self, flow: mitmproxy.http.HTTPFlow):
        global activated_flows,messages_dict,manager_dict
        activated_flows.remove(flow.id)
        messages_dict.pop(flow.id)
        manager_dict.pop(flow.id)

    def stop_manager(self):
        global manager_dict
        for manager in manager_dict.values():
            manager.stop()


client_websocket = ClientWebSocket()

async def start_proxy(host="127.0.0.1", port=17878):
    opts = options.Options(mode=["socks5"], listen_host=host, listen_port=port, ssl_insecure=True)

    master = DumpMaster(
        opts,
        with_termlog=False,
        with_dumper=False,
    )
    master.addons.add(client_websocket)
    await master.run()
    return master


if __name__ == "__main__":
    import asyncio

    try:
        asyncio.run(start_proxy())
    except KeyboardInterrupt:
        client_websocket.stop_manager()
        ctx.master.shutdown()
        

addons = [
    ClientWebSocket()
]