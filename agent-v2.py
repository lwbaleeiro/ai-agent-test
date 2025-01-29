import json
from datetime import datetime

class AIAgent:
    def __init__(self):
        self.short_memory = []  # Últimas 5 interações
        self.long_memory_file = "long_term_memory_v2.txt"
        self.tools = {
            "calculator": self.calculator_tool,
            "time": self.time_tool,
            "date": self.date_tool
        }

    def update_short_memory(self, interaction):
        """Atualiza a memória de curto prazo com contexto"""
        self.short_memory.append(interaction)
        if len(self.short_memory) > 5:
            self.short_memory.pop(0)

    def update_long_memory(self, data):
        """Armazena informações importantes a longo prazo com tags"""
        timestamp = datetime.now().isoformat()
        entry = {
            "timestamp": timestamp,
            "data": data
        }
        with open(self.long_memory_file, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def calculator_tool(self, expression):
        """Ferramenta de cálculo com validação"""
        try:
            # Remove palavras não numéricas para melhorar a expressão
            clean_exp = ''.join([c for c in expression if c in '0123456789+-*/(). '])
            result = eval(clean_exp)
            self.update_long_memory({
                "type": "calculation",
                "input": expression,
                "result": result
            })
            return result
        except Exception as e:
            return f"Erro na operação: {str(e)}"

    def time_tool(self):
        """Retorna hora atual com formatação"""
        now = datetime.now().strftime("%H:%M:%S")
        self.update_long_memory({
            "type": "time_query",
            "result": now
        })
        return now

    def date_tool(self):
        """Retorna data atual em formato local"""
        now = datetime.now().strftime("%d/%m/%Y")
        self.update_long_memory({
            "type": "date_query",
            "result": now
        })
        return now

    def decide_action(self, input_text):
        """Sistema de decisão com pontuação"""
        input_lower = input_text.lower()
        
        # Sistema de pontuação por intenção
        scores = {
            'calculator': 0,
            'date': 0,
            'time': 0
        }
        
        # Palavras-chave ponderadas
        math_keywords = {
            'calcular': 2, 'calcule': 2, 'quanto é': 2, 
            '+': 1, '-': 1, '*': 1, '/': 1, '=': 1
        }
        
        date_keywords = {'data': 2, 'hoje': 1, 'dia': 1}
        time_keywords = {'hora': 2, 'horas': 1, 'relógio': 1}
        
        # Calcula pontuações
        for word, weight in math_keywords.items():
            if word in input_lower:
                scores['calculator'] += weight
                
        for word, weight in date_keywords.items():
            if word in input_lower:
                scores['date'] += weight
                
        for word, weight in time_keywords.items():
            if word in input_lower:
                scores['time'] += weight
                
        # Determina ação com maior pontuação
        max_score = max(scores.values())
        if max_score == 0:
            return "memory", None
            
        actions = [k for k, v in scores.items() if v == max_score]
        
        # Prioridade para cálculos se houver operadores matemáticos
        if 'calculator' in actions:
            return "tool", "calculator"
            
        return "tool", actions[0]

    def generate_response(self, input_text):
        """Gera resposta com contexto"""
        action_type, tool = self.decide_action(input_text)
        
        # Registra na memória curta
        self.update_short_memory({
            "input": input_text,
            "action": f"{action_type}:{tool}" if tool else "memory",
            "timestamp": datetime.now().isoformat()
        })
        
        if action_type == "tool":
            if tool == "calculator":
                # Extrai expressão matemática
                expression = ''.join([c for c in input_text if c in '0123456789+-*/(). '])
                result = self.tools[tool](expression)
                return f"🔢 Resultado calculado: {result}"
                
            elif tool == "date":
                result = self.tools[tool]()
                return f"📅 Data atual: {result}"
                
            elif tool == "time":
                result = self.tools[tool]()
                return f"🕒 Hora atual: {result}"
        
        # Resposta baseada em memória
        if self.short_memory:
            last_interaction = self.short_memory[-1]["input"]
            return f"Baseado em nossa última conversa sobre '{last_interaction}', como posso ajudar melhor?"
            
        return "Desculpe, não entendi. Poderia reformular sua pergunta?"

    def print_status(self):
        """Exibe o estado completo do agente"""
        print("\n=== Estado do Agente ===")
        print("Memória Curta (últimas 5 interações):")
        print(json.dumps(self.short_memory, indent=2, ensure_ascii=False))
        
        print("\nMemória Longa:")
        try:
            with open(self.long_memory_file, "r") as f:
                for line in f:
                    print(json.loads(line))
        except FileNotFoundError:
            print("Memória longa vazia")

# Testes
if __name__ == "__main__":
    agent = AIAgent()
    
    test_cases = []

    # test_cases = [
    #     "Que dia é hoje?",
    #     "Que horas são?",
    #     "Calcule 2 + 3 * 4",
    #     "Quanto é 100 dividido por 3?",
    #     "Previsão do tempo",
    #     "sair"
    # ]

    # testes interativo
    for case in test_cases:
        print(f"\nVocê: {case}")
        if case.lower() == "sair":
            break
            
        response = agent.generate_response(case)
        print(f"Agente: {response}")
        agent.print_status()
    
    while True:
        user_input = input("\nVocê: ")
        if user_input.lower() == "sair":
            break
        
        response = agent.generate_response(user_input)
        print("Agente:", response)
        
        # Mostrar estado ao final
        if "resultado" in response.lower() or "atual" in response.lower():
            agent.print_status()