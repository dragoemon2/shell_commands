class ShellTool:
    def __init__(self):
        self.cmds = []

    def process(self, cmd):
        self.cmds.append(cmd)

    def create(self):
        return ' && '.join(self.cmds)