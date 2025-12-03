import pandas as pd
import scipy.stats
import streamlit as st
import time

# Configuración de la página
st.set_page_config(page_title="Lanzar una moneda", layout="wide")

# Inicializar session_state
if 'experiment_no' not in st.session_state:
    st.session_state['experiment_no'] = 0

# DataFrame con resultados (no perder entre runs)
if 'df_experiment_results' not in st.session_state:
    st.session_state['df_experiment_results'] = pd.DataFrame(columns=['no', 'iteraciones', 'media'])

# Lista de medias para la gráfica (serie con nombre 'media')
if 'means' not in st.session_state:
    st.session_state['means'] = [0.5]  # valor inicial

st.header('Lanzar una moneda')

# Crear chart con DataFrame explícito y columna 'media'
chart_df = pd.DataFrame(st.session_state['means'], columns=['media'])
chart = st.line_chart(chart_df)

def toss_coin(n, sleep_time=0.01):
    """Generar n lanzamientos y actualizar chart correctamente."""
    trial_outcomes = scipy.stats.bernoulli.rvs(p=0.5, size=n)

    outcome_1_count = 0

    for i, r in enumerate(trial_outcomes, start=1):
        if r == 1:
            outcome_1_count += 1
        mean = outcome_1_count / i

        # Guardar en session_state['means'] y agregar fila al chart como DataFrame
        st.session_state['means'].append(mean)
        chart.add_rows(pd.DataFrame([mean], columns=['media']))

        # Barra de progreso
        progress = None
        # Para no recrear el widget cada iteración, podríamos crear uno antes del loop.
        # Aquí usamos st.session_state para mantenerlo simple:
        if 'progress' not in st.session_state:
            st.session_state['progress'] = st.progress(0)
        st.session_state['progress'].progress(i / n)

        if sleep_time and sleep_time > 0:
            time.sleep(sleep_time)

    # limpiar progreso
    if 'progress' in st.session_state:
        st.session_state['progress'].empty()
        del st.session_state['progress']

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
    st.write(f'Ejecutando experimento con {number_of_trials} intentos...')
    st.session_state['experiment_no'] += 1
    # Llamada a la función principal (ajusta sleep_time a 0 para producción)
    mean = toss_coin(number_of_trials, sleep_time=0.005)

    # Guardar resultado en el DataFrame de sesión
    new_row = pd.DataFrame([[st.session_state['experiment_no'], number_of_trials, mean]],
                           columns=['no', 'iteraciones', 'media'])
    st.session_state['df_experiment_results'] = pd.concat(
        [st.session_state['df_experiment_results'], new_row], ignore_index=True)

if clear_button:
    st.session_state['experiment_no'] = 0
    st.session_state['df_experiment_results'] = pd.DataFrame(columns=['no', 'iteraciones', 'media'])
    st.session_state['means'] = [0.5]
    # Reiniciar la página para reconstruir el chart limpio
    st.experimental_rerun()

# Mostrar tabla de resultados
st.subheader('Historial de experimentos')
st.dataframe(st.session_state['df_experiment_results'])
