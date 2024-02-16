from flask import Flask, request, jsonify
import click
from flask_swagger_ui import get_swaggerui_blueprint
from my_cli.helper_functions import Helper

app = Flask(__name__)
obj = Helper()

SWAGGER_URL = "/api/docs"
API_URL = "/static/swagger.json"
SWAGGER_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        "app_name" : "Access and retrieve data"
    }
)

app.register_blueprint(SWAGGER_BLUEPRINT, url_prefix = SWAGGER_URL)

def initialize_project_cli(project_id):
    _, result = obj.initialize_project(project_id)
    return result

@app.route("/initialize/<project_id>")
def initialize_project_api(project_id):
    default_message = {"API call" : "Success", "Data stored in database" : "Success", "Query Parameters" : "[list=True]"}
    list_elements = request.args.get("list")

    status, result = obj.initialize_project(project_id)

    if status:
        if list_elements == "True":
            return jsonify(result), 200
        return jsonify(default_message), 200
    else:
        return jsonify(result), 404

def query_string_cli(search_string):
    _, result = obj.query_string(search_string)
    return result

@app.route("/query_string")
def query_string_api():
    search_string = request.args.get("search_string")
    default_message = "Please use the query parameter \"search_string\" to list the iElements that contains the query string."
    if search_string:
        status, result = obj.query_string(search_string)
        if status:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
    return jsonify(default_message), 400

def download_all_files_cli():
    _, result = obj.download_all_files()
    return result

@app.route("/download_all")
def download_all_files_api():
    status, result = obj.download_all_files()
    if status:
        return jsonify(result), 200
    return jsonify(result), 404

@app.route("/download_all/status")
def download_all_status_api():
    status, result = obj.download_all_status()
    if status:
        return jsonify(result), 200
    return jsonify(result), 404

@click.command()
@click.option('-initialize', help="Initialize with the project ID")
@click.option('-query', help="Provide the query string to search in the sqlite database")
@click.option('-download-all', is_flag=True, help="Download all data")
def all_functions(initialize, query, download_all):
    if initialize:
        print(initialize_project_cli(initialize))
    if query:
        print(query_string_cli(query))
    if download_all:
        print(download_all_files_cli())
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000, debug=True)