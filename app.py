from flask import Flask, render_template, request, redirect, url_for
import os
#from io import StringIO
from io import BytesIO
import pandas as pd
from eda import perform_eda,clean_data
from flask import send_file
import pandas as pd
import seaborn as sns
import matplotlib
matplotlib.use('Agg')  # Non-GUI backend
import matplotlib.pyplot as plt



app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect('/')
    file = request.files['file']
    if file.filename == '':
        return redirect('/')
    if file:

        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        return redirect(url_for('visualization', filename=file.filename))
    
@app.route('/visualization/<filename>',methods=['GET','POST'])
def visualization(filename):
       filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
       summary = perform_eda(filepath)
       
       if request.method=='POST':
           filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

           missing_strategy = request.form.get('missing_values_strategy')
           remove_duplicates = 'remove_duplicates' in request.form
           drop_columns = request.form.getlist('drop_columns')
           
           
           cleaned_path=clean_data(filepath,missing_strategy,remove_duplicates,drop_columns)
           df=pd.read_csv(cleaned_path)
           summary=perform_eda(cleaned_path)
     
           hist_columns = request.form.getlist('hist_columns')
           count_columns = request.form.getlist('count_columns')
           hue_column = request.form.get('hue_column')
           heatmap_color = request.form['heatmap_color']
           hist_color = request.form['hist_color']
           count_color = request.form['count_color']
     
           
      
           plot_filenames = []

              # Heatmap
           numeric_df = df.select_dtypes(include=['number'])
           plt.figure(figsize=(10,6))
           sns.heatmap(numeric_df.corr(), cmap=heatmap_color, annot=True)
           heatmap_filename = 'static/heatmap.png'
           plt.savefig(heatmap_filename)
           plt.close()
           plot_filenames.append('heatmap.png')

              # Histograms
           for col in hist_columns:
               plt.figure(figsize=(8,5))
               sns.histplot(df[col].dropna(), kde=True, color=hist_color)
               plt.title(f'Histogram of {col}')
               fname = f'static/{col}_hist.png'
               plt.savefig(fname)
               plt.close()
               plot_filenames.append(f'{col}_hist.png')
      
        # Countplots
           for col in count_columns:
               plt.figure(figsize=(8,5))
               sns.countplot(x=df[col], hue=df[hue_column] if hue_column else None, color=count_color)
               plt.title(f'Countplot of {col}')
               plt.xticks(rotation=45)
               fname = f'static/{col}_countplot.png'
               plt.savefig(fname)
               plt.close()
               plot_filenames.append(f'{col}_countplot.png')
      
              # Render the same template, passing plots!
           return render_template(
               'eda.html',
               filename=filename,
               summary=summary,
               cleaned_path=cleaned_path,
               show=True,
               check=False,
               plots=plot_filenames)
       
       
       df=pd.read_csv(filepath)
       plot_filenames = []
       return render_template(
               'eda.html',
               filename=filename,
               summary=summary,
               show=False,
               check=True,
               all_columns=df.columns.tolist(),
               numeric_cols=df.select_dtypes(include='number').columns,
               categorical_cols=df.select_dtypes(include='object').columns,
               plots=plot_filenames)
       
     
@app.route('/download/<cleaned_path>')
def download_report(cleaned_path):
    #filepath = os.path.join(app.config['UPLOAD_FOLDER'],cleaned_path)
    df = pd.read_csv(cleaned_path)
    
    #cleaned_filepath = os.path.join(app.config['UPLOAD_FOLDER'],cleaned_path)

    # Save to memory buffer instead of disk
    buffer = BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    
    # Return as downloadable file
    return send_file(buffer, as_attachment=True,
                     download_name=cleaned_path,
                     mimetype='text/csv')

if __name__ == '__main__':
    app.run(debug=True)
