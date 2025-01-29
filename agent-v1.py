import json
import math
from datetime import datetime

class AIAgent:
    def __init__(self):
        self.short_memory = []  # Últimas 3 interações
        self.long_memory_file = "long_term_memory.txt"
        self.tools = {
            "calculator": self.calculator_tool,
            "data": self.data_tool,
            "hora": self.hora_tool
        }

    def update_short_memory(self, interaction):
        """Atualiza a memória de curto prazo"""
        self.short_memory.append(interaction)
        if len(self.short_memory) > 3:
            self.short_memory.pop(0)

    def update_long_memory(self, data):
        """Armazena informações importantes a longo prazo"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.long_memory_file, "a") as f:
            f.write(f"{timestamp} - {data}\n")

    def calculator_tool(self, expression):
        """Ferramenta de cálculo matemático"""
        try:
            result = eval(expression)
            self.update_long_memory(f"CALCULATION: {expression} = {result}")
            return result
        except:
            return "Erro na expressão matemática"

    def data_tool(self, expression):
        """Ferramenta de data"""
        now = datetime.now()
        input_text = expression.lower()

        result = now.strftime("%d/%m/%Y")
        self.update_long_memory(f"CONSULTA DATA: {input_text} -> {result}")

        return result

    def hora_tool(self, expression):
        now = datetime.now()
        input_text = expression.lower()

        result = f"Hora: {now.strftime('%H:%M:%S')}"

        self.update_long_memory(f"CONSULTA HORA: {input_text} -> {result}")
        return result
        
    def decide_action(self, input_text):
        """Planejamento: Decide qual ação tomar"""
        input_text = input_text.lower()
        
        # Verifica se é uma operação matemática
        math_keywords = ['calcular', 'calcule', 'quanto é', '+', '-', '*', '/']
        # Verifica data e hora atual
        data_keywords = ['data', 'hoje', 'dia', 'hora', 'horas']

        if any(keyword in input_text for keyword in math_keywords):
            return "use_tool", "calculator"
        elif any(keyword in input_text for keyword in data_keywords):
            if any(k in input_text for k in ["data", "hoje", "dia"]):
                return "use_tool", "data"
            else:
                return "use_tool", "hora"

        # Se não encontrar padrão específico, usa memória
        return "use_memory", None

    def generate_response(self, input_text):
        """Executa a ação e gera resposta"""
        action, tool = self.decide_action(input_text)
        
        # Atualiza memória curta
        self.update_short_memory({
            "input": input_text,
            "action": action,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })

        if action == "use_tool" and tool == "calculator":
            expression = input_text.replace("calcular", "").strip()
            result = self.tools["calculator"](expression)
            return f"O resultado da operação é: {result}"
        elif action == "use_tool" and tool == "data":
            result = self.tools["data"](input_text)
            return f"Data atual: {result}"
        elif action == "use_tool" and tool == "hora":
            result = self.tools["hora"](input_text)
            return f"Hora atual: {result}"
        
        if action == "use_memory" and tool is None:
            if self.short_memory:
                return f"Baseado na nossa interação anterior sobre {self.short_memory[-1][input]} posso ajudar com..."
        
        # Resposta padrão se não reconhecer o padrão
        return "Desculpe, ainda estou aprendendo. Como posso ajudar melhor?"

    def print_status(self):
        """Mostra o estado atual do agente"""
        print("\n--- Estado do Agente ---")
        print("Memória Curta:", json.dumps(self.short_memory, indent=2))
        with open(self.long_memory_file, "r") as f:
            print("Memória Longa:", f.read())

# Testando o agente
if __name__ == "__main__":
    agent = AIAgent()
    
    while True:
        user_input = input("\nVocê: ")
        if user_input.lower() == "sair":
            break
        
        response = agent.generate_response(user_input)
        print("Agente:", response)
        
        # Mostrar estado ao final
        if "resultado" in response.lower() or "atual" in response.lower():
            agent.print_status()