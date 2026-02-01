import pdfplumber
import re

# ==============================================================================
# CONFIGURAÇÕES DO SISTEMA
# ==============================================================================

ARQUIVO_PDF = "ponto.pdf"     # O nome do arquivo que você vai analisar
LIMITE_HE_MINUTOS = 120       # Alerta se Hora Extra > 2 horas (120 min)
LIMITE_ABSENT_MINUTOS = 60    # Alerta se Desconto/Ausência > 1 hora (60 min)

# LISTA BRANCA (ALLOWLIST)
# Se a Observação tiver QUALQUER uma dessas palavras, o sistema IGNORA o alerta.
PALAVRAS_JUSTIFICADAS = [
    # --- Feriados e Folgas Comuns ---
    "D.S.R.", 
    "FERIAS", "FÉRIAS", 
    "FOLGA", 
    "BH LIBERACAO", "BH LIBERAÇÃO", 
    "CURSO", 
    "ANO NOVO", "NATAL", "CARNAVAL", "FERIADO", "PÁSCOA", "PASCOA",
    
    # --- Justificativas Médicas e Legais ---
    "ATESTADO", 
    "LICENCA", "LICENÇA", 
    "FALECIMENTO",
    "AFASTAMENTO", "AFASTAMENTO TEMPORARIO", "AFASTAMENTO TEMPORÁRIO",
    "DISPENSADO",
    "SUSPENSAO", "SUSPENSÃO",
    "FALTA PARCIAL",
    "JUSTIFICATIVA LEGAL",
    "VIAGEM",
    
    # --- Declarações ---
    "DECLARACAO MEDICA", "DECLARAÇÃO MEDICA", "DECLARAÇÃO MÉDICA",
    "DECLARACAO CURSO", "DECLARAÇÃO CURSO",
    "DECLARACAO DIVERSA", "DECLARAÇÃO DIVERSA",
    
    # --- Compensações ---
    "COMPENSACAO ELEITORAL", "COMPENSAÇÃO ELEITORAL",

    # --- Tratativas Já Realizadas (Ignorar se já estiver escrito) ---
    "FALTA", "INJUSTIFICADA", "ATRASO"
]

# ==============================================================================
# FUNÇÕES AUXILIARES
# ==============================================================================

def converter_minutos(valor):
    """Converte horário 'HH:MM' para total de minutos (int)."""
    if not valor: return 0
    # Remove asteriscos ou letras, pega só os números
    match = re.search(r'(\d{1,2}):(\d{2})', str(valor))
    if match:
        return (int(match.group(1)) * 60) + int(match.group(2))
    return 0

def e_formato_data(texto):
    """Verifica se o texto começa com data (DD/MM/AAAA)"""
    return bool(re.match(r'\d{2}/\d{2}/\d{4}', str(texto)))

def analisar_pente_fino(caminho):
    print(f"\n🚀 INICIANDO ANÁLISE: {caminho}")
    print(f"🎯 Critérios: HE > {LIMITE_HE_MINUTOS/60}h | Faltas > {LIMITE_ABSENT_MINUTOS/60}h sem justificativa.")
    print("..." * 20)
    
    alertas = []
    total_dias_analisados = 0

    try:
        with pdfplumber.open(caminho) as pdf:
            total_paginas = len(pdf.pages)
            
            for i, pagina in enumerate(pdf.pages):
                pag_num = i + 1
                
                # Feedback de progresso a cada 50 páginas
                if pag_num % 50 == 0:
                    print(f"Processando página {pag_num} de {total_paginas}...")

                # Tenta pegar o nome do funcionário
                texto_pag = pagina.extract_text() or ""
                nome = "Funcionario Desconhecido"
                match_nome = re.search(r'Nome:\s+(.*?)\s+Chapa:', texto_pag)
                if match_nome:
                    nome = match_nome.group(1).strip()

                tabelas = pagina.extract_tables()
                for tabela in tabelas:
                    for linha in tabela:
                        # 1. Filtro Básico: Ignora linhas vazias
                        if not linha: continue
                        
                        # 2. Filtro de Data: Só analisa se a linha começar com uma data válida
                        if not e_formato_data(linha[0]): continue

                        total_dias_analisados += 1

                        col_data = linha[0]
                        
                        # --- LÓGICA INTELIGENTE PARA LINHAS QUEBRADAS ---
                        # Se a linha for longa (normal)
                        if len(linha) >= 10:
                            col_he     = linha[-4]
                            col_absent = linha[-3]
                            col_obs    = linha[-1]
                        
                        # Se a linha for curta (mesclada pelo "Ausente")
                        else:
                            col_he = "00:00"
                            col_absent = "00:00"
                            # Procura o maior horário na linha (será a falta)
                            for item in linha:
                                if re.search(r'\d{2}:\d{2}', str(item)):
                                    if converter_minutos(item) > converter_minutos(col_absent):
                                        col_absent = item
                            
                            # A observação costuma ser o último item.
                            # Mas se o último item for horário, então Obs está vazia.
                            ultimo_item = str(linha[-1]).strip()
                            if converter_minutos(ultimo_item) > 0:
                                col_obs = ""
                            else:
                                col_obs = ultimo_item

                        # Normaliza Observação (MAIÚSCULO)
                        obs_texto = str(col_obs).strip().upper() if col_obs else ""

                        # ---------------------------------------------------------
                        # REGRA 1: HORA EXTRA ALTA
                        # ---------------------------------------------------------
                        mins_he = converter_minutos(col_he)
                        if mins_he > LIMITE_HE_MINUTOS:
                            alertas.append({
                                "pag": pag_num, "nome": nome, "data": col_data,
                                "tipo": "⚠️ ALERTA: HORA EXTRA",
                                "detalhe": f"Marcou: {col_he} (> 2h)",
                                "obs_lida": obs_texto
                            })

                        # ---------------------------------------------------------
                        # REGRA 2: AUSÊNCIAS / FALTAS
                        # ---------------------------------------------------------
                        mins_absent = converter_minutos(col_absent)
                        
                        # Verifica se está escrito "Ausente" na linha
                        linha_inteira = " ".join([str(c) for c in linha if c]).upper()
                        tem_texto_ausente = "AUSENTE" in linha_inteira
                        
                        # GATILHO: Tem mais de 1h de desconto OU apareceu "Ausente"?
                        if (mins_absent > LIMITE_ABSENT_MINUTOS) or tem_texto_ausente:
                            
                            eh_justificado = False

                            # Verifica se a observação "salva" o funcionário (Lista Branca)
                            if obs_texto: 
                                for palavra in PALAVRAS_JUSTIFICADAS:
                                    if palavra in obs_texto:
                                        eh_justificado = True
                                        break
                            
                            # Se NÃO achou justificativa válida
                            if not eh_justificado:
                                motivo_erro = "Campo Observação Vazio" if not obs_texto else f"Motivo não aceito: {col_obs}"
                                
                                alertas.append({
                                    "pag": pag_num, "nome": nome, "data": col_data,
                                    "tipo": "🔴 CRÍTICO: FALTA",
                                    "detalhe": f"Tempo: {col_absent} | {motivo_erro}",
                                    "obs_lida": obs_texto
                                })

    except Exception as e:
        print(f"\n❌ ERRO FATAL: {e}")
        print("Verifique se o arquivo está fechado e se o nome está correto.")
        return [], 0

    return alertas, total_dias_analisados

# ==============================================================================
# EXECUÇÃO DO RELATÓRIO
# ==============================================================================
if __name__ == "__main__":
    resultado, total_dias = analisar_pente_fino(ARQUIVO_PDF)

    print("\n" + "="*80)
    print(f"📊 RELATÓRIO FINAL DE AUDITORIA")
    print(f"Total de linhas (dias) analisados: {total_dias}")
    print(f"Irregularidades encontradas: {len(resultado)}")
    print("="*80)

    if len(resultado) == 0:
        print("\n✅ SUCESSO! Nenhuma irregularidade encontrada nos parâmetros definidos.")
    else:
        print(f"{'PÁG':<5} | {'DATA':<10} | {'FUNCIONÁRIO':<25} | {'PROBLEMA'}")
        print("-" * 90)
        
        for r in resultado:
            nome_limpo = (r['nome'][:23] + '..') if len(r['nome']) > 23 else r['nome']
            print(f"{r['pag']:<5} | {r['data']:<10} | {nome_limpo:<25} | {r['tipo']}")
            print(f"      ↳ Detalhe: {r['detalhe']}")
            print("-" * 90)

    input("\nPressione ENTER para fechar...")