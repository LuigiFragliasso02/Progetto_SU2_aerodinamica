import matplotlib.pyplot as plt

# --- I tuoi dati ---
# Asse X: 1/Nc
x_dati = [0.007751937984, 0.003891050584, 0.001949317739, 0.001]
# x_dati = [0.007751937984, 0.003891050584, 0.001949317739]


# Asse Y: Cl
y_dati = [0.212968, 0.216994, 0.22487, 0.226532]
# y_dati = [0.212968, 0.216994, 0.22487]


# --- Creazione del Grafico ---

# 1. Crea la figura e gli assi
plt.figure(figsize=(10, 7))

# 2. Disegna i punti e la linea
# Matplotlib unirà i punti nell'ordine in cui li fornisci.
# Per mostrare la convergenza da dx a sx, ordiniamo i dati per x decrescente.
# (Questo passaggio è facoltativo ma produce il grafico più comune per la convergenza)
punti_ordinati = sorted(zip(x_dati, y_dati), reverse=True)
x_ordinato, y_ordinato = zip(*punti_ordinati)

plt.plot(x_ordinato, y_ordinato, marker='o', linestyle='-', color='red', label='Dati numerici')

# 3. Aggiungi etichette, titolo e griglia
plt.xlabel("1/Nc (h)")
plt.ylabel("Cl")
plt.title("Convergenza del Cl")
plt.grid(True)
plt.legend()

# 4. Mostra il grafico
plt.show()

# Se vuoi salvarlo su file:
# plt.savefig("mio_grafico_convergenza.png")