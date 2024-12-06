import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from flask import Flask, request, render_template, jsonify, redirect, url_for

app = Flask(__name__)

# Define your threshold values
THRESHOLD_FLEX = 300  # Example threshold for flex sensors
THRESHOLD_PRESSURE = 400  # Example threshold for pressure sensor
SENSOR_COUNT = 6  # Number of sensors

@app.route('/')
def home():
    return render_template('index.html')  # Render the HTML form for file upload

@app.route('/predict', methods=['POST'])
def predict():
    # Check if the request contains a file
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']

    # Check if a file was actually uploaded
    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    # Read the CSV file
    try:
        df = pd.read_csv(file)
    except Exception as e:
        return jsonify({'error': str(e)})

    # Assuming the CSV has 6 columns for 5 flex sensors and 1 pressure sensor
    if df.shape[1] != SENSOR_COUNT:
        return jsonify({'error': f'Expected {SENSOR_COUNT} columns in the CSV, but got {df.shape[1]} columns'})

    # Compute the average of each sensor column
    sensor_data_avg = df.mean(axis=0).values  # Calculate average for each sensor across all rows

    # Extract the flex and pressure data
    flex_data = sensor_data_avg[:5]  # First 5 values are for flex sensors
    pressure_data = sensor_data_avg[5]  # 6th value is for the pressure sensor

    # Check how many sensors exceed their thresholds
    flex_above_threshold = sum([1 for val in flex_data if val > THRESHOLD_FLEX])
    pressure_above_threshold = 1 if pressure_data > THRESHOLD_PRESSURE else 0

    # Combine the results
    total_above_threshold = flex_above_threshold + pressure_above_threshold

    # Predict autism based on the number of sensors exceeding the threshold
    if total_above_threshold >= 2:  # Example: If 4 or more sensors exceed their threshold, predict autism
        prediction = "Autistic"
    else:
        prediction = "Non-autistic"

    # Generate a graph to display on the next page
    fig, ax = plt.subplots()
    labels = [f'Flex Sensor {i+1}' for i in range(5)] + ['Pressure Sensor']
    values = list(flex_data) + [pressure_data]

    ax.bar(labels, values, color=['blue']*5 + ['green'])
    ax.set_title('Average Sensor Data')
    ax.set_ylabel('Sensor Reading')

    # Save the figure to a BytesIO object and encode it as a base64 string
    img = io.BytesIO()
    fig.savefig(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode('utf8')

    return render_template('result.html', prediction=prediction, graph_url=graph_url, sensor_data=sensor_data_avg)

@app.route('/result', methods=['GET'])
def result():
    return render_template('result.html')  # A page to display the results and graph

if __name__ == '__main__':
    app.run(debug=True)
