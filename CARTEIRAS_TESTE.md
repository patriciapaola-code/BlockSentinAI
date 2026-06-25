# 📋 Guia de Carteiras para Teste - Sistema de Rastreamento de Ransomware

## 🎯 Carteiras Recomendadas

### ✅ **SEGWIT (Recomendado - bc1q...)**
Estas funcionam melhor com a API Blockstream:

```
bc1qjuqyesxjgravlf0evtz5p8ks8k2w6ytcherrk3
bc1qeca5hd7m9latsls46ty7u5udrvwclzq4nn64n4
```

---

### ✅ **LEGACY (1... ou 3...)**
Formato antigo mas ainda ativo:

```
1A1z7agoat4EvZ8eD6gL2pmCe4Sj7jzRH4           (Satoshi's primeira carteira)
16FnhJgft5PxM3QNRjq9FiafkKHAAv8Ngy          (Carteira com atividade histórica)
1dice8EMCQAqQSN3LGzJ72b3FYYyHBiUSo          (Dice gambling - padrões interessantes)
3J98t1WpEZ73CNmYviecrnyiWrnqRhWNLy          (Multisig - estrutura complexa)
```

---

## 🚨 Histórico Público de Ransomware

### WannaCry (2017)
```
15XVFNWF17LVJBvvKKYjdvxKPX6EEoJv4S
```

### NotPetya (2017)
```
1GvzuqohmDezKxKzNfYL26xAQPJpP3xHNB
```

### Emotet (2018)
```
1HfNwXnYLhGzX1GvK4j6oE7V8wDgpEMtJm
```

---

## 🔍 Onde Encontrar Carteiras Reais

### 1. **Blockchain.com**
   - URL: https://blockchain.com/explorer
   - Busque por endereço ou transação
   - Histórico completo com visualização

### 2. **Blockchair**
   - URL: https://blockchair.com
   - Excelente para análise de padrões
   - Dados em tempo real

### 3. **Chainalysis**
   - URL: https://www.chainalysis.com/
   - Base de dados de ransomware conhecido
   - Requer autenticação (acesso acadêmico)

### 4. **Elliptic**
   - URL: https://www.elliptic.co/
   - Classificação de risco de carteiras
   - API pública limitada

### 5. **OXT.me** (OnionChain)
   - Especializado em análise de padrões
   - Ótimo para mixers e CoinJoin

---

## ✨ Dicas para Testar

### Para Iniciantes
```
Profundidade: 2-3
Máx Vizinhos: 50
Máx Nós: 200
Sensibilidade: Baixa
```
→ Análise rápida (~1-2 minutos)

### Intermediário
```
Profundidade: 4
Máx Vizinhos: 100
Máx Nós: 500
Sensibilidade: Médio
```
→ Análise balanceada (~3-5 minutos)

### Avançado
```
Profundidade: 5-6
Máx Vizinhos: 200-300
Máx Nós: 500 (máximo)
Sensibilidade: Alto
```
→ Análise profunda (~10-15 minutos)

---

## ⚠️ Solução de Problemas

### "Processando blockchain..." - Trava

**Problema:** O processamento não progride

**Soluções:**
1. ✅ Reduza a profundidade de 4 para 2
2. ✅ Reduza "Máximo de vizinhos" para 50
3. ✅ Use uma carteira diferente com mais histórico
4. ✅ Verifique a conexão internet (API Blockstream pode estar lenta)

### Carteira sem dados

**Problema:** "Grafo vazio" ou "sem transações"

**Soluções:**
1. ✅ Certifique-se de usar uma carteira SegWit válida (bc1q...)
2. ✅ Use uma das carteiras sugeridas acima
3. ✅ Teste em blockchain.com antes para confirmar atividade

### Erro de memória

**Problema:** "Out of memory" ou aplicação congela

**Soluções:**
1. ✅ Reduza "Máximo de nós" de 500 para 300
2. ✅ Reduza "Máximo de vizinhos" de 100 para 50
3. ✅ Feche outros programas para liberar RAM

---

## 🔗 Estrutura Bitcoin Explicada

### Tipos de Endereço

| Prefixo | Nome | Formato | Ano | Vantagem |
|---------|------|--------|-----|----------|
| `1...` | P2PKH (Legacy) | 26-35 caracteres | 2009 | Compatibilidade |
| `3...` | P2SH (Multisig) | 26-35 caracteres | 2012 | Segurança |
| `bc1q...` | SegWit v0 | 42-62 caracteres | 2017 | 30-40% mais compacto |
| `bc1p...` | Taproot (SegWit v1) | 62 caracteres | 2021 | Privacy melhorada |

**Recomendação:** Use `bc1q...` (SegWit) para melhor performance com a API

---

## 📊 Padrões a Procurar

### Fan-in Elevado
- Múltiplas carteiras enviando fundos para 1 endereço
- Indicador de consolidação
- Comum em ransomware

### Fan-out Elevado
- 1 carteira distribuindo fundos para múltiplas endereços
- Indicador de dispersão
- Comum em mixers

### Possível Mixer
- Muitas entradas + muitas saídas
- Valores diferentes
- Padrão caótico
- Indicador de lavagem de dinheiro

### Cadeia Rápida
- Sequências A→B→C→D
- Transações em minutos
- Indicador de automação/bot

### Valores Fracionados
- 10 BTC → 5×2 BTC
- Padrão de ocultação
- Comum em evasão de KYC

---

## 🎯 Próximos Passos

1. Teste com carteiras sugeridas acima
2. Observe os padrões detectados
3. Compare com histórico em blockchain.com
4. Use sensibilidade "Médio" como padrão
5. Ajuste parâmetros conforme necessário

**Sucesso na análise!** 🚀
