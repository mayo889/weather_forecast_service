from swagger_ui import api_doc
from flask import Flask, render_template, send_file, request, jsonify
from flask_prometheus_metrics import register_metrics
from prometheus_client import make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple

from tools import (get_today_date, read_data_from_col, read_html, read_json,
                    get_history_weather, NUM_TO_MONTH)

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

api_doc(app, config_path='./swagger-config.yaml', url_prefix='/api/doc', title='API doc')

PATH_TO_MODEL = "static/models/serialized_model.json"


@app.route("/")
def main_page():
    return render_template(
        'index.html',
        today_date=get_today_date(),
        preds=read_json('preds'),
        graph_preds=read_html('graph'),
        graph_metrics=read_html('metrics')
    )


@app.route("/history", methods =["GET", "POST"])
def history_page():
    if request.method == "POST":
        month = int(request.form.get("month"))
        year = int(request.form.get("year"))
    else:
        month, year = 1, 2023
    history_data = get_history_weather(month, year)

    return render_template(
        'history.html',
        selected_month=month,
        name_of_month=NUM_TO_MONTH[month],
        selected_year=year,
        history_data=history_data
    )


@app.route("/contacts")
def contacts_page():
    return render_template(
        'contacts.html'
    )


@app.route('/api/predictions')
def predictions():
    x = read_json('preds')
    response = {i: elem for i, elem in enumerate(x, 1)}
    return jsonify(response), 200


@app.route('/api/predictions/<day>')
def predictions_on_day(day):
    day = int(day) - 1
    preds = read_json('preds')

    if day >= len(preds) or day < 0:
        return f"ERROR: Predictions are available for {len(preds)} days, but you requested {day+1}", 400
    return jsonify(preds[day]), 200


@app.route('/api/metrics')
def dasboards():
    data = read_data_from_col('metrics')[-1]
    return jsonify(data), 200


@app.route("/test")
def test():
    return "test"


@app.route('/api/model')
def download_model():
    return send_file(PATH_TO_MODEL, as_attachment=True)


if __name__ == '__main__':
    register_metrics(app, app_version="v0.1.2", app_config="staging")

    # Plug metrics WSGI app to your main app with dispatcher
    dispatcher = DispatcherMiddleware(app.wsgi_app, {"/metrics": make_wsgi_app()})

    run_simple(hostname="server", port=8000, application=dispatcher)

    # app.run(host='server', port=8000, debug=True)
