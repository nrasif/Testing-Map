from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')
def render_the_map():
    return render_template('testing_map.html')

@app.route('/figure1')
def figWell1F():
    return render_template(r'Well_Log_Plotly/figWell1F.html')

@app.route('/figure2')
def figWell2F():
    return render_template(r'Well_Log_Plotly/figWell2F.html')

if __name__ == '__main__':
    app.run(debug=True)