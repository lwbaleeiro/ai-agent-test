import json
import math
from datetime import datetime

class AIAgent:
    def __init__(self):
        self.short_memory = []  # Últimas 3 interações
        self.long_memory_file = "long_term_memory.txt"
        self.tools = {
            "calculator": self.calculator_tool
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

    def decide_action(self, input_text):
        """Planejamento: Decide qual ação tomar"""
        input_text = input_text.lower()
        
        # Verifica se é uma operação matemática
        math_keywords = ['calcular', 'quanto é', '+', '-', '*', '/']
        if any(keyword in input_text for keyword in math_keywords):
            return "use_tool", "calculator"
        
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
        if "resultado" in response.lower():
            agent.print_status()