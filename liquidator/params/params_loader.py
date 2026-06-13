def read_json_file(file_path):
    import json

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


class ParamsLoader:
    def __init__(self):
        from pathlib import Path
        # Get the project root directory
        current_dir = Path(__file__).parent
        self.params_dir = current_dir.parent.parent / "params"
    
    def load_params(self, year):
        # Load actual parameters from JSON file
        from pathlib import Path

        params_file = self.params_dir / f"{year}.json"

        if not params_file.exists():
            raise FileNotFoundError(f"Parameters file not found: {params_file}")

        return read_json_file(params_file)
