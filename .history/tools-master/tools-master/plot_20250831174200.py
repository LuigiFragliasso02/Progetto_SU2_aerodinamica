import os
import re
import pandas as pd
import matplotlib.pyplot as plt

# Directory per salvare i grafici
PLOT_DIR = "plot_tesi"
os.makedirs(PLOT_DIR, exist_ok=True)

# =======================
# Funzione robusta per leggere e pulire i file CSV
# =======================
def safe_read_csv(filepath):
    """
    Legge un file CSV potenzialmente "sporco", pulisce i dati e le colonne,
    e restituisce un DataFrame pronto per l'analisi.
    """
    try:
        df = pd.read_csv(filepath, on_bad_lines="skip")
        df = df.dropna(how="all")
        # Pulisce i nomi delle colonne (minuscolo e senza spazi)
        df.columns = [str(c).strip().lower() for c in df.columns]
        # Sostituisce la virgola con il punto per i decimali
        df = df.replace(",", ".", regex=True)

        # Funzione interna per trovare una colonna tra più nomi possibili
        def trova_col(possibili_nomi):
            for nome in possibili_nomi:
                if nome in df.columns:
                    # Converte in numerico, trasformando errori in NaN (Not a Number)
                    col = pd.to_numeric(df[nome], errors="coerce")
                    if col.notna().sum() > 0: # Controlla se c'è almeno un valore valido
                        return col
            return pd.Series([None] * len(df)) # Ritorna una colonna vuota se non trova nulla

        # Costruisce il DataFrame pulito
        dati = pd.DataFrame()
        dati["alfa"] = trova_col(["alfa", "aoa"])
        dati["cl"] = trova_col(["cl", "unnamed: 1", "unnamed: 2"])
        dati["cd"] = trova_col(["cd", "unnamed: 3", "unnamed: 4", "unnamed: 5"])
        
        # Rimuove le righe dove 'alfa' non è valido
        dati = dati.dropna(subset=["alfa"])
        return dati
    except FileNotFoundError:
        print(f"ATTENZIONE: Il file '{filepath}' non è stato trovato. Verrà saltato.")
        return pd.DataFrame() # Ritorna un DataFrame vuoto se il file non esiste
    except Exception as e:
        print(f"ERRORE durante la lettura di '{filepath}': {e}")
        return pd.DataFrame()

# =======================
# 1. Plot Convergenza Spaziale (logica invariata)
# =======================
def plot_convergenza():
    files = [
        ("ALL_AOA_i=0.000_129x64/dati_numerici_n0012_129_65_i0.csv", "129x65"),
        ("ALL_AOA_i=0.000_257x129/dati_numerici_n0012_257_129_i0.000.csv", "257x129"),
        ("ALL_AOA_i=0.000_513x257/dati_numerici_n0012_513_257_i0.csv", "513x257"),
        ("ALL_AOA_i=0.000_1000x512/dati_numerici_n0012_1000_513_i0.csv", "1000x513"),
    ]

    x_cl, y_cl = [], []
    data_cd = {0: ([], []), 10: ([], []), 16: ([], [])}

    print("--- 1. Inizio Elaborazione per Convergenza Spaziale ---")
    for filepath, label in files:
        if not os.path.exists(filepath):
            print(f"ATTENZIONE: Il file '{filepath}' non è stato trovato.")
            continue
        try:
            df = pd.read_csv(filepath)
            df.columns = df.columns.str.strip()
            angle_col = 'AOA' if 'AOA' in df.columns else 'alfa'

            # --- ECCO LA CORREZIONE ---
            # Cerca solo le cifre seguite da 'x', senza il trattino basso iniziale
            match = re.search(r'(\d+)x', label) 
            
            if not match:
                print(f"ATTENZIONE: Impossibile estrarre N da '{label}'.")
                continue
            
            N = int(match.group(1))
            x_val = 1 / N

            # Estrazione dati per Cl
            cl_row = df[df[angle_col] == 2]
            if not cl_row.empty:
                x_cl.append(x_val)
                y_cl.append(cl_row['Cl'].iloc[0])

            # Estrazione dati per Cd
            for alfa_val in [0, 10, 16]:
                if alfa_val == 0 or N != 1000: # Condizione originale
                    cd_row = df[df[angle_col] == alfa_val]
                    if not cd_row.empty:
                        data_cd[alfa_val][0].append(x_val)
                        data_cd[alfa_val][1].append(cd_row['Cd'].iloc[0])
            print(f"OK: {filepath}")
        except Exception as e:
            print(f"ERRORE durante l'elaborazione di '{filepath}': {e}")

    fig, axs = plt.subplots(2, 2, figsize=(15, 11))
    fig.suptitle('Analisi di Convergenza Spaziale', fontsize=18, fontweight='bold')

    def sort_and_plot(ax, x_data, y_data, color, title):
        if x_data and y_data:
            punti_ordinati = sorted(zip(x_data, y_data))
            x_ordinato, y_ordinato = zip(*punti_ordinati)
            # Aggiunto il 'label' qui per farlo apparire in legenda
            ax.plot(x_ordinato, y_ordinato, marker='o', linestyle='-', color=color, label='Dati numerici')
        else:
            ax.text(0.5, 0.5, 'Dati non disponibili', ha='center', va='center')
        
        ax.set_title(title, fontsize=12)
        ax.set_xlabel('1/N (h)', fontsize=10)
        ax.set_ylabel('Coefficiente', fontsize=10)
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.legend() # Ora troverà il label 'Dati numerici'

    sort_and_plot(axs[0, 0], x_cl, y_cl, 'red', 'Convergenza $C_l$ per $\\alpha=2^\\circ$')
    sort_and_plot(axs[0, 1], data_cd[0][0], data_cd[0][1], 'blue', 'Convergenza $C_d$ per $\\alpha=0^\\circ$')
    sort_and_plot(axs[1, 0], data_cd[10][0], data_cd[10][1], 'green', 'Convergenza $C_d$ per $\\alpha=10^\\circ$')
    sort_and_plot(axs[1, 1], data_cd[16][0], data_cd[16][1], 'purple', 'Convergenza $C_d$ per $\\alpha=16^\\circ$')

    axs[0, 0].invert_yaxis()
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    save_path = os.path.join(PLOT_DIR, "1_convergenza_spaziale.png")
    plt.savefig(save_path)
    print(f"Grafico di convergenza salvato in: '{save_path}'\n")

# =======================
# 2. Funzione di plot generica per i coefficienti
# =======================
# def plot_coefficiente(files, labels, outpath, y_col, title, y_label):
#     """
#     Funzione generica per plottare un coefficiente (es. Cl, Cd) contro alfa.
#     """
#     print(f"--- Inizio Elaborazione per: {title} ---")
#     plt.figure(figsize=(10, 7))
    
#     for filepath, label in zip(files, labels):
#         df = safe_read_csv(filepath)
#         # Controlla se il DataFrame e le colonne necessarie non sono vuote
#         if not df.empty and y_col in df.columns and not df[y_col].dropna().empty:
#             # Ordina per alfa per assicurare che la linea sia disegnata correttamente
#             df_sorted = df.sort_values(by="alfa")
#             plt.plot(df_sorted["alfa"], df_sorted[y_col], marker="o", linestyle="-", label=label)
            
#     plt.xlabel("Alfa [°]")
#     plt.ylabel(y_label)
#     plt.title(title)
#     plt.grid(True)
#     plt.legend()
#     plt.savefig(outpath)
#     plt.close() # Chiude la figura per liberare memoria
#     print(f"Grafico '{title}' salvato in: '{outpath}'\n")
# =======================
# 2. Funzione di plot generica per i coefficienti (AGGIORNATA)
# =======================
def plot_coefficiente(files, labels, outpath, x_col, y_col, title, x_label, y_label):
    """
    Funzione generica per plottare una relazione tra due coefficienti (es. Cl vs Alfa, Cd vs Cl).
    """
    print(f"--- Inizio Elaborazione per: {title} ---")
    plt.figure(figsize=(10, 7))
    
    for filepath, label in zip(files, labels):
        df = safe_read_csv(filepath)
        # Controlla che entrambe le colonne necessarie esistano
        if not df.empty and x_col in df.columns and y_col in df.columns:
            # Rimuove le righe dove uno dei due valori è mancante
            df_clean = df.dropna(subset=[x_col, y_col])
            if not df_clean.empty:
                # Ordina i valori in base alla colonna dell'asse X per un plot corretto
                df_sorted = df_clean.sort_values(by=x_col)
                plt.plot(df_sorted[x_col], df_sorted[y_col], marker="o", linestyle="-", label=label)
            
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    plt.grid(True)
    plt.legend()
    plt.savefig(outpath)
    plt.close()
    print(f"Grafico '{title}' salvato in: '{outpath}'\n")

# =======================
# ESECUZIONE PRINCIPALE
# =======================
if __name__ == "__main__":
    # 1. Plot di convergenza 
    plot_convergenza()

    # =====================================================================
    # 2 & 3. PLOT CONFRONTO MESH
    # =====================================================================
    files_mesh = [
        "ALL_AOA_i=0.000_129x64/dati_numerici_n0012_129_65_i0.csv",
        "ALL_AOA_i=0.000_257x129/dati_numerici_n0012_257_129_i0.000.csv",
        "ALL_AOA_i=0.000_513x257/dati_numerici_n0012_513_257_i0.csv"
    ]
    labels_mesh = ["Mesh 129x64", "Mesh 257x129", "Mesh 513x257"]

    # 2. Plot curva di portanza (Cl vs Alfa)
    plot_coefficiente(
        files=files_mesh,
        labels=labels_mesh,
        outpath=os.path.join(PLOT_DIR, "2_curva_portanza_mesh.png"),
        x_col="alfa",
        y_col="cl",
        title="Curva di Portanza - Confronto Mesh",
        x_label="Alfa [°]",
        y_label="$C_l$"
    )

    # 3. Plot curva polare (Cd vs Cl) 
    plot_coefficiente(
        files=files_mesh,
        labels=labels_mesh,
        outpath=os.path.join(PLOT_DIR, "3_curva_polare_mesh.png"),
        x_col="cl",
        y_col="cd",
        title="Curva Polare ($C_d$ vs $C_l$) - Confronto Mesh",
        x_label="$C_l$",
        y_label="$C_d$"
    )

    # =====================================================================
    # 4 & 5. PLOT CONFRONTO SIMULAZIONE VS SPERIMENTALE
    # =====================================================================
    print("\n--- Inizio Elaborazione per Confronto con Dati Sperimentali ---")
    
    files_confronto = [
        "ALL_AOA_i=0.000_513x257/dati_numerici_n0012_513_257_i0.csv",
        "ALL_AOA_i=0.000_513x257/dati_sperimentali_n0012_Ladson_i0.csv" 
    ]
    labels_confronto = ["Simulazione 513x257", "Dati Sperimentali (Ladson)"]

    # 4. Plot confronto curva di portanza (Cl vs Alfa)
    plot_coefficiente(
        files=files_confronto,
        labels=labels_confronto,
        outpath=os.path.join(PLOT_DIR, "4_confronto_portanza.png"),
        x_col="alfa",
        y_col="cl",
        title="Confronto Portanza (Simulazione vs Dati Sperimentali)",
        x_label="Alfa [°]",
        y_label="$C_l$"
    )

    # 5. Plot confronto curva polare (Cd vs Cl)
    plot_coefficiente(
        files=files_confronto,
        labels=labels_confronto,
        outpath=os.path.join(PLOT_DIR, "5_confronto_polare.png"),
        x_col="cl",
        y_col="cd",
        title="Confronto Polare ($C_d$ vs $C_l$) (Simulazione vs Dati Sperimentali)",
        x_label="$C_l$",
        y_label="$C_d$"
    )

    # =======================
    # 6. PLOT: Confronto curva di portanza per diverse incidenze/condizioni
    # =======================
    print("\n--- Inizio Elaborazione per Plot 6: Confronto Portanza Nuove Condizioni ---")

    files_nuove_condizioni = [
        "ALL_AOA_i=0.000_513x257/dati_sperimentali_n0012_Ladson_i0.002_i0005.csv", # Assumendo .csv
        "ALL_AOA_i=0.000_513x257/dati_numerici_n0012_513_257_i0.002.csv",          # Assumendo .csv
        "ALL_AOA_i=0.000_513x257/dati_numerici_n0012_513_257_i0.005.csv"           # Assumendo .csv
    ]
    labels_nuove_condizioni = [
        "Sperimentale i0.002_i0005",
        "Numerico i0.002",
        "Numerico i0.005"
    ]

    plot_coefficiente(
        files=files_nuove_condizioni,
        labels=labels_nuove_condizioni,
        outpath=os.path.join(PLOT_DIR, "6_confronto_portanza_nuove_condizioni.png"),
        x_col="alfa",
        y_col="cl",
        title="Curva di Portanza - Confronto Nuove Condizioni",
        x_label="Alfa [°]",
        y_label="$C_l$"
    )

    print("\n✅ Tutti i plot sono stati generati con successo.")