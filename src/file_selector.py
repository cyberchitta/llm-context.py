import os

import wx

from config_manager import ConfigManager


class FileSelector(wx.Frame):
    def __init__(self, configuration_manager):
        super().__init__(parent=None, title="File Selector")
        self.configuration_manager = configuration_manager
        self.InitUI()

    def InitUI(self):
        panel = wx.Panel(self)

        select_button = wx.Button(panel, label="Select Files")
        select_button.Bind(wx.EVT_BUTTON, self.OnSelectFiles)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(select_button, 0, wx.ALL | wx.CENTER, 10)
        panel.SetSizer(sizer)

        self.SetSize((300, 200))
        self.Centre()

    def OnSelectFiles(self, event):
        root_path = (
            self.configuration_manager.get_global_config().get("root_path", ".") + "/"
        )
        default_dir = os.path.expanduser(root_path)
        with wx.FileDialog(
            self,
            "Select Files",
            defaultDir=default_dir,
            wildcard="*.*",
            style=wx.FD_OPEN | wx.FD_MULTIPLE,
        ) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_OK:
                selected_files = fileDialog.GetPaths()
                project_config = self.configuration_manager.get_project_config()
                project_config["files"] = selected_files
                self.configuration_manager.save_config(
                    self.configuration_manager.project_config_file, project_config
                )
                print("Selected files:", selected_files)


if __name__ == "__main__":
    global_config_file = os.path.expanduser("~/.llm-context/config.json")
    project_config_file = ".llm-context/config.json"
    configuration_manager = ConfigManager(global_config_file, project_config_file)

    app = wx.App()
    file_selector = FileSelector(configuration_manager)
    file_selector.Show(True)
    app.MainLoop()
