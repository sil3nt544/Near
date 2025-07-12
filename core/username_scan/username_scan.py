from textual.app import App, ComposeResult
from textual.widgets import DataTable, Input, Checkbox
from textual.containers import Horizontal
from textual.events import Key
import asyncio
import json
import re
import httpx
from datetime import datetime

with open("core/username_scan/data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

class TableApp(App):
    CSS = """
    Screen {
        layout: vertical;
        align: center top;
        padding: 1 2;
    }

    Horizontal {
        height: auto;
        width: 100%;
        padding: 0;
        margin-bottom: 0;
        align-horizontal: left;
        align-vertical: middle;
    }

    Input {
        height: 3;
        margin-bottom: 1;
        width: 100%;
    }

    Checkbox {
        width: auto;
        margin-right: 1;
    }

    DataTable {
        height: 1fr;
        overflow: auto;
        margin-top: 0;
    }
    """

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Checkbox("Show NSFW sites", id="nsfw_toggle")
            yield Input(placeholder="Type username then hit Enter", id="username_input")
        self.table = DataTable(id="results_table")
        yield self.table

    def on_mount(self):
        self.theme = "dracula"
        self.nsfw_enabled = False
        self.table.cursor_type = None
        self.table.add_columns("Status", "Website", "URL", "Time", "Saved In")

    async def check_single_site(self, client, site, info, username, now):
        try:
            if info.get("isNSFW", False) and not self.nsfw_enabled:
                return None
            if "url" not in info:
                return None
            if "regexCheck" in info and not re.match(info["regexCheck"], username):
                return ("[orange3]/[/]", f"[orange3]{site}[/]", "-", now())
            url = info["url"].format(username)
            r = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
            if info.get("errorType") == "status_code":
                status = "FIND" if r.status_code == 200 else "NOT FOUND"
            elif info.get("errorType") == "message":
                err_msgs = info["errorMsg"]
                if isinstance(err_msgs, str):
                    err_msgs = [err_msgs]
                status = "NOT FOUND" if any(e in r.text for e in err_msgs) else "FIND"
            else:
                status = "UNKNOWN"

            if status == "FIND":
                return ("[green]+[/]", f"[green]{site}[/]", url, now(), f"results/{username}/{username}.txt")
            elif status == "NOT FOUND":
                return ("[red]-[/]", f"[red]{site}[/]", url, now(), "-")
            else:
                return ("[orange3]/[/]", f"[orange3]{site}[/]", url, now(), "-")
        except Exception as e:
            return ("[orange3]/[/]", f"[orange3]{site}[/]", str(e), now(), "-")

    async def check_username(self, username: str):
        self.table.clear()
        now = lambda: datetime.now().strftime("%H:%M:%S")
        rows = []

        def insert_sorted(row):
            # Verde in cima, tutto il resto in fondo
            if row[0] == "[green]+[/]":
                rows.insert(0, row)
            else:
                rows.append(row)

        async with httpx.AsyncClient(timeout=10) as client:
            async def process(site, info):
                result = await self.check_single_site(client, site, info, username, now)
                if result:
                    insert_sorted(result)
                    self.table.clear()
                    self.table.add_rows(rows)

            tasks = [
                asyncio.create_task(process(site, info))
                for site, info in data.items()
                if isinstance(info, dict)
            ]

            await asyncio.gather(*tasks)

        self.set_focus(self.table)

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        await self.check_username(event.value)

    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        if event.checkbox.id == "nsfw_toggle":
            self.nsfw_enabled = event.value

    async def on_key(self, event: Key) -> None:
        if event.key == "q":
            self.exit()
        if event.key == "enter" and self.focused.id == "username_input":
            await self.check_username(self.query_one("#username_input").value)

if __name__ == "__main__":
    try:
        TableApp().run()
    except KeyboardInterrupt:
        pass

