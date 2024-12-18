from flask import Flask, request, render_template, send_file
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import io
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/scndpage')
def scndpage():
    return render_template('scndpage.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    plot_type = request.form['plot_type']

    x_column = request.form.get('x_column')
    y_column = request.form.get('y_column')
    x_axis = request.form.get('x_axis')
    y_axis = request.form.get('y_axis')
    pie_columns = request.form.get('pie_columns')
    heatmap_columns = request.form.get('heatmap_columns')

    if file and file.filename.endswith('.csv'):
        df = pd.read_csv(file)
        img = io.BytesIO()

        if plot_type == 'scatter' and x_column and y_column:
            sns.scatterplot(x=df[x_column], y=df[y_column], palette="magma", color=plt.cm.magma(0.5), s=100)

        elif plot_type == 'bar' and x_axis and y_axis:
            df_sorted = df[[x_axis, y_axis]].sort_values(by=x_axis)
            medval = df_sorted[y_axis].mean()
            colors = ["#9b65b6" if value < medval else "#391a48" for value in df_sorted[y_axis]]
            fig, ax = plt.subplots(figsize=(10,8))
            bars = ax.barh(df_sorted[x_axis], df_sorted[y_axis], color=colors, height=0.7)
            ax.spines[["right", "top", "bottom"]].set_visible(True)
            ax.xaxis.set_visible(True)
            ax.bar_label(bars, padding=3, color="white", fontsize=12, label_type="edge", fmt="%.1f", fontweight="bold")


        elif plot_type == 'pie' and pie_columns:
            columns = pie_columns.split(',')
            columns = [col.strip() for col in columns]
            df[columns].sum().plot.pie(autopct='%1.1f%%')

        elif plot_type == 'heatmap' and heatmap_columns:
            columns = heatmap_columns.split(',')
            columns = [col.strip() for col in columns]
            df[columns] = df[columns].apply(pd.to_numeric, errors='coerce')
            sns.heatmap(df[columns].corr(), cmap="RdBu", vmin=-1, vmax=1, square=True, annot=True, annot_kws={"fontsize":11, "fontweight":"bold"})

        else:
            return 'Invalid plot type selected or missing inputs.'

        plt.savefig(img, format='png')
        img.seek(0)
        plt.close()
        return send_file(img, mimetype='image/png')

    return 'Please upload a valid CSV file and select a plot type.'

if __name__ == '__main__':
    app.run(debug=True)
