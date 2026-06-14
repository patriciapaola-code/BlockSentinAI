import sys

def leitura():
    print(sys.executable)

    import pandas as pd

    df = pd.read_csv("transacoesbtcsimples.csv")

    print("Dados carregados:")
    print(df)