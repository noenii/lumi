import discord

import discord

class PageSearchModal(discord.ui.Modal, title = "Go to Page"):
    page_num = discord.ui.TextInput(
        label = "Page Number",
        placeholder = "Enter a Page Number",
        required = True,
        max_length = 5
    )

    def __init__(self, paginator_view):
        super().__init__()
        self.paginator_view = paginator_view

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral = True)

        try:
            target_page = int(self.page_num.value) - 1
            max_pages = len(self.paginator_view.pages)

            if 0 <= target_page < max_pages:
                self.paginator_view.current_page = target_page
                self.paginator_view.update_view()
                self.paginator_view.build_page()

                if isinstance(self.paginator_view, EmbedPaginator):
                    await interaction.message.edit(
                        embed = self.paginator_view.pages[target_page],
                        view = self.paginator_view
                    )
                else:
                    await interaction.message.edit(view = self.paginator_view)
            else:
                await interaction.followup.send(
                    f"Invalid Page, Enter a Number Between 1 and {max_pages}",
                    ephemeral = True
                )
        except ValueError:
            await interaction.followup.send("Enter a Number", ephemeral=True)

class vPaginator(discord.ui.LayoutView):
    def __init__(self, pages_data: list[list], buttons: list[str] = None, timeout: int = 120):
        super().__init__(timeout = timeout)
        self.pages = pages_data
        self.current_page = 0
        self.button_names = buttons or ["prev", "next", "search", "exit"]
        self.build_page()

    def build_page(self):
        self.clear_items()
        self.add_item(discord.ui.Container(*self.pages[self.current_page]))

        if self.button_names:
            row = discord.ui.ActionRow()
            if "prev" in self.button_names:
                b = discord.ui.Button(emoji = "<:larrow:1546438657035075675>", style = discord.ButtonStyle.secondary, disabled = self.current_page == 0)
                b.callback = self.go_prev
                row.add_item(b)
            if "next" in self.button_names:
                b = discord.ui.Button(emoji = "<:rarrow:1546438717919469650>", style = discord.ButtonStyle.secondary, disabled = self.current_page == len(self.pages) - 1)
                b.callback = self.go_next
                row.add_item(b)
            if "search" in self.button_names:
                b = discord.ui.Button(emoji = "<:search:1546438616190947369>", style = discord.ButtonStyle.secondary)
                b.callback = self.go_search
                row.add_item(b)
            if "exit" in self.button_names:
                b = discord.ui.Button(emoji = "<:stop:1546438775633092658>", style = discord.ButtonStyle.danger)
                b.callback = self.go_exit
                row.add_item(b)
            self.add_item(row)

    def update_view(self):
        self.build_page()

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        message = getattr(self, 'message', None)
        if message:
            try:
                await message.edit(view=self)
            except discord.HTTPException:
                pass

    async def go_prev(self, interaction: discord.Interaction):
        self.current_page -= 1
        self.build_page()
        await interaction.response.edit_message(view=self)

    async def go_next(self, interaction: discord.Interaction):
        self.current_page += 1
        self.build_page()
        await interaction.response.edit_message(view=self)

    async def go_search(self, interaction: discord.Interaction):
        await interaction.response.send_modal(PageSearchModal(self))

    async def go_exit(self, interaction: discord.Interaction):
        self.stop()
        await interaction.response.edit_message(view=None)

class ePaginator(discord.ui.View):
    def __init__(self, embeds: list[discord.Embed], buttons: list[str] = None, timeout: int = 120):
        super().__init__(timeout=timeout)
        self.pages = embeds
        self.current_page = 0
        self.button_names = buttons or ["prev", "next", "search", "exit"]

        self.buttons_map = {}
        if "prev" in self.button_names:
            btn = discord.ui.Button(emoji = "<:larrow:1546438657035075675>", style = discord.ButtonStyle.secondary)
            btn.callback = self.go_prev
            self.buttons_map["prev"] = btn
            self.add_item(btn)
        if "next" in self.button_names:
            btn = discord.ui.Button(emoji = "<:rarrow:1546438717919469650>", style = discord.ButtonStyle.secondary)
            btn.callback = self.go_next
            self.buttons_map["next"] = btn
            self.add_item(btn)
        if "search" in self.button_names:
            btn = discord.ui.Button(emoji = "<:search:1546438616190947369>", style = discord.ButtonStyle.secondary)
            btn.callback = self.go_search
            self.buttons_map["search"] = btn
            self.add_item(btn)
        if "exit" in self.button_names:
            btn = discord.ui.Button(emoji = "<:stop:1546438775633092658>", style = discord.ButtonStyle.danger)
            btn.callback = self.go_exit
            self.buttons_map["exit"] = btn
            self.add_item(btn)

        self.update_view()

    def update_view(self):
        if "prev" in self.buttons_map:
            self.buttons_map["prev"].disabled = self.current_page == 0
        if "next" in self.buttons_map:
            self.buttons_map["next"].disabled = self.current_page == len(self.pages) - 1

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        message = getattr(self, 'message', None)
        if message:
            try:
                await message.edit(view=self)
            except discord.HTTPException:
                pass

    async def go_prev(self, interaction: discord.Interaction):
        self.current_page -= 1
        self.update_view()
        await interaction.response.edit_message(embed = self.pages[self.current_page], view = self)

    async def go_next(self, interaction: discord.Interaction):
        self.current_page += 1
        self.update_view()
        await interaction.response.edit_message(embed = self.pages[self.current_page], view = self)

    async def go_search(self, interaction: discord.Interaction):
        await interaction.response.send_modal(PageSearchModal(self))

    async def go_exit(self, interaction: discord.Interaction):
        self.stop()
        await interaction.response.edit_message(view=None)

def chunk_list(items: list, per_page: int):
    for i in range(0, len(items), per_page):
        yield items[i : i + per_page]
