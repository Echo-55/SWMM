
class SteamCMDNotInstalledException(Exception):
    def __init__(self, path):
        self.path = path
        self.message = f"SteamCMD not found at {self.path}"
        super().__init__(self.message)

class RemovedFromSteamException(Exception):
    def __init__(self, name):
        self.name = name
        self.message = f"{self.name} has been removed from Steam"
        super().__init__(self.message)