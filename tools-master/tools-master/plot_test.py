import matplotlib.pyplot as plt
import numpy as np

def plot_airfoil(dat_file, output_file="airfoil.png", profile_name="NACA 0012"):
    # Carica i dati dal file .dat (salvato da XFOIL)
    coords = np.loadtxt(dat_file, skiprows=1)  # spesso la prima riga è un header
    x, y = coords[:, 0], coords[:, 1]

    # Crea la figura
    fig, ax = plt.subplots(figsize=(8, 4))  # dimensioni in pollici
    ax.plot(x, y, 'k-', linewidth=1.5)      # profilo in nero

    # Imposta rapporto 1:1 sugli assi (scala reale)
    ax.set_aspect('equal', adjustable='box')

    # Limiti asse y da -1 a 1
    ax.set_ylim(-1, 1)
    ax.set_xlim(-1, 2)

    # Sfondo bianco
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    # Etichette assi
    ax.set_xlabel("x / c")
    ax.set_ylabel("y / c")

    ax.set_title(f"Profilo alare: {profile_name}", fontsize=14, fontweight='bold')

    # Margini automatici sugli assi x
    ax.margins(0.05)

    # Griglia sottile (opzionale)
    ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)

    # Salva l’immagine in PNG con alta risoluzione
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()

# Esempio di utilizzo
plot_airfoil("n0012_open.dat", "naca0012.png", "NACA 0012")
