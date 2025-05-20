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
        try:
            result = subprocess.run(
                ["docker", "inspect", "--format={{json .State.Status}}", self.name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            status = result.stdout.strip().lower().replace('"', '')
            return {
                "running": "running",
                "exited": "stopped",
                "created": "created"
            }.get(status, "unknown")
        except subprocess.CalledProcessError:
            return "not_exist"
        except Exception as e:
            print(f"状态检测异常: {e}")
            return "error"


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
        self.discover_models()  # 初始化时自动发现

    def discover_models(self):
        """动态发现 Docker 容器并自动注册"""
        for model_type in ["stt", "tts"]:
            result = subprocess.run(
                ["docker", "ps", "-a", "--filter", f"name={model_type}-", "--format={{.Names}}"],
                stdout=subprocess.PIPE,
                text=True,
                check=True
            )
            
            containers = result.stdout.strip().split('\n')
            for name in containers:
                if name and name not in self.models[model_type]:
                    self.models[model_type][name] = DockerModel(name)


    def add_model(self, model_type: str, name: str):
        if model_type in self.models:
            # 增强容器有效性验证
            if not self._is_valid_container(name, model_type):
                return False
            if name not in self.models[model_type]:
                self.models[model_type][name] = DockerModel(name)
                return True
        return False
    
    def _is_valid_container(self, name: str, expected_type: str) -> bool:
        """验证容器是否符合命名规范且真实存在"""
        try:
            # 检查容器命名规范（例如 stt- 或 tts- 前缀）
            if not name.startswith(f"{expected_type}-"):
                return False
                
            result = subprocess.run(
                ["docker", "inspect", name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return result.returncode == 0
        except Exception:
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