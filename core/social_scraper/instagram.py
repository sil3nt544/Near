from textual.app import App, ComposeResult
from textual.widgets import Input, Static, Header, Footer
from textual.containers import Vertical
from textual.reactive import reactive
from rich.text import Text
import instaloader
import os
from instaloader.exceptions import ConnectionException, QueryReturnedNotFoundException


class IGOSINTApp(App):
    CSS = """
Screen {
    align: center middle;
}

Vertical {
    height: 100%;
    width: 50%;
    min-width: 40;
}

Input {
    margin-top: 1;
    height: 3;
    margin-bottom: 1;
    width: 100%;
    max-width: 50;
}

Static#info_box, Static#message_box {
    width: 100%;
    max-width: 70;
    padding: 1 2;
}

Footer {
    dock: bottom;
}
    """
    

    BINDINGS = [("q", "quit", "Quit")]

    username = reactive("")
    info_box: Static
    message_box: Static

    def compose(self) -> ComposeResult:
        self.theme = "dracula"
        yield Vertical(
            Input(placeholder="Enter username and press Enter", id="username_input"),
            Static("", id="info_box"),
            Static("", id="message_box"),
        )

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        self.username = event.value.strip()
        self.info_box = self.query_one("#info_box", Static)
        self.message_box = self.query_one("#message_box", Static)

        self.info_box.update("[yellow]Fetching data, please wait...[/yellow]")
        await self.run_scraper(self.username)

    async def run_scraper(self, username: str):
        L = instaloader.Instaloader(
            download_pictures=False,
            download_videos=False,
            download_video_thumbnails=False,
            download_geotags=True,
            download_comments=False,
            save_metadata=True,
            compress_json=False,
        )

        try:
            profile = instaloader.Profile.from_username(L.context, username)
        except instaloader.exceptions.ProfileNotExistsException:
            self.info_box.update(f"[red]Error: User '{username}' not found.[/red]")
            return
        except Exception as e:
            self.info_box.update(f"[red]Unexpected error: {e}[/red]")
            return

        os.makedirs(username, exist_ok=True)

        info = {
            "Username": profile.username,
            "User ID": profile.userid,
            "Full Name": profile.full_name,
            "Bio": profile.biography,
            "Verified": profile.is_verified,
            "Private": profile.is_private,
            "Profile Pic URL": profile.profile_pic_url,
            "External URL": profile.external_url,
            "Followers": profile.followers,
            "Following": profile.followees,
            "Posts": profile.mediacount,
        }

        with open(f"{username}/profile_info.txt", "w", encoding="utf-8") as f:
            for key, value in info.items():
                f.write(f"{key}: {value}\n")

        L.download_profilepic(profile)

        try:
            for post in profile.get_posts():
                try:
                    metadata = {
                        "URL": f"https://www.instagram.com/p/{post.shortcode}/",
                        "Caption": post.caption,
                        "Hashtags": post.caption_hashtags,
                        "Date (UTC)": post.date_utc,
                        "Location": str(post.location),
                        "Likes": post.likes,
                        "Comments": post.comments,
                    }

                    post_file = f"{username}/post_{post.shortcode}.txt"
                    with open(post_file, "w", encoding="utf-8") as f:
                        for key, value in metadata.items():
                            f.write(f"{key}: {value}\n")

                except (ConnectionException, QueryReturnedNotFoundException) as e:
                    self.console.log(f"[!] Skipped a post due to error: {e}")
                    continue
        except Exception as e:
            self.console.log(f"[!] Could not fetch posts: {e}")
            self.message_box.update(
                f"[yellow]Warning: Could not fetch posts due to rate limit or auth error.[/yellow]"
            )

        output = Text()
        for key, value in info.items():
            output.append(f"{key}: ", style="bold cyan")
            output.append(f"{value}\n")

        self.info_box.update(output)
        self.message_box.update(f"[green]All data saved in the folder: './{username}'[/green]")

if __name__ == "__main__":
    IGOSINTApp().run()


