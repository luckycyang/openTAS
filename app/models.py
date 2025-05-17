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
        print("status:"+self.name)
        if self.is_running():
            return "running"
        else:
            return "stopped"



class ModelManager:
    def __init__(self):
        self.models = {
            "stt": {
                "funasr-online-server": DockerModel("funasr-online-server"),
                # 可以在这里添加更多的 STT 模型
            },
            "tts": {
                "chat-tts-ui": DockerModel("chat-tts-ui"),
                # 可以在这里添加更多的 TTS 模型
            }
        }

    def add_model(self, model_type: str, name: str):
        """动态添加新的模型"""
        if model_type in self.models:
            if name not in self.models[model_type]:
                self.models[model_type][name] = DockerModel(name)
                return True
        return False

    def get_all_model_names_by_type(self, model_type: str) -> list:
        """根据类型返回所有注册的模型名称"""
        return list(self.models.get(model_type, {}).keys())

    def get_model_status(self, model_type: str, name: str) -> str:
        model = self.models[model_type].get(name)
        if model:
            return model.status()
        return "unknown"

    def start_model(self, model_type: str, name: str) -> bool:
        model = self.models[model_type].get(name)
        if model:
            return model.start()
        return False

    def stop_model(self, model_type: str, name: str) -> bool:
        model = self.models[model_type].get(name)
        if model:
            return model.stop()
        return False