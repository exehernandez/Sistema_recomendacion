from flask import Flask, render_template, request
import pandas as pd
import ast

app = Flask(__name__)

# Aquí deberías definir o cargar tus DataFrames recomendaciones y base_de_datos
base_de_datos = pd.read_csv(r"D:\Exe\OneDrive - alumnos.frm.utn.edu.ar\Cursos\Data Science\TP4\Entrega\base_de_datos.csv")
recomendaciones = pd.read_csv(r"D:\Exe\OneDrive - alumnos.frm.utn.edu.ar\Cursos\Data Science\TP4\Entrega\recomedaciones.csv")
mov_df = pd.read_csv(r"D:\Exe\OneDrive - alumnos.frm.utn.edu.ar\Cursos\Data Science\TP4\Entrega\Cold Start\mov_df.csv")
ona_df = pd.read_csv(r"D:\Exe\OneDrive - alumnos.frm.utn.edu.ar\Cursos\Data Science\TP4\Entrega\Cold Start\ona_df.csv")
ova_df = pd.read_csv(r"D:\Exe\OneDrive - alumnos.frm.utn.edu.ar\Cursos\Data Science\TP4\Entrega\Cold Start\ova_df.csv")
special_df = pd.read_csv(r"D:\Exe\OneDrive - alumnos.frm.utn.edu.ar\Cursos\Data Science\TP4\Entrega\Cold Start\special_df.csv")
tv_df = pd.read_csv(r"D:\Exe\OneDrive - alumnos.frm.utn.edu.ar\Cursos\Data Science\TP4\Entrega\Cold Start\tv_df.csv")


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recomendaciones', methods=['POST'])
def obtener_recomendaciones():
    user_id = request.form['user_id']

    # Verificar si el user_id está en la base de datos
    if int(user_id) in recomendaciones['user_id'].values:
        # Obtener las recomendaciones para el user_id ingresado
        recomendaciones_usuario = recomendaciones[recomendaciones['user_id'] == int(user_id)]['recomms'].values[0]
        recomendaciones_usuario = ast.literal_eval(recomendaciones_usuario)

        # Filtrar base_de_datos según las recomendaciones para el user_id ingresado
        df_resultado = base_de_datos[base_de_datos['anime_id'].isin(recomendaciones_usuario)]
        # Ordenar df_resultado por la columna anime_id según el orden de recomendaciones
        df_resultado = df_resultado.sort_values(by='anime_id', key=lambda x: x.map({anime_id: i for i, anime_id in enumerate(recomendaciones_usuario)})).reset_index(drop=True).head(20)
        return render_template('recomendaciones.html', user_id=user_id, df_resultado=df_resultado.to_html(index=False))
    else:
        # Si el user_id no está en la base de datos, mostrar mensaje de COLD START
        return render_template('cold_start.html',
                               mov_df=mov_df.to_html(index=False, classes='table'),
                               ona_df=ona_df.to_html(index=False, classes='table'),
                               ova_df=ova_df.to_html(index=False, classes='table'),
                               special_df=special_df.to_html(index=False, classes='table'),
                               tv_df=tv_df.to_html(index=False, classes='table'))

if __name__ == '__main__':
    app.run(debug=True)
