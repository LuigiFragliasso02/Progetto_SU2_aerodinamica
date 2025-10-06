
import os
import re
import pandas as pd
import matplotlib.pyplot as plt

# Directory per salvare i grafici
PLOT_DIR = "plot_tesi_per_elaborato"
os.makedirs(PLOT_DIR, exist_ok=True)


def safe_read_csv(filepath):
    """
    Legge un file CSV potenzialmente "sporco", pulisce i dati e le colonne,
    e restituisce un DataFrame pronto per l'analisi.
    """
    try:
        df = pd.read_csv(filepath, on_bad_lines="skip")
        df = df.dropna(how="all")
        df.columns = [str(c).strip().lower() for c in df.columns]
        df = df.replace(",", ".", regex=True)

        def trova_col(possibili_nomi):
            for nome in possibili_nomi:
                if nome in df.columns:
                    col = pd.to_numeric(df[nome], errors="coerce")
                    if col.notna().sum() > 0:
                        return col
            return pd.Series([None] * len(df))

        dati = pd.DataFrame()
        dati["alfa"] = trova_col(["alfa", "aoa"])
        dati["cl"] = trova_col(["cl", "unnamed: 1", "unnamed: 2"])
        dati["cd"] = trova_col(["cd", "unnamed: 3", "unnamed: 4", "unnamed: 5"])
        
        return dati
    except FileNotFoundError:
        print(f"ATTENZIONE: Il file '{filepath}' non è stato trovato. Verrà saltato.")
        return pd.DataFrame()
    except Exception as e:
        print(f"ERRORE durante la lettura di '{filepath}': {e}")
        return pd.DataFrame()

# =======================
# 1. Plot Convergenza Spaziale 
# =======================

def plot_convergenza():
    """
    Versione migliorata di plot_convergenza che utilizza safe_read_csv()
    e disegna i plot con scala numerica corretta (come in plot_coefficiente).
    """
    files = [
        ("ALL_AOA_i=0.000_129x64/dati_numerici_n0012_129_65_i0.csv", "129x65"),
        ("ALL_AOA_i=0.000_257x129/dati_numerici_n0012_257_129_i0.000.csv", "257x129"),
        ("ALL_AOA_i=0.000_513x257/dati_numerici_n0012_513_257_i0.csv", "513x257"),
        ("ALL_AOA_i=0.000_1000x512/dati_numerici_n0012_1000_513_i0.csv", "1000x513"),
    ]

    x_cl, y_cl = [], []
    data_cd = {0: ([], []), 10: ([], []), 16: ([], [])}

    print("--- 1. Inizio Elaborazione per Convergenza Spaziale (SCALATA) ---")
    for filepath, label in files:
        df = safe_read_csv(filepath)
        if df.empty:
            continue

        # Estrai N dalla label
        match = re.search(r'(\d+)x', label)
        if not match:
            print(f"ATTENZIONE: Impossibile estrarre N da '{label}'.")
            continue
        N = int(match.group(1))
        x_val = 1.0 / N

        # Cl per alfa = 2
        cl_row = df[df["alfa"] == 2]
        if not cl_row.empty:
            x_cl.append(x_val)
            y_cl.append(cl_row["cl"].iloc[0])

        # Cd per alfa = 0, 10, 16
        for alfa_val in [0, 10, 16]:
            #if alfa_val == 0 or N != 1000:
                cd_row = df[df["alfa"] == alfa_val]
                if not cd_row.empty:
                    data_cd[alfa_val][0].append(x_val)
                    data_cd[alfa_val][1].append(cd_row["cd"].iloc[0])

        print(f"OK: {filepath}")

    # === Creazione figure ===
    fig, axs = plt.subplots(2, 2, figsize=(15, 11))
    fig.suptitle("Analisi di Convergenza Spaziale del NACA 0012, Re=6E06, M=0.15", fontsize=18, fontweight="bold")

    def plot_scalato(ax, x_data, y_data, color, title):
        if x_data and y_data:
            df_plot = pd.DataFrame({"x": x_data, "y": y_data}).dropna()
            df_plot = df_plot.sort_values(by="x")
            ax.plot(df_plot["x"], df_plot["y"], marker="o", linestyle="-", color=color, label="Dati numerici")

            # Limiti automatici basati sul dataset
            ax.set_xlim(df_plot["x"].min()*0.9, df_plot["x"].max()*1.1)
            ax.set_ylim(df_plot["y"].min()*0.995, df_plot["y"].max()*1.005)

        else:
            ax.text(0.5, 0.5, "Dati non disponibili", ha="center", va="center")

        ax.set_title(title, fontsize=15)
        ax.set_xlabel("1/N (h)", fontsize=12)
        ax.set_ylabel("Coefficiente", fontsize=12)
        ax.grid(True, linestyle="--", alpha=0.6)
        ax.legend()


    # Disegno i 4 grafici
    plot_scalato(axs[0, 0], x_cl, y_cl, "red", "Convergenza $C_l$ per $\\alpha=2^\\circ$")
    plot_scalato(axs[0, 1], data_cd[0][0], data_cd[0][1], "blue", "Convergenza $C_d$ per $\\alpha=0^\\circ$")
    plot_scalato(axs[1, 0], data_cd[10][0], data_cd[10][1], "green", "Convergenza $C_d$ per $\\alpha=10^\\circ$")
    plot_scalato(axs[1, 1], data_cd[16][0], data_cd[16][1], "purple", "Convergenza $C_d$ per $\\alpha=16^\\circ$")

    # axs[0, 0].invert_yaxis()  # come nell'originale
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])

    save_path = os.path.join(PLOT_DIR, "1_convergenza_spaziale_scalata.png")
    plt.savefig(save_path)
    plt.close()
    print(f"Grafico di convergenza SCALATO salvato in: '{save_path}'\n")


def plot_coefficiente(files, plot_configs, outpath, x_col, y_col, title, x_label, y_label,
                      x_min=None, x_max=None, y_min=None, y_max=None,
                      highlight_last_point=None,
                      label_fontsize=16, title_fontsize=18, legend_fontsize=14):
    """
    Funzione generica che accetta configurazioni di stile e può evidenziare
    l'ultimo punto di un file specifico, senza collegarlo alla linea.
    """
    print(f"--- Inizio Elaborazione per: {title} ---")
    plt.figure(figsize=(10, 7))

    point_to_highlight = None

    for i, (filepath, (label, style)) in enumerate(zip(files, plot_configs)):
        df = safe_read_csv(filepath)

        if i == highlight_last_point and not df.empty:
            last_row = df.iloc[-1]
            if x_col in last_row and y_col in last_row:
                point_to_highlight = (last_row[x_col], last_row[y_col])
            df_plot_current_series = df.iloc[:-1]
        else:
            df_plot_current_series = df

        if x_min is not None: df_plot_current_series = df_plot_current_series[df_plot_current_series[x_col] >= x_min]
        if x_max is not None: df_plot_current_series = df_plot_current_series[df_plot_current_series[x_col] <= x_max]
        if y_min is not None: df_plot_current_series = df_plot_current_series[df_plot_current_series[y_col] >= y_min]
        if y_max is not None: df_plot_current_series = df_plot_current_series[df_plot_current_series[y_col] <= y_max]

        if not df_plot_current_series.empty and x_col in df_plot_current_series.columns and y_col in df_plot_current_series.columns:
            df_clean = df_plot_current_series.dropna(subset=[x_col, y_col])
            if not df_clean.empty:
                df_sorted = df_clean.sort_values(by=x_col)
                plt.plot(df_sorted[x_col], df_sorted[y_col], label=label, **style)

    if point_to_highlight:
        plt.scatter(point_to_highlight[0], point_to_highlight[1],
                    color='green',
                    marker='o',
                    s=100,
                    label='Punto Finale Simulazione',
                    zorder=5)

    plt.xlabel(x_label, fontsize=label_fontsize)
    plt.ylabel(y_label, fontsize=label_fontsize)
    plt.title(title, fontsize=title_fontsize)
    plt.grid(True)
    plt.legend(fontsize=legend_fontsize)
    plt.savefig(outpath)
    plt.close()
    print(f"Grafico '{title}' salvato in: '{outpath}'\n")


# =======================
# ESECUZIONE PRINCIPALE
# =======================
if __name__ == "__main__":
    # Stili di plotting riutilizzabili per coerenza grafica
    stile_numerico = {'marker': 'o', 'linestyle': '-'}
    stile_numerico_1 = {'marker': 'o'}

    stile_sperimentale = {'marker': 's', 'color': 'red', 'linestyle': 'None'}
    stile_sperimentale_1 = {'marker': 's', 'color': 'red'}


    # # =====================================================================
    # # 1. Plot di Convergenza Spaziale
    # # =====================================================================
    # plot_convergenza()
    
    # # =====================================================================
    # # 2 & 3. Plot Confronto al variare del Mesh i=0, n0012
    # # =====================================================================
    # files_mesh = [
    #     "ALL_AOA_i=0.000_129x64/dati_numerici_n0012_129_65_i0.csv",
    #     "ALL_AOA_i=0.000_257x129/dati_numerici_n0012_257_129_i0.000.csv",
    #     "ALL_AOA_i=0.000_513x257/dati_numerici_n0012_513_257_i0.csv"
    # ]
    # plot_configs_mesh = [
    #     ("Mesh 129x64", stile_numerico),
    #     ("Mesh 257x129", stile_numerico),
    #     ("Mesh 513x257", stile_numerico)
    # ]
    # plot_coefficiente(files_mesh, plot_configs_mesh, os.path.join(PLOT_DIR, "2_curva_portanza_Variare_mesh_n0012_i0.png"),
    #                   x_col="alfa", y_col="cl", title="Curva di portanza al variare del mesh - NACA 0012, Re=6E06, M=0.15", x_label="Alfa [°]", y_label="$C_l$", label_fontsize=16, title_fontsize=15, legend_fontsize=16)
    # plot_coefficiente(files_mesh, plot_configs_mesh, os.path.join(PLOT_DIR, "3_curva_polare_Variare_mesh_n0012_i0.png"),
    #                   x_col="cl", y_col="cd", title="Curva Polare ($C_d$ vs $C_l$) - Confronto Mesh", x_label="$C_l$", y_label="$C_d$", x_min=-0.3, x_max=2.5, y_min=0.0, y_max=0.037)
    
    # # =====================================================================
    # # 4 & 5. Plot Confronto Simulazione Base fully turbolent vs Sperimentale
    # # =====================================================================
    # files_confronto_base = [
    #     "ALL_AOA_i=0.000_513x257/dati_numerici_n0012_513_257_i0.csv",
    #     "ALL_AOA_i=0.000_513x257/dati_sperimentali_n0012_Ladson_i0.csv" 
    # ]
    # plot_configs_confronto_base = [
    #     ("Simulazione 513x257", stile_numerico),
    #     ("Dati Sperimentali (Ladson)", stile_sperimentale)
    # ]
    # plot_coefficiente(files_confronto_base, plot_configs_confronto_base, os.path.join(PLOT_DIR, "4_confronto_portanza_n0012_i0_con_Ladson.png"),
    #                   x_col="alfa", y_col="cl", title="Confronto Portanza (Simulazione vs Dati Sperimentali)", x_label="Alfa [°]", y_label="$C_l$", highlight_last_point=0)
    # plot_coefficiente(files_confronto_base, plot_configs_confronto_base, os.path.join(PLOT_DIR, "5_confronto_polare_n0012_i0_con_Ladson.png"),
    #                   x_col="cl", y_col="cd", title="Confronto Polare ($C_d$ vs $C_l$) (Simulazione vs Dati Sperimentali)", x_label="$C_l$", y_label="$C_d$", y_min=0, y_max=0.05, highlight_last_point=0)


    # plot_configs_confronto_base_1 = [
    #     ("Simulazione 513x257", stile_numerico_1),
    #     ("Dati Sperimentali (Ladson)", stile_sperimentale_1)
    # ]
    # plot_coefficiente(files_confronto_base, plot_configs_confronto_base_1, os.path.join(PLOT_DIR, "5_1_confronto_polare_n0012_i0_con_Ladson.png"),
    #                 x_col="cl", y_col="cd", title="Confronto Polare ($C_d$ vs $C_l$) (Simulazione vs Dati Sperimentali)", x_label="$C_l$", y_label="$C_d$",y_min=-0.2, y_max=0.2, x_min=-0.20, x_max=0.20, highlight_last_point=0)
    
    
    
    # files_confronto_base_2 = [
    #     "ALL_AOA_i=0.000_513x257_y_plus=0.225\dati_numerici_n0012_513_257_i0.csv",
    #     "ALL_AOA_i=0.000_513x257/dati_sperimentali_n0012_Ladson_i0.csv" 
    # ]
    # plot_coefficiente(files_confronto_base_2, plot_configs_confronto_base, os.path.join(PLOT_DIR, "5_4_confronto_polare_n0012_i0_con_Ladson_Y_plus=0.225.png"),
    #             x_col="cl", y_col="cd", title="Curva Polare ($C_d$ vs $C_l$) Simulazione vs Dati Sperimentali - NACA 0012, Re=6E06, M=0.15", x_label="$C_l$", y_label="$C_d$", y_min=0.0, y_max=0.05, x_min=-0.30, label_fontsize=16, title_fontsize=15, legend_fontsize=16)

    # plot_coefficiente(files_confronto_base_2, plot_configs_confronto_base, os.path.join(PLOT_DIR, "4_2_confronto_portanza_n0012_i0_con_Ladson.png"),
    #                 x_col="alfa", y_col="cl", title="Curva Portanza - Simulazione vs Dati Sperimentali - NACA 0012, Re=6E06, M=0.15", x_label="Alfa [°]", y_label="$C_l$", label_fontsize=16, title_fontsize=15, legend_fontsize=16)

    # # =====================================================================
    # # 6 & 7. Plot Confronto Free Transition vs Ladson
    # # =====================================================================
    # files_confronto_ladson = [
    #     "ALL_AOA_i=0.000_513x257/dati_sperimentali_n0012_Ladson_i0.002_i0005.csv",
    #     "ALL_AOA_i=0.000_513x257/dati_numerici_n0012_513_257_i0.002.csv",          
    #     "ALL_AOA_i=0.000_513x257/dati_numerici_n0012_513_257_i0.005.csv"
    # ]
    # plot_configs_confronto_ladson = [
    #     ("Sperimentale (Ladson)", stile_sperimentale),
    #     ("Numerico i0.002", stile_numerico),
    #     ("Numerico i0.005", stile_numerico)
    # ]
    # plot_coefficiente(files_confronto_ladson, plot_configs_confronto_ladson, os.path.join(PLOT_DIR, "6_curva_portanza_confronto_i0.002_0.005_con_ladson.png"),
    #                   x_col="alfa", y_col="cl", title="Curva Portanza - Simulazione vs Dati Sperimentali - NACA 0012, Re=6E06, M=0.15 - Dati Ladson", x_label="Alfa [°]", y_label="$C_l$", label_fontsize=16, title_fontsize=13, legend_fontsize=16)
    # plot_coefficiente(files_confronto_ladson, plot_configs_confronto_ladson, os.path.join(PLOT_DIR, "7_curva_polare_i0.002_0.005_con_confronto_ladson.png"),
    #                   x_col="cl", y_col="cd", title="Curva Polare - Simulazione vs Dati Sperimentali - NACA 0012, Re=6E06, M=0.15 - Dati Ladson", x_label="$C_l$", y_label="$C_d$", label_fontsize=16, title_fontsize=13, legend_fontsize=16)

    # # =====================================================================
    # # 8 & 9. Plot Confronto Nuove Condizioni vs Abott
    # # =====================================================================
    # files_lift_abott = [
    #     "ALL_AOA_i=0.000_513x257/dati_sperimentali_n0012_Abott_i0002_i0005.csv",
    #     "ALL_AOA_i=0.000_513x257/dati_numerici_n0012_513_257_i0.002.csv",          
    #     "ALL_AOA_i=0.000_513x257/dati_numerici_n0012_513_257_i0.005.csv"
    # ]
    # plot_configs_lift_abott = [
    #     ("Sperimentale (Abott)", stile_sperimentale),
    #     ("Numerico i0.002", stile_numerico),
    #     ("Numerico i0.005", stile_numerico)
    # ]
    # plot_coefficiente(files_lift_abott, plot_configs_lift_abott, os.path.join(PLOT_DIR, "8_curva_portanza_confronto_i0.002_0.005_con_abott.png"),
    #                   x_col="alfa", y_col="cl", title="Curva Portanza - Simulazione vs Dati Sperimentali - NACA 0012, Re=6E06, M=0.15 - Dati Abott", x_label="Alfa [°]", y_label="$C_l$", label_fontsize=16, title_fontsize=13, legend_fontsize=16)
    
    # files_polar_abott = [
    #     "ALL_AOA_i=0.000_513x257/dati_sperimentali_POLARE_ABOTT_i0002_i0005.csv",
    #     "ALL_AOA_i=0.000_513x257/dati_numerici_n0012_513_257_i0.002.csv",          
    #     "ALL_AOA_i=0.000_513x257/dati_numerici_n0012_513_257_i0.005.csv"
    # ]
    # plot_configs_polar_abott = [
    #     ("Sperimentale (Abott Polare)", stile_sperimentale),
    #     ("Numerico i0.002", stile_numerico),
    #     ("Numerico i0.005", stile_numerico)
    # ]
    # plot_coefficiente(files_polar_abott, plot_configs_polar_abott, os.path.join(PLOT_DIR, "9_curva_polare_confronto_i0.002_0.005_con_abott.png"),
    #                   x_col="cl", y_col="cd", title="Curva Polare - Simulazione vs Dati Sperimentali - NACA 0012, Re=6E06, M=0.15 - Dati Abott", x_label="$C_l$", y_label="$C_d$", label_fontsize=16, title_fontsize=12, legend_fontsize=16)






    # =====================================================================
    #  PLOT COMBINATO: Curve di Portanza (Mesh vs Sperimentale)
    # =====================================================================
    print("\n--- Inizio Elaborazione per Grafico Portanza Combinato ---")

    # Definiamo la lista completa dei file per questo grafico
    files_combinati = [
        "ALL_AOA_i=0.000_129x64/dati_numerici_n0012_129_65_i0.csv",
        "ALL_AOA_i=0.000_257x129/dati_numerici_n0012_257_129_i0.000.csv",
        "ALL_AOA_i=0.000_513x257_y_plus=0.225\dati_numerici_n0012_513_257_i0.csv",
        "ALL_AOA_i=0.000_513x257/dati_sperimentali_n0012_Ladson_i0.csv" 
    ]
    # Definiamo la lista delle configurazioni (etichette e stili)
    plot_configs_combinati = [
        ("Mesh 129x64", stile_numerico),
        ("Mesh 257x129", stile_numerico),
        ("Mesh 513x257", stile_numerico),
        ("Dati Sperimentali (Ladson)", stile_sperimentale)
    ]

    # Chiamiamo la funzione di plot per la curva di portanza
    plot_coefficiente(
        files_combinati,
        plot_configs_combinati,
        os.path.join(PLOT_DIR, "COMBINATO_portanza_mesh_vs_sperimentale.png"),
        x_col="alfa", 
        y_col="cl",
        title="Curva di portanza al variare del mesh - NACA 0012, Re=6E06, M=0.15",
        x_label="Alfa [°]", 
        y_label="$C_l$",
        x_min=0.0, 
        x_max=20,
        label_fontsize=18, 
        title_fontsize=15, 
        legend_fontsize=16
    )

    # Chiamiamo la funzione di plot per la curva polare
    plot_coefficiente(
        files_combinati,
        plot_configs_combinati,
        os.path.join(PLOT_DIR, "COMBINATO_polare_mesh_vs_sperimentale.png"),
        x_col="cl", 
        y_col="cd", 
        title="Curva polare al variare del mesh - NACA 0012, Re=6E06, M=0.15",
        x_label="$C_l$", 
        y_label="$C_d$",
        y_min=0.0, 
        y_max=0.04,
        label_fontsize=18, 
        title_fontsize=15, 
        legend_fontsize=16
    )


    #### FREE TRANSTION I=0.003
    files_combinati_free_trans = [
        "ALL_AOA_i=0.000_129x64/dati_numerici_n0012_129_65_i0.csv",
        "ALL_AOA_i=0.000_257x129/dati_numerici_n0012_257_129_i0.000.csv",
        "ALL_AOA_i=0.000_513x257_y_plus=0.225\dati_numerici_n0012_513_257_i0.csv",
        "ALL_AOA_i=0.000_513x257/dati_sperimentali_n0012_Ladson_i0.csv" 
    ]
    # Definiamo la lista delle configurazioni (etichette e stili)
    plot_configs_combinati_free_trans = [
        ("Mesh 129x64", stile_numerico),
        ("Mesh 257x129", stile_numerico),
        ("Mesh 513x257", stile_numerico),
        ("Dati Sperimentali (Ladson)", stile_sperimentale)
    ]
    plot_coefficiente(
        files_combinati_free_trans,
        plot_configs_combinati_free_trans,
        os.path.join(PLOT_DIR, "COMBINATO_portanza_mesh_vs_sperimentale_free_transition.png"),
        x_col="alfa", 
        y_col="cl",
        title="Curva di portanza al variare del mesh - NACA 0012, Re=6E06, M=0.15",
        x_label="Alfa [°]", 
        y_label="$C_l$",
        x_min=0.0, 
        x_max=20,
        label_fontsize=18, 
        title_fontsize=15, 
        legend_fontsize=16
    )

    # Chiamiamo la funzione di plot per la curva polare
    plot_coefficiente(
        files_combinati_free_trans,
        plot_configs_combinati_free_trans,
        os.path.join(PLOT_DIR, "COMBINATO_polare_mesh_vs_sperimentale_free_transition.png"),
        x_col="cl",  
        y_col="cd", 
        title="Curva polare al variare del mesh - NACA 0012, Re=6E06, M=0.15",
        x_label="$C_l$",
        y_label="$C_d$", 
        y_min=0.0, 
        y_max=0.04,
        label_fontsize=18, 
        title_fontsize=15, 
        legend_fontsize=16
    )
    print("\n Tutti i plot sono stati generati con successo.")