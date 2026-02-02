import json
import os

class ConfigManager:
    def __init__(self, config_path="data/config.json"):
        self.config_path = config_path
        self.config = {
            "indexed_folders": [],
            "llm": {
                "provider": "Ollama",
                "model": "llama3",
                "api_key": ""
            },
            "view_mode": "list"
        }
        self.load()

    def load(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    saved_config = json.load(f)
                    self.config.update(saved_config)
            except Exception as e:
                print(f"Error loading config: {e}")

    def save(self):
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get_folders(self):
        return self.config.get("indexed_folders", [])

    def add_folder(self, path):
        if path not in self.config["indexed_folders"]:
            self.config["indexed_folders"].append(path)
            self.save()

    def remove_folder(self, path):
        if path in self.config["indexed_folders"]:
            self.config["indexed_folders"].remove(path)
            self.save()

    def get_llm_config(self):
        return self.config.get("llm", {})

    def set_llm_config(self, provider, model, api_key, base_url=""):
        self.config["llm"] = {
            "provider": provider,
            "model": model,
            "api_key": api_key,
            "base_url": base_url
        }
        self.save()
