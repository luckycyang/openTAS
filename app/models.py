import subprocess

class DockerModel:
    def __init__(self, name: str):
        self.name = name

    def is_running(self) -> bool:
        """检查容器是否正在运行"""
        try:
            result = subprocess.run(
                ["docker", "inspect", "--format='{{.State.Running}}'", self.name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            return "true" in result.stdout.lower()
        except subprocess.CalledProcessError:
            return False

    def start(self) -> bool:
        """启动容器"""
        try:
            subprocess.run(["docker", "start", self.name], check=True)
            print(f"[Docker] 容器 {self.name} 已启动")
            return True
        except subprocess.CalledProcessError as e:
            print(f"[Docker] 启动容器 {self.name} 失败: {e}")
            return False

    def stop(self) -> bool:
        """停止容器"""
        try:
            subprocess.run(["docker", "stop", self.name], check=True)
            print(f"[Docker] 容器 {self.name} 已停止")
            return True
        except subprocess.CalledProcessError as e:
            print(f"[Docker] 停止容器 {self.name} 失败: {e}")
            return False

    def status(self) -> str:
        """获取容器状态：running/stopped/error"""
        if self.is_running():
            return "running"
        else:
            return "stopped"



class ModelManager:
    def __init__(self):
        self.models = {
            "funasr": DockerModel("funasr"),
            "chattts": DockerModel("chattts"),
            # 可以添加更多模型
        }

    def get_all_model_names(self) -> list:
        """返回所有注册模型的名字"""
        return list(self.models.keys())
    
    def get_model_status(self, name: str) -> str:
        model = self.models.get(name)
        if model:
            return model.status()
        return "unknown"

    def start_model(self, name: str) -> bool:
        model = self.models.get(name)
        if model:
            return model.start()
        return False

    def stop_model(self, name: str) -> bool:
        model = self.models.get(name)
        if model:
            return model.stop()
        return False