// ==========================================================
// Trabalho Pratico — Comparacao entre Mergesort e Quicksort
// Autor: Andrei Faccin
// ==========================================================
//
// Este programa em C implementa e compara dois algoritmos
// classicos de ordenacao: MERGESORT e QUICKSORT.
//
// Para fazer esse trabalho foi utilizado:
//  - Os links que o professor disponibilizou no pdf.
//  - Consultas ao chatGPT para me ajudar a entender e resolver o problema proposto.
//
// O objetivo e medir:
//   1) Tempo de execucao (em nanossegundos).
//   2) Memoria dinamica usada pelo algoritmo.
//
// Para isso:
//   - Rodei ambos algoritmos em diferentes cenarios de entrada:
//       * vetor ja ordenado (crescente)
//       * vetor inverso (decrescente)
//       * vetor aleatorio
//   - Testei diferentes tamanhos de entrada: 
//       100, 1000, 2000, 3000, 4000, 5000, 10000.
//   - Repeti cada experimento 30 vezes.
//   - Gerei arquivos CSV com os resultados.
//
// Depois, esses arquivos podem ser usados para gerar graficos
// e escrever o relatorio final.
//
// ==========================================================

#include <stdio.h>    // entrada/saida (printf, fprintf, fopen, etc.)
#include <stdlib.h>   // malloc, free, rand, srand
#include <string.h>   // memcpy
#include <stdint.h>   // tipos inteiros portateis (uint64_t)
#include <inttypes.h> // para imprimir uint64_t com PRIu64
#include <time.h>     // medir tempo com clock_gettime

#ifndef ELEM_T
#define ELEM_T double
#endif

// ----------------------------------------------------------
// Funcao para medir tempo em nanossegundos
// ----------------------------------------------------------
static uint64_t now_ns(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000000000ULL + (uint64_t)ts.tv_nsec;
}

// ----------------------------------------------------------
// Rastreador de memoria dinamica
// ----------------------------------------------------------
static size_t mt_current = 0; // memoria atual em uso
static size_t mt_peak = 0;    // pico maximo durante a execucao

// Reinicia o contador
static void mt_reset(void) { mt_current = 0; mt_peak = 0; }

// Consulta o pico de memoria
static size_t mt_peak_bytes(void) { return mt_peak; }

// Versao "monitorada" do malloc
static void* mt_malloc(size_t sz) {
    void* p = malloc(sz);
    if (p) {
        mt_current += sz;
        if (mt_current > mt_peak) mt_peak = mt_current;
    }
    return p;
}

// Versao "monitorada" do free
static void mt_free(void* p, size_t sz) {
    if (p) {
        free(p);
        if (mt_current >= sz) mt_current -= sz;
        else mt_current = 0;
    }
}

// ----------------------------------------------------------
// Funcoes utilitarias simples
// ----------------------------------------------------------

// compara se um elemento e menor que outro
static inline int less(ELEM_T a, ELEM_T b) { return a < b; }

// troca o conteudo de duas posicoes do vetor
static inline void swap(ELEM_T* a, ELEM_T* b) {
    ELEM_T t = *a; *a = *b; *b = t;
}

// ----------------------------------------------------------
// Implementacao do QUICKSORT
// ----------------------------------------------------------
// Usei a particao de Lomuto:
//   - pivo = ultimo elemento do subvetor
//   - percorremos o subvetor rearranjando os elementos
// ----------------------------------------------------------
static long partition_lomuto(ELEM_T* arr, long low, long high) {
    ELEM_T pivot = arr[high];
    long i = low - 1;
    for (long j = low; j < high; ++j) {
        if (arr[j] <= pivot) { // se menor ou igual ao pivo
            i++;
            swap(&arr[i], &arr[j]);
        }
    }
    swap(&arr[i+1], &arr[high]);
    return i+1;
}

static void quicksort_rec(ELEM_T* arr, long low, long high) {
    if (low < high) {
        long p = partition_lomuto(arr, low, high);
        quicksort_rec(arr, low, p - 1);
        quicksort_rec(arr, p + 1, high);
    }
}

static void quicksort(ELEM_T* arr, size_t n) {
    if (n > 1) quicksort_rec(arr, 0, (long)n - 1);
}

// ----------------------------------------------------------
// Implementacao do MERGESORT
// ----------------------------------------------------------
// O mergesort e um algoritmo "dividir e conquistar":
//   - divide o vetor em duas metades
//   - ordena cada metade recursivamente
//   - depois faz um merge nas duas metades ordenadas
//
// Precisa de memoria auxiliar O(n) para juntar as metades.
// ----------------------------------------------------------
static void merge(ELEM_T* a, ELEM_T* aux, size_t left, size_t mid, size_t right) {
    size_t i = left, j = mid + 1, k = left;
    while (i <= mid && j <= right) {
        if (a[i] <= a[j]) aux[k++] = a[i++];
        else aux[k++] = a[j++];
    }
    while (i <= mid) aux[k++] = a[i++];
    while (j <= right) aux[k++] = a[j++];
    for (k = left; k <= right; ++k) a[k] = aux[k];
}

static void mergesort_rec(ELEM_T* a, ELEM_T* aux, size_t left, size_t right) {
    if (left >= right) return;
    size_t mid = left + (right - left) / 2;
    mergesort_rec(a, aux, left, mid);
    mergesort_rec(a, aux, mid + 1, right);
    merge(a, aux, left, mid, right);
}

static void mergesort(ELEM_T* a, size_t n) {
    if (n < 2) return;
    size_t bytes = n * sizeof(ELEM_T);
    ELEM_T* aux = (ELEM_T*)mt_malloc(bytes); // aloca memoria extra
    mergesort_rec(a, aux, 0, n - 1);
    mt_free(aux, bytes); // libera memoria
}

// ----------------------------------------------------------
// Geracao dos cenarios de entrada
// ----------------------------------------------------------
typedef enum { ASC = 0, DESC = 1, RANDOM = 2 } scenario_t;

// vetor ja ordenado em ordem crescente
static void fill_asc(ELEM_T* a, size_t n) {
    for (size_t i = 0; i < n; ++i) a[i] = (ELEM_T)i;
}

// vetor em ordem decrescente
static void fill_desc(ELEM_T* a, size_t n) {
    for (size_t i = 0; i < n; ++i) a[i] = (ELEM_T)(n - 1 - i);
}

// vetor aleatorio
static void fill_random(ELEM_T* a, size_t n, unsigned int seed) {
    srand(seed);
    for (size_t i = 0; i < n; ++i) {
        a[i] = (ELEM_T)(rand() % 1000000); // numeros ate 1 milhao
    }
}

// ----------------------------------------------------------
// Verificacao de corretude: confere se vetor ficou ordenado
// ----------------------------------------------------------
static int is_sorted(const ELEM_T* a, size_t n) {
    for (size_t i = 1; i < n; ++i) {
        if (a[i] < a[i-1]) return 0; // encontrou inversao
    }
    return 1;
}

// ----------------------------------------------------------
// Funcoes auxiliares para salvar resultados em CSV
// ----------------------------------------------------------
static void write_csv_header(FILE* f) {
    fprintf(f, "algorithm,type,scenario,n,run,time_ns,peak_dynamic_bytes\n");
}

static const char* scenario_name(scenario_t s) {
    switch (s) {
        case ASC: return "asc"; case DESC: return "desc"; default: return "random";
    }
}

static const char* type_name(void) {
#if defined(ELEM_T_IS_INT)
    return "int";
#elif defined(ELEM_T_IS_FLOAT)
    return "float";
#elif defined(ELEM_T_IS_DOUBLE)
    return "double";
#else
    return "unknown";
#endif
}

// ----------------------------------------------------------
// Funcao principal
// ----------------------------------------------------------
int main(void) {
    // tamanhos a testar
    const size_t Ns[] = {100, 1000, 2000, 3000, 4000, 5000, 10000};
    const size_t n_Ns = sizeof(Ns)/sizeof(Ns[0]);
    const int RUNS = 30; // numero de repeticoes

    // define nome do arquivo de saida (depende do tipo)
    char results_file[128];
    snprintf(results_file, sizeof(results_file), "results_%s.csv", type_name());

    FILE* out = fopen(results_file, "w");
    write_csv_header(out);

    // aloca vetores auxiliares
    size_t maxN = Ns[n_Ns - 1];
    ELEM_T* master = (ELEM_T*)malloc(maxN * sizeof(ELEM_T)); // base
    ELEM_T* work   = (ELEM_T*)malloc(maxN * sizeof(ELEM_T)); // copia para ordenar

    // para cada tamanho de entrada
    for (size_t iN = 0; iN < n_Ns; ++iN) {
        size_t n = Ns[iN];
        // para cadacenario (asc, desc, random)
        for (int s = 0; s < 3; ++s) {
            scenario_t sc = (scenario_t)s;
            // repete 30 vezes
            for (int run = 1; run <= RUNS; ++run) {

                // gera vetor base de acordo com cenario
                if (sc == ASC) fill_asc(master, n);
                else if (sc == DESC) fill_desc(master, n);
                else fill_random(master, n, 42 + run);

                // ---------- MERGESORT ----------
                memcpy(work, master, n * sizeof(ELEM_T));
                mt_reset(); // zera contador de memoria
                uint64_t t0 = now_ns();     // inicio do cronometro
                mergesort(work, n);         // executa ordenacao
                uint64_t t1 = now_ns();     // fim do cronometro
                if (!is_sorted(work, n)) { fprintf(stderr, "Erro mergesort\n"); return 1; }
                fprintf(out, "mergesort,%s,%s,%zu,%d,%" PRIu64 ",%zu\n",
                        type_name(), scenario_name(sc), n, run, (t1 - t0), mt_peak_bytes());

                // ---------- QUICKSORT ----------
                memcpy(work, master, n * sizeof(ELEM_T));
                mt_reset(); // quicksort nao usa malloc, entao fica 0
                t0 = now_ns();
                quicksort(work, n);
                t1 = now_ns();
                if (!is_sorted(work, n)) { fprintf(stderr, "Erro quicksort\n"); return 1; }
                fprintf(out, "quicksort,%s,%s,%zu,%d,%" PRIu64 ",%zu\n",
                        type_name(), scenario_name(sc), n, run, (t1 - t0), mt_peak_bytes());
            }
        }
    }

    fclose(out);
    free(master);
    free(work);
    return 0;
}
