from pathlib import Path
import pathlib
import os
import shell_tool

class RosColconTool(shell_tool.ShellTool):
    IGNORE = [
        '.git',
        '.vscode',
        'build',
        'install',
        'log',
        'devel',
    ]

    def __init__(self):
        super().__init__()

    @staticmethod
    def is_ros2_package(path: Path):
        return (path / 'package.xml').exists()
    
    @staticmethod
    def is_ros2_workspace(path: Path):
        return (path / 'src').exists() and (path / 'build').exists() and (path / 'install').exists()
    
    @staticmethod
    def is_src_dir(path: Path):
        return RosColconTool.is_ros2_workspace(path.parent) and path.name == 'src'
    
    @staticmethod
    def parent_workspace(path: Path):
        if RosColconTool.is_ros2_workspace(path):
            return path
        elif RosColconTool.is_src_dir(path):
            return path.parent
        else:
            while path != Path('/'):
                path = path.parent
                if RosColconTool.is_ros2_workspace(path):
                    return path
            return None
        
    @staticmethod
    def enumerate_packages(path: Path):
        for p in path.iterdir():
            if p.name in RosColconTool.IGNORE:
                continue
            if p.is_file():
                continue
            if RosColconTool.is_ros2_package(p):
                yield p
            else:
                yield from RosColconTool.enumerate_packages(p)

    def colcon_build(self, path: Path):
        self.process(f'cd {RosColconTool.parent_workspace(path)}')
        match (path):
            case _ if RosColconTool.is_ros2_package(path):
                self.process(f'colcon build --packages-select {path.name}')
            case _ if RosColconTool.is_ros2_workspace(path):
                self.process(f'colcon build')
            case _ if RosColconTool.is_src_dir(path):
                self.process(f'colcon build')
            case _:
                packages = ' '.join([p.name for p in RosColconTool.enumerate_packages(path)])
                self.process(f'colcon build --packages-select {packages}')
    
        self.process(f'source install/setup.bash')
        self.process(f'cd {path}')

    @classmethod
    def main(cls):
        runner = cls()
        runner.process('source /opt/ros/humble/setup.bash')
        runner.colcon_build(Path(os.getcwd()))
        print(runner.create())

if __name__ == '__main__':
    RosColconTool.main()