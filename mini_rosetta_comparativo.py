
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Mini-ROSETTA Comparativo PTFs", layout="centered")

st.title("🌱 Mini-ROSETTA: Comparación de PTFs para CC y PMP")

st.write("""
Esta versión calcula:
- **Ks** con Rawls et al. (1982)
- **Curva de retención de humedad** (van Genuchten)
- **CC y PMP** usando **Saxton & Rawls (2006)** y **Rawls et al. (1982)**
- Grafica ambos resultados para comparación.
""")

# Entradas de usuario
sand = st.number_input("Arena (%)", min_value=0.0, max_value=100.0, value=65.0)
silt = st.number_input("Limo (%)", min_value=0.0, max_value=100.0, value=25.0)
clay = st.number_input("Arcilla (%)", min_value=0.0, max_value=100.0, value=10.0)
bd = st.number_input("Densidad aparente (g/cm³)", min_value=0.5, max_value=2.2, value=1.45)
om = st.number_input("Materia orgánica (%)", min_value=0.0, max_value=10.0, value=1.8)

if st.button("🔍 Calcular PTFs"):

    # Ks Rawls et al. (1982)
    a, b, c, d, e = -0.884, 0.0153, -0.0003, -0.197, 0.112
    log_Ks = a + b*sand + c*clay + d*bd + e*om
    Ks = 10 ** log_Ks

    # van Genuchten (Carsel & Parrish)
    theta_s = 1 - bd/2.65
    theta_r = 0.045
    alpha = 0.075
    n = 1.89

    # Saxton & Rawls (2006)
    sand_f = sand / 100
    clay_f = clay / 100
    om_f = om / 100

    CC_Saxton = (-0.251 + 0.195 * clay_f + 0.011 * om_f +
                 0.006 * clay_f * om_f - 0.027 * sand_f * om_f +
                 0.452 * sand_f * clay_f + 0.299)

    PMP_Saxton = (-0.024 + 0.487 * clay_f + 0.006 * om_f +
                  0.005 * clay_f * om_f - 0.013 * sand_f * om_f +
                  0.068 * sand_f * clay_f + 0.031)

    AD_Saxton = CC_Saxton - PMP_Saxton

    # Rawls et al. (1982)
    CC_Rawls = (-0.251 + 0.195 * clay + 0.011 * om) / 100
    PMP_Rawls = (-0.024 + 0.004 * clay + 0.004 * om) / 100
    AD_Rawls = CC_Rawls - PMP_Rawls

    # Resultados
    st.subheader("✅ Resultados estimados")
    st.write(f"**Ks:** {Ks:.2f} cm/h")
    st.write(f"**θs:** {theta_s:.3f}")
    st.write(f"**θr:** {theta_r:.3f}")
    st.write(f"**α:** {alpha:.3f} 1/cm")
    st.write(f"**n:** {n:.2f}")
    st.write(f"**CC Saxton:** {CC_Saxton:.3f} | PMP Saxton: {PMP_Saxton:.3f} | AD Saxton: {AD_Saxton:.3f}")
    st.write(f"**CC Rawls:** {CC_Rawls:.3f} | PMP Rawls: {PMP_Rawls:.3f} | AD Rawls: {AD_Rawls:.3f}")

    # Curva de retención
    h = np.logspace(-1, 3.2, 100)
    psi = h / 102.04  # Convertir cm a kPa
    Se = 1 / (1 + (alpha * h)**n)**(1 - 1/n)
    theta = theta_r + Se * (theta_s - theta_r)

    fig, ax = plt.subplots()
    ax.plot(psi, theta, label="Curva de retención")

    ax.axhline(CC_Saxton, color='green', linestyle='--', label="CC Saxton")
    ax.axhline(PMP_Saxton, color='red', linestyle='--', label="PMP Saxton")
    ax.axhline(CC_Rawls, color='blue', linestyle=':', label="CC Rawls")
    ax.axhline(PMP_Rawls, color='purple', linestyle=':', label="PMP Rawls")

    ax.set_xscale('log')
    ax.set_xlabel('Suction (kPa)')
    ax.set_ylabel('Contenido volumétrico de agua (cm³/cm³)')
    ax.set_title('Curva de retención + CC/PMP Saxton vs Rawls')
    ax.legend()
    ax.invert_xaxis()

    st.pyplot(fig)

    df = pd.DataFrame({
        'h (cm)': h,
        'Suction (kPa)': psi,
        'θ (cm³/cm³)': theta
    })
    st.download_button("📥 Descargar curva (CSV)", df.to_csv(index=False), "curva_retencion.csv")

st.caption("Demo comparativa Saxton vs Rawls | Desarrollado con Streamlit")
