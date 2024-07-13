import json
import time
import queue
import threading

from my_logger import logger
from rc_message import RCMessage
from mjai.player import MjaiPlayerClient

from consts import CARD2MJAI

class GameStatus:
    def __init__(self):
        self.uid = -1
        self.seat = -1
        self.tehai = []
        self.tsumo = None

        self.last_dahai_actor = -1

        self.player_list = []
        self.dora_markers = []

        self.is_3p = False


class Manager:
    def __init__(self):
        self.game_status = GameStatus()
        self.mjai_msgs = []
        self.mjai_player = MjaiPlayerClient()

        self.q = queue.Queue()
        self.running = True
        self.t = threading.Thread(target=self.run)
        self.t.start()

    def run(self):
        while self.running:
            try:
                item = self.q.get(timeout=1)
                assert isinstance(item, RCMessage)
                self.parse(item)



                self.q.task_done()
            except queue.Empty:
                pass
            # time.sleep(1)

    def put(self, item):
        self.q.put(item)

    def stop(self):
        self.running = False
        self.t.join()

    def __del__(self):
        self.stop()

    def parse(self, item: RCMessage):
        if item.msg_type == 0x01:
            if "uid" not in item.msg_data:
                logger.error(f"Unknown login message: {item.msg_data}")
                return
            self.game_status.uid = int(item.msg_data["uid"])
            logger.info(f"Got uid: {self.game_status.uid}")
            return
        if "cmd" in item.msg_data:
            match item.msg_data["cmd"]:
                case "cmd_enter_room":
                    players = item.msg_data["data"]["players"]
                    if item.msg_data["data"]["options"]["player_count"] == 3:
                        self.game_status.is_3p = True
                    for idx, player in enumerate(players):
                        self.game_status.player_list.append(player["user"]["user_id"])
                        if player["user"]["user_id"] == self.game_status.uid:
                            position_at = player['position_at']
                            self.game_status.seat = position_at
                            self.mjai_msgs.append({"type": "start_game", "id": position_at})
                            self.mjai_player.launch_bot(position_at, self.game_status.is_3p)
                    if self.game_status.is_3p:
                        self.game_status.player_list.append(-1)


                case "cmd_game_start":
                    bakaze = CARD2MJAI[item.msg_data["data"]["quan_feng"]]
                    dora_marker = CARD2MJAI[item.msg_data["data"]["bao_pai_card"]]
                    kyoku = item.msg_data["data"]["dealer_pos"]+1
                    honba = item.msg_data["data"]["ben_chang_num"]
                    kyotaku = item.msg_data["data"]["li_zhi_bang_num"]
                    oya = item.msg_data["data"]["dealer_pos"]
                    scores = [player["hand_points"] for player in item.msg_data["data"]["user_info_list"]]
                    if self.game_status.is_3p:
                        scores.append(0)
                    tehais = [["?"]*13 for _ in range(4)]
                    if len(item.msg_data["data"]["hand_cards"]) == 14:
                        my_tehai = item.msg_data["data"]["hand_cards"][:13]
                        my_tsumo = item.msg_data["data"]["hand_cards"][13]
                    else:
                        my_tehai = item.msg_data["data"]["hand_cards"]
                        my_tsumo = None
                    my_tehai = [CARD2MJAI[card] for card in my_tehai]
                    self.game_status.tehai = my_tehai
                    tehais[self.game_status.seat] = my_tehai
                    self.mjai_msgs.append({
                        "type": "start_kyoku",
                        "bakaze": bakaze,
                        "dora_marker": dora_marker,
                        "kyoku": kyoku,
                        "honba": honba,
                        "kyotaku": kyotaku,
                        "oya": oya,
                        "scores": scores,
                        "tehais": tehais,
                    })
                    self.game_status.dora_markers = []
                    self.game_status.tsumo = my_tsumo
                    if my_tsumo is not None:
                        my_tsumo = CARD2MJAI[my_tsumo]
                        self.mjai_msgs.append({
                            "type": "tsumo",
                            "actor": self.game_status.seat,
                            "pai": my_tsumo,
                        })
                        if len(self.mjai_msgs) > 0:
                            self.react()
                            # logger.warning(f"MJAI <- {self.mjai_msgs}")
                            # logger.error(f"MJAI -> {self.react()}")
                    else:
                        self.mjai_msgs.append({
                            "type": "tsumo",
                            "actor": oya,
                            "pai": "?",
                        })
                case "cmd_in_card_brc":
                    actor = self.game_status.player_list.index(item.msg_data["data"]["user_id"])
                    pai = CARD2MJAI[item.msg_data["data"]["card"]]
                    self.mjai_msgs.append({
                        "type": "tsumo",
                        "actor": actor,
                        "pai": pai,
                    })
                case "cmd_game_action_brc":
                    action_info = item.msg_data["data"]["action_info"]
                    for action in action_info:
                        match action["action"]:
                            case 2 | 3 | 4:
                                # chi_low, chi_mid, chi_high
                                actor = self.game_status.player_list.index(action["user_id"])
                                target = (actor - 1) % 4
                                pai = CARD2MJAI[action["card"]]
                                consumed = [CARD2MJAI[card] for card in action["group_cards"]]
                                self.mjai_msgs.append({
                                    "type": "chi",
                                    "actor": actor,
                                    "target": target,
                                    "pai": pai,
                                    "consumed": consumed,
                                })
                            case 5:
                                actor = self.game_status.player_list.index(action["user_id"])
                                target = self.game_status.last_dahai_actor
                                pai = CARD2MJAI[action["card"]]
                                consumed = [CARD2MJAI[card] for card in action["group_cards"]]
                                self.mjai_msgs.append({
                                    "type": "pon",
                                    "actor": actor,
                                    "target": target,
                                    "pai": pai,
                                    "consumed": consumed,
                                })
                            case 6:
                                actor = self.game_status.player_list.index(action["user_id"])
                                target = self.game_status.last_dahai_actor
                                pai = CARD2MJAI[action["card"]]
                                consumed = [CARD2MJAI[card] for card in action["group_cards"]]
                                self.mjai_msgs.append({
                                    "type": "daiminkan",
                                    "actor": actor,
                                    "target": target,
                                    "pai": pai,
                                    "consumed": consumed,
                                })
                            case 7:
                                # actor = self.game_status.player_list.index(action["user_id"])
                                # target = self.game_status.last_dahai_actor
                                # pai = CARD2MJAI[action["card"]]
                                # self.mjai_msgs.append({
                                #     "type": "hora",
                                #     "actor": actor,
                                #     "target": target,
                                #     "pai": pai,
                                # })     
                                self.mjai_msgs.append({
                                    "type": "end_kyoku",
                                })
                            case 8:
                                actor = self.game_status.player_list.index(action["user_id"])
                                consumed = [CARD2MJAI[action["card"]]]*4
                                if consumed[0] in ["5m", "5p", "5s"]:
                                    consumed[0] += "r"
                                self.mjai_msgs.append({
                                    "type": "ankan",
                                    "actor": actor,
                                    "consumed": consumed,
                                })
                            case 9:
                                actor = self.game_status.player_list.index(action["user_id"])
                                pai = CARD2MJAI[action["card"]]
                                consumed = [pai]*3
                                if pai in ["5m", "5p", "5s"]:
                                    consumed[0] += "r"
                                self.mjai_msgs.append({
                                    "type": "kakan",
                                    "actor": actor,
                                    "pai": pai,
                                    "consumed": consumed,
                                })
                            case 10:
                                # tsumo ron
                                self.mjai_msgs.append({
                                    "type": "end_kyoku",
                                })
                            case 11:
                                actor = self.game_status.player_list.index(action["user_id"])
                                pai = CARD2MJAI[action["card"]]
                                tsumogiri = action["move_cards_pos"][0] == 14
                                if action["is_li_zhi"]:
                                    self.mjai_msgs.append({
                                        "type": "reach",
                                        "actor": actor,
                                    })
                                self.mjai_msgs.append({
                                    "type": "dahai",
                                    "actor": actor,
                                    "pai": pai,
                                    "tsumogiri": tsumogiri,
                                })
                                self.game_status.last_dahai_actor = actor
                                if action["is_li_zhi"]:
                                    self.mjai_msgs.append({
                                        "type": "reach_accepted",
                                        "actor": actor,
                                    })
                                if len(self.game_status.dora_markers) > 0:
                                    for dora_marker in self.game_status.dora_markers:
                                        self.mjai_msgs.append({
                                            "type": "dora",
                                            "dora_marker": dora_marker,
                                        })
                                    self.game_status.dora_markers = []
                            case 12:
                                # ryukyoku
                                self.mjai_msgs.append({
                                    "type": "end_kyoku",
                                })
                            case 13:
                                actor = self.game_status.player_list.index(action["user_id"])
                                pai = CARD2MJAI[action["card"]] # Must be "N"
                                self.mjai_msgs.append({
                                    "type": "nukidora",
                                    "actor": actor,
                                    "pai": pai,
                                })
                            case _:
                                pass
                case "cmd_send_current_action":
                    pai = CARD2MJAI[item.msg_data["data"]["in_card"]]
                    if pai != "?":
                        self.mjai_msgs.append({
                            "type": "tsumo",
                            "actor": self.game_status.seat,
                            "pai": pai,
                        })
                    if len(self.mjai_msgs) > 0:
                        self.react()
                        # logger.warning(f"MJAI <- {self.mjai_msgs}")
                        # logger.error(f"MJAI -> {self.react()}")
                case "cmd_send_other_action":
                    if len(self.mjai_msgs) > 0:
                        self.react()
                        # logger.warning(f"MJAI <- {self.mjai_msgs}")
                        # logger.error(f"MJAI -> {self.react()}")
                case "cmd_gang_bao_brc":
                    dora_marker = CARD2MJAI[item.msg_data["data"]["cards"][-1]]
                    self.game_status.dora_markers.append(dora_marker)
                case "cmd_room_end":
                    self.mjai_msgs.append({
                        "type": "end_game",
                    })
                    self.mjai_player.delete_bot()
                    self.mjai_msgs = []
                    self.game_status = GameStatus()
                case _:
                    pass
            # self.send_mjai(self.mjai_msgs)
        pass

    def react(self):
        out = self.mjai_player.react(str(self.mjai_msgs).replace("\'", "\"").replace("True", "true").replace("False", "false"))
        self.mjai_msgs = []
        json_out = json.loads(out)
        if json_out["type"] == "reach":
            reach = [{
                'type': 'reach',
                'actor': self.game_status.seat,
            }]
            out = self.mjai_player.react(str(reach).replace("\'", "\""))
            json_out = json.loads(out)
            json_out["type"] = "reach"
        return json_out