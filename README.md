<br/>
<p align="center">
  <h1 align="center">Riki</h3>

  <p align="center">
A simple tool to intercept Riichi City's websocket message and translate it to MJAI message for Mahjong AI model.<br>
<br>
    <br/>
    <br/>
    <a href="https://discord.gg/Z2wjXUK8bN">Ask me anything about this at Discord</a>
    <br/>
    <br/>
    <a href="https://github.com/shinkuan/Riki/issues">Report Bug</a>
    .
    <a href="https://github.com/shinkuan/Riki/issues">Request Feature</a>
  </p>
</p>

# About The Project

## "The purpose of this project is to provide people with a convenient way to real-time understand their performance in Riichi City game matches and to learn and improve from it. This project is intended for educational purposes only, and the author is not responsible for any actions taken by users using this project. Riichi City officials may detect abnormal behavior, and any consequences such as account suspension are not related to the author."

# Usage

## Installation.

### You will need:

1. Python 3.10~3.12
1. A `mortal.pth`. [(Get one from Discord server if you don't have one.)](https://discord.gg/Z2wjXUK8bN)
2. Proxifier or similar software to redirect Riichi City connection to MITM.

**Get mortal.pth at [Discord](https://discord.gg/Z2wjXUK8bN)**

1. Go to #verify and click the ✅ reaction.
2. Go to #bot-zip
3. Download a bot you like.
4. Extract the zip.
5. And mortal.pth is there.

### Windows

1. Clone this repository 
2. cd in to the directory (`cd Riki`)
3. Create a virtual environment (`python -m venv venv`)
4. Activate the virtual environment (`.\venv\Scripts\Activate`)
5. Install the requirements (`pip install -r requirements.txt`)
6. Open mitmproxy if this is your first time using it.
7. Close it.
8. Go to your user home directory `~/.mitmproxy`
9.  Install the certificate.
10. Put `mortal.pth` into `./Akagi/mjai/bot`
11. Setup Proxifier or similar software to redirect Riichi City connection to MITM.

### Mac

1. Clone this repository
2. cd in to the directory (`cd Riki`)
3. Create a virtual environment (`python -m venv venv`)
4. Activate the virtual environment (`source venv/bin/activate`)
5. Install the requirements (`pip install -r requirements.txt`)
6. Open mitmproxy if this is your first time using it.
7. Close it.
8. Go to your user home directory `~/.mitmproxy`
9. Install the certificate.
10. Put `mortal.pth` into `./Akagi/mjai/bot`
11. Setup Proxifier or similar software to redirect Riichi City connection to MITM.

## Launch

1. cd into the directory (`cd Riki`)
2. Activate the virtual environment (`.\venv\Scripts\Activate` or `source venv/bin/activate`)
3. Run the script (`python mitm.py`)
4. Open Riichi City and play a game.

# TODO

- [ ] Add GUI

# Special Thanks

[Equim-chan/Mortal](https://github.com/Equim-chan/Mortal)

[smly/mjai.app](https://github.com/smly/mjai.app)

# LICENSE

```
“Commons Clause” License Condition v1.0

The Software is provided to you by the Licensor under the License, as defined below, subject to the following condition.

Without limiting other conditions in the License, the grant of rights under the License will not include, and the License does not grant to you, the right to Sell the Software.

For purposes of the foregoing, “Sell” means practicing any or all of the rights granted to you under the License to provide to third parties, for a fee or other consideration (including without limitation fees for hosting or consulting/ support services related to the Software), a product or service whose value derives, entirely or substantially, from the functionality of the Software. Any license notice or attribution required by the License must also include this Commons Clause License Condition notice.

Software: Riki

License: GNU Affero General Public License version 3 with Commons Clause

Licensor: shinkuan
```
