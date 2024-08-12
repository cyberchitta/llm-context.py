import os

import wx

from llm_code_context.config_manager import ConfigManager


class FileSelectorUi(wx.Frame):
    @staticmethod
    def create():
        config_manager = ConfigManager.create_default()

        frame = wx.Frame(parent=None, title="File Selector")
        panel = wx.Panel(frame)

        select_button = wx.Button(panel, label="Select Files")
        select_button.Bind(
            wx.EVT_BUTTON, lambda event: FileSelectorUi.on_select_files(config_manager, event)
        )

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(select_button, 0, wx.ALL | wx.CENTER, 10)
        panel.SetSizer(sizer)

        frame.SetSize((300, 200))
        frame.Centre()

        return FileSelectorUi(config_manager, panel)

    @staticmethod
    def on_select_files(config_manager, event):
        root_path = config_manager.project.get("root_path", ".") + "/"
        default_dir = os.path.expanduser(root_path)
        with wx.FileDialog(
            None,
            "Select Files",
            defaultDir=default_dir,
            wildcard="*.*",
            style=wx.FD_OPEN | wx.FD_MULTIPLE,
        ) as file_dialog:
            if file_dialog.ShowModal() == wx.ID_OK:
                selected_files = file_dialog.GetPaths()
                config_manager.update_files(selected_files)

    def __init__(self, config_manager, panel):
        super().__init__(parent=None, title="File Selector")
        self.config_manager = config_manager
        self.panel = panel


def main():
    app = wx.App()
    file_selector = FileSelectorUi.create()
    file_selector.panel.GetParent().Show(True)
    app.MainLoop()


if __name__ == "__main__":
    main()
