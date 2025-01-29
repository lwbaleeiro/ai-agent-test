import sqlite3
import requests
import time

class AIAgent:
    def __init__(self, memory_limit=5):
        # Memória curta
        self.short_memory = []
        self.memory_limit = memory_limit

        # Memória longa
        self.db_connection = sqlite3.connect("long_term_memory.db")
        self.cursor = self.db_connection.cursor()
        self._setup_database()

    def _setup_database(self):
        """Configura o banco de dados para a memória longa."""
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS memory (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, data TEXT)"
        )
        self.db_connection.commit()

    def add_to_short_memory(self, data):
        """Adiciona dados à memória curta."""
        if len(self.short_memory) >= self.memory_limit:
            self.short_memory.pop(0)  # Remove o item mais antigo
        self.short_memory.append(data)

    def add_to_long_memory(self, data):
        """Adiciona dados à memória longa."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("INSERT INTO memory (timestamp, data) VALUES (?, ?)", (timestamp, data))
        self.db_connection.commit()

    def retrieve_long_memory(self):
        """Recupera todos os dados da memória longa."""
        self.cursor.execute("SELECT * FROM memory")
        return self.cursor.fetchall()

    def connect_to_tool(self, tool_name, **kwargs):
        """Exemplo de conexão com uma ferramenta externa (API de previsão do tempo)."""
        if tool_name == "weather_api":
            city = kwargs.get("city", "")
            api_key = kwargs.get("api_key", "")
            url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}"
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": "Failed to connect to Weather API"}

    def plan(self, task):
        """Exemplo de planejamento básico para executar uma tarefa."""
        if task == "check_weather":
            return ["Fetch weather data", "Save to memory"]
        else:
            return ["Task not recognized"]

    def act(self, steps, tool=None, **kwargs):
        """Executa as etapas planejadas."""
        for step in steps:
            if step == "Fetch weather data":
                result = self.connect_to_tool(tool, **kwargs)
                self.add_to_short_memory(result)
                print("Weather data fetched and saved to short memory.")
            elif step == "Save to memory":
                if self.short_memory:
                    self.add_to_long_memory(str(self.short_memory[-1]))
                    print("Weather data saved to long memory.")
            else:
                print(f"Unknown step: {step}")

# Exemplo de uso do agente
if __name__ == "__main__":
    agent = AIAgent()

    # Exemplo de tarefa: verificar o clima
    task = "check_weather"
    steps = agent.plan(task)

    # Chamar a ação com a ferramenta
    agent.act(steps, tool="weather_api", city="Sinop", api_key="a6f6c66d81d34a819a621444252901")

    # Exibir memórias
    print("Memória curta:", agent.short_memory)
    print("Memória longa:", agent.retrieve_long_memory())
