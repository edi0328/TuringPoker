# TuringPoker

A Python poker bot client built for the McGill Poker Bot Tournament. It connects to a Turing Games server over WebSockets and responds to game updates.

The current `TemplateBot.act` implementation always calls. Experimental hand-analysis helpers are included but are not used by the bot's decisions.

## Run

Install Python and connect to a running tournament server:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py --host localhost --port 1999 --room my-new-room --username edison-bot
```

Use the host, port, and room provided by the tournament. The server is not included in this repository.

Bot decisions live in `main.py`. The `tg/` package handles the protocol and shared types.
