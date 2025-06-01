import random

# Exceções personalizadas
class MatrizNaoQuadrada(Exception):
    def __init__(self, msg="A matriz deve ser quadrada (mesmo número de linhas e colunas)."):
        super().__init__(msg)

class MatrizSingular(Exception):
    def __init__(self, msg="Pivô zero ou matriz singular!"):
        super().__init__(msg)

def salvar_em_arquivo(A, L, U):
    with open("resultado_decomposicao_LU.txt", "w") as f:
        n = len(A)
        f.write("=== Decomposição LU ===\n\n")

        f.write("Matriz A:\n")
        for linha in A:
            f.write('  '.join(f"{x:.4f}" for x in linha) + '\n')

        f.write("\nMatriz L:\n")
        for linha in L:
            f.write('  '.join(f"{x:.4f}" for x in linha) + '\n')

        f.write("\nMatriz U:\n")
        for linha in U:
            f.write('  '.join(f"{x:.4f}" for x in linha) + '\n')

def decompor_LU(A):
    n = len(A)
    L = [[0.0] * n for _ in range(n)]
    U = [[0.0] * n for _ in range(n)]

    # Verifica se a matriz é quadrada
    for linha in A:
        if len(linha) != n:
            raise MatrizNaoQuadrada()

    for k in range(n):
        for j in range(k, n):
            soma = sum(L[k][s] * U[s][j] for s in range(k))
            U[k][j] = A[k][j] - soma

        if abs(U[k][k]) < 1e-12:
            raise MatrizSingular()

        for i in range(k + 1, n):
            soma = sum(L[i][s] * U[s][k] for s in range(k))
            L[i][k] = (A[i][k] - soma) / U[k][k]

        L[k][k] = 1.0

    if n <= 10:
        print("\n=== Decomposição LU ===\n")
        print("Matriz A:")
        for linha in A:
            print('  '.join(f"{x:.4f}" for x in linha))
        print("\nMatriz L:")
        for linha in L:
            print('  '.join(f"{x:.4f}" for x in linha))
        print("\nMatriz U:")
        for linha in U:
            print('  '.join(f"{x:.4f}" for x in linha))
    else:
        print("Matriz grande. Resultados salvos no arquivo.")

    salvar_em_arquivo(A, L, U)

def entrada_manual():
    while True:
        try:
            n = int(input("Tamanho da matriz quadrada: "))
            if n <= 0:
                print("Informe um valor positivo.")
                continue
            break
        except ValueError:
            print("Entrada inválida.")

    A = []
    for i in range(n):
        linha = []
        for j in range(n):
            while True:
                try:
                    val = float(input(f"A[{i}][{j}]: "))
                    linha.append(val)
                    break
                except ValueError:
                    print("Número inválido.")
        A.append(linha)
    return A

def gerar_matriz(n, minimo=-10, maximo=10):
    return [[random.uniform(minimo, maximo) for _ in range(n)] for _ in range(n)]

def main():
    print("Como você quer montar a matriz?")
    print("1 - Inserir manualmente")
    print("2 - Gerar automaticamente")

    while True:
        op = input("Opção: ").strip()
        if op == '1':
            A = entrada_manual()
            break
        elif op == '2':
            while True:
                try:
                    tamanho = int(input("Tamanho da matriz: "))
                    if tamanho <= 0:
                        print("Digite um número positivo.")
                        continue
                    break
                except ValueError:
                    print("Entrada inválida.")
            A = gerar_matriz(tamanho)
            break
        else:
            print("Opção inválida. Tente novamente.")

    try:
        decompor_LU(A)
    except (MatrizNaoQuadrada, MatrizSingular) as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    main()
