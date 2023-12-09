from flask import Flask, render_template, request
import pandas as pd
from surprise import Reader, Dataset, KNNBasic
from surprise.model_selection import train_test_split

app = Flask(__name__)

# Agregar la lógica para cargar datos y preprocesar
rating_df = pd.read_csv(r"D:\Exe\OneDrive - alumnos.frm.utn.edu.ar\Cursos\Data Science\TP4\Dataset\rating_complete.csv")
rating_df['animes_vistos_por_usuario'] = rating_df.groupby('user_id')['anime_id'].transform('count')
rating_df = rating_df.sort_values(by='animes_vistos_por_usuario', ascending=False)
df_reducido = rating_df.head(300000)
df_reducido = df_reducido.sample(frac=1, random_state=42)
df = df_reducido.copy()

reader = Reader(rating_scale=(1, 10))
data = Dataset.load_from_df(df[['user_id', 'anime_id', 'rating']], reader)
train, test = train_test_split(data, random_state=42, test_size=0.2)

# Configuración de opciones para el algoritmo KNN
sim_options = {'name': 'cosine', 'user_based': True}

# Inicialización del modelo KNN con las opciones especificadas
model = KNNBasic(sim_options=sim_options)
model.sim_options['shrinkage'] = 10  # Ajustar el parámetro de contracción (shrinkage)

# Entrenamiento del modelo
model.fit(train)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recomendar', methods=['POST'])
def recomendar():
    if request.method == 'POST':
        # Obtener user_id del formulario
        user_id = int(request.form['user_id'])

        # Obtener recomendaciones para el usuario
        recommendations = get_recommendations(user_id)

        if not recommendations:
            return render_template('resultados.html', user_id=user_id, message="No hay recomendaciones disponibles.")

        return render_template('resultados.html', user_id=user_id, recommendations=recommendations)

def get_recommendations(user_id):
    # Cargar el conjunto de datos completo
    full_data = Dataset.load_from_df(df[['user_id', 'anime_id', 'rating']], reader)

    # Obtener el conjunto de entrenamiento completo
    full_trainset = full_data.build_full_trainset()

    # Obtener los ítems que el usuario aún no ha visto
    unseen_items = set(full_trainset.all_items()) - set(train.ur[train.to_inner_uid(user_id)])

    if not unseen_items:
        print("El usuario ha visto todos los animes disponibles.")
        return []

    # Hacer predicciones solo para los ítems no vistos
    user_predictions = [model.predict(user_id, iid) for iid in unseen_items]

    if not user_predictions:
        print("No se generaron predicciones para el usuario.")
        return []

    # Ordenar las predicciones por estimación en orden descendente
    user_predictions.sort(key=lambda x: x.est, reverse=True)

    # Imprimir las recomendaciones para depuración
    print("Recomendaciones para el usuario", user_id)
    for pred in user_predictions:
        print(f"Anime {full_trainset.to_raw_iid(pred.iid)} con estimación {pred.est}")
    print("\n")  # Nueva línea para separar

    # Obtener las recomendaciones
    recommendations = [
        (full_trainset.to_raw_iid(pred.iid), pred.est)
        for pred in user_predictions
    ]

    return recommendations[:10]  # Devolver las primeras 10 recomendaciones



if __name__ == '__main__':
    app.run(debug=True)

