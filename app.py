import pandas as pd
import scipy.stats
import streamlit as st
import time

# Inicializar session_state
if 'experiment_no' not in st.session_state:
    st.session_state['experiment_no'] = 0

if 'df_experiment_results' not in st.session_state:
    st.session_state['df_experiment_results'] = pd.DataFrame(columns=['no', 'iteraciones', 'media'])

st.set_page_config(page_title="Lanzar una moneda", layout="wide")

st.header('Lanzar una moneda')

# Chart inicial con valor 0.5 (simetría)
chart = st.line_chart([0.5])

def toss_coin(n, sleep_time=0.01):
    """Genera n lanzamientos bernoulli, actualiza chart y muestra progreso."""
    trial_outcomes = scipy.stats.bernoulli.rvs(p=0.5, size=n)

    outcome_1_count = 0
    progress = st.progress(0)

    for i, r in enumerate(trial_outcomes, start=1):
        if r == 1:
            outcome_1_count += 1
        mean = outcome_1_count / i
        chart.add_rows([mean])
        # Actualizar barra de progreso (valor entre 0 y 1)
        progress.progress(i / n)
        # Pequeña pausa para animación (ajustable)
        if sleep_time and sleep_time > 0:
            time.sleep(sleep_time)

    progress.empty()
    return mean

# Controles UI
col1, col2 = st.columns([3,1])
with col1:
    number_of_trials = st.slider('¿Número de intentos?', 1, 1000, 10)
with col2:
    start_button = st.button('Ejecutar')
    clear_button = st.button('Limpiar historial')

# Acciones
if start_button:
    st.write(f'Experimento con {number_of_trials} intentos en curso.')
    st.session_state['experiment_no'] += 1
    # Llamar a toss_coin (ajusta sleep_time si quieres más velocidad)
    mean = toss_coin(number_of_trials, sleep_time=0.01)
    # Guardar resultado en el DataFrame en session_state
    st.session_state['df_experiment_results'] = pd.concat([
        st.session_state['df_experiment_results'],
        pd.DataFrame([[st.session_state['experiment_no'],
                       number_of_trials,
                       mean]], columns=['no', 'iteraciones', 'media'])
    ], ignore_index=True)
    st.session_state['df_experiment_results'] = st.session_state['df_experiment_results'].reset_index(drop=True)

if clear_button:
    st.session_state['experiment_no'] = 0
    st.session_state['df_experiment_results'] = pd.DataFrame(columns=['no', 'iteraciones', 'media'])
    chart.line_chart([0.5])  # reset chart (alternativa simple)
    st.experimental_rerun()

# Mostrar tabla de resultados
st.subheader('Historial de experimentos')
st.write(st.session_state['df_experiment_results'])
