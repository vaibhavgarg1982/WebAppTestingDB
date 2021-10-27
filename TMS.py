from flask import (
    Flask,
    render_template,
    request,
    url_for,
    redirect,
    Response,
    send_from_directory,
    abort,
)
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    login_required,
    current_user,
    UserMixin,
)

from werkzeug.security import generate_password_hash, check_password_hash

import os
import json

import sqlite3
import datetime


app = Flask(__name__)
app.secret_key = "d9b98d29c818ee2e82b3b608c0d72257"

login_manager = LoginManager()
login_manager.init_app(app)


class User(UserMixin):
    pass


@login_manager.user_loader
def user_loader(email):
    # get the user from the database
    conn = sqlite3.connect("testing.db")
    c = conn.cursor()
    c.execute(
        "SELECT * FROM users WHERE username=?", (email,),
    )
    user = c.fetchone()
    conn.close()
    if user:
        user = User()
        user.id = email
        return user
    return None



@login_manager.request_loader
def request_loader(request):
    email = request.form.get("email")
    conn = sqlite3.connect("testing.db")
    c = conn.cursor()
    c.execute(
        "SELECT * FROM users WHERE username=?", (email,),
    )
    user = c.fetchone()
    conn.close()
    if user:
        user = User()
        user.id = email
        return user
    return None


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    # get users from database, user table (username, hash))
    # username is the same as email    
    email = request.form["email"]
    password = request.form["password"]
    conn = sqlite3.connect("testing.db")
    c = conn.cursor()
    c.execute(
        "SELECT * FROM users WHERE username=?", (email,),
    )
    user = c.fetchone()
    conn.close()
    if user:
        if check_password_hash(user[1], password):
            user = User()
            user.id = email
            login_user(user)
            return render_template("about.html")  # redirect(url_for("projects"))

    return abort(401)


@app.route("/undercon")
@login_required
def undercon():
    return render_template(
        "undercon.html",
        msg="You should not see this page. Select an option from the left menu bar",
    )  # , current_user=current_user.id
    # )  #'Logged in as: ' + current_user.id


@app.route("/about")
@login_required
def about():
    return render_template("about.html")  # , current_user=current_user.id
    # )  #'Logged in as: ' + current_user.id


@app.route("/Projects", methods=["GET", "POST"])
@login_required
def projects():
    conn = sqlite3.connect("testing.db")
    c = conn.cursor()

    if request.method == "POST":
        name = request.form["ProjectName"]
        description = request.form["ProjectDescription"]
        if len(name) > 0 and len(description) > 0:
            # get list of all project names
            proj_names = [row[0] for row in c.execute("SELECT name FROM Mst_projects")]
            # print(proj_names)
            if name not in proj_names:
                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                c.execute(
                    "INSERT INTO Mst_projects (name, description, dateC, userName) VALUES(:name, :description, :dateC, :userName)",
                    {
                        "name": name,
                        "description": description,
                        "dateC": now,
                        "userName": current_user.id,
                    },
                )
                conn.commit()
            else:
                conn.close()
                return render_template(
                    "undercon.html",
                    msg="Project Name already exists, press back and try again",
                )
                # return "Project already exists, press back to return to the projects page and retry"
        else:
            conn.close()
            return "Project name and description cannot be empty"
        pass

    query = "SELECT * FROM Mst_projects"
    projects = [row for row in c.execute(query)]
    # projects = c.fetchall()
    conn.close()
    return render_template("projects.html", projects=projects)


@app.route("/Testcases", methods=["GET", "POST"])
@login_required
def testcases():
    conn = sqlite3.connect("testing.db")
    c = conn.cursor()

    if request.method == "POST":
        name = request.form["TestcaseName"]
        test_category = request.form["TestcaseCategory"]
        description = request.form["TestcaseDescription"]
        steps = request.form["TestcaseSteps"]
        expected_result = request.form["TestcaseExpectedResult"]
        automated = request.form["TestcaseAutomated"]
        if (
            len(name) > 0
            and len(test_category) > 0
            and len(description) > 0
            and len(steps) > 0
            and len(expected_result) > 0
            and len(automated) > 0
        ):
            # get list of all testcase names
            testcase_names = [
                row[0] for row in c.execute("SELECT name FROM Mst_testcases")
            ]
            # print(testcase_names)
            if name not in testcase_names:
                c.execute(
                    "INSERT INTO Mst_testcases (name, test_category, description, steps, expected_result, automated, dateC, userName) VALUES(:name, :test_category, :description, :steps, :expected_result, :automated, :dateC, :userName)",
                    {
                        "name": name,
                        "test_category": test_category,
                        "description": description,
                        "steps": steps,
                        "expected_result": expected_result,
                        "automated": automated,
                        "dateC": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "userName": current_user.id,
                    },
                )
                conn.commit()
            else:
                conn.close()
                return render_template(
                    "undercon.html",
                    msg="Testcase Name already exists, press back and try again",
                )
                # return "Testcase already exists, press back to return to the testcases page and retry"
        else:
            conn.close()
            return render_template(
                "undercon.html",
                msg="Testcase name, test category, description, steps, expected result or automated cannot be empty",
            )
            # return "Testcase name, test category, description, steps, expected result or automated cannot be empty"
        pass

    query = "SELECT * FROM Mst_testcases"
    testcases = [row for row in c.execute(query)]
    # testcases = c.fetchall()
    conn.close()
    return render_template("testcases.html", testcases=testcases)


@app.route("/viewbyproject", methods=["GET", "POST"])
@login_required
def viewbyproject():
    conn = sqlite3.connect("testing.db")
    c = conn.cursor()
    # get all project ids and project names from the MstProjects table
    query = "SELECT project_id, name FROM Mst_projects"
    projects = [row for row in c.execute(query)]

    if request.method == "POST":
        project_id = request.form["projects"]
        query = (
            "SELECT * FROM Mst_testcases INNER JOIN Mapping ON Mst_testcases.testcase_id = Mapping.testcase_id INNER JOIN Mst_projects ON Mst_projects.project_id = Mapping.project_id WHERE Mst_projects.project_id = "
            + project_id
        )
        testcases = [row for row in c.execute(query)]
        # testcases = c.fetchall()
        # select project name from the MstProjects table with the project_id
        query = "SELECT name FROM Mst_projects WHERE project_id = " + project_id
        project_name = [row for row in c.execute(query)]
        conn.close()
        return render_template(
            "viewbyproject.html",
            testcases=testcases,
            projects=projects,
            sel_project=project_name[0][0],
        )
    conn.close()
    return render_template("viewbyproject.html", projects=projects)


@app.route("/maptc_projects", methods=["GET", "POST"])
@login_required
def map_tc_to_projects():
    conn = sqlite3.connect("testing.db")
    c = conn.cursor()

    # get all project ids and project names from the MstProjects table
    query = "SELECT project_id, name FROM Mst_projects"
    projects = [row for row in c.execute(query)]
    query = "SELECT * FROM Mst_testcases"
    testcases = [row for row in c.execute(query)]

    if request.method == "POST":
        project_id = request.form["projects"]
        test_ids = request.form.getlist("test_ids")
        # insert project_id and each testcase_id into the Mapping table
        for test_id in test_ids:
            c.execute(
                "INSERT OR IGNORE INTO Mapping (project_id, testcase_id, dateC, userName) VALUES(:project_id, :test_id, :dateC, :userName)",
                {
                    "project_id": project_id,
                    "test_id": test_id,
                    "dateC": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "userName": current_user.id,
                },
            )
        conn.commit()
        conn.close()
        return render_template(
            "maptc_projects.html", testcases=testcases, projects=projects
        )

    conn.close()
    return render_template(
        "maptc_projects.html", projects=projects, testcases=testcases
    )


@app.route("/testresults", methods=["GET", "POST"])
@login_required
def testresults():
    conn = sqlite3.connect("testing.db")
    c = conn.cursor()
    # get all project ids and project names from the MstProjects table
    query = "SELECT project_id, name FROM Mst_projects"
    projects = [row for row in c.execute(query)]

    if request.method == "POST":
        if request.form["addsrc"] == "Add Test Results":
            d = dict(request.form)
            d_filtered = {
                k: v
                for k, v in d.items()
                if "Description" in k
                or "ConfigInfo" in k
                or "Tester" in k
                or "Date" in k
                or "PassFail" in k
            }
            d_filtered_list = [
                k.split("_") + [v] for k, v in d_filtered.items() if len(v) > 1
            ]

            """d_filtered_list is a list of lists with the following structure
            each element is a list of length 4, first being the testcase_id, second being the project_id, 
            third being the test_result field, 4th being the value of that field"""

            # 1. use the testcase_id and project_id to select the row from mapping table

            d_filtered_with_mapping = []
            for i in d_filtered_list:
                query = (
                    "SELECT map_id FROM Mapping WHERE testcase_id = "
                    + i[0]
                    + " AND project_id = "
                    + i[1]
                )
                mapping = [row for row in c.execute(query)][0][0]
                d_filtered_with_mapping.append([mapping] + i)
            # print(d_filtered_with_mapping)
            # 2. gather the values based on the mapping_id
            d_tr = {}
            for i in d_filtered_with_mapping:
                if i[0] not in d_tr:
                    d_tr[i[0]] = {}
                d_tr[i[0]][i[3]] = i[4]

            # print(d_tr)
            # 3. insert the values into the test_results table
            for map_id in d_tr.keys():
                c.execute(
                    "INSERT INTO testresults VALUES (:tr_id, :map_id, :result_description, :config_info, :tester, :execution_date, :pass_fail)",
                    {
                        "tr_id": None,
                        "map_id": map_id,
                        "result_description": d_tr[map_id].get("ResDescription", ""),
                        "config_info": d_tr[map_id].get("ConfigInfo", ""),
                        "tester": d_tr[map_id].get("Tester", ""),
                        "execution_date": d_tr[map_id].get("Date", ""),
                        "pass_fail": d_tr[map_id].get("PassFail", ""),
                    },
                )
            conn.commit()

        else:
            project_id = request.form["projects"]
            query = (
                "SELECT * FROM Mst_testcases INNER JOIN Mapping ON Mst_testcases.testcase_id = Mapping.testcase_id INNER JOIN Mst_projects ON Mst_projects.project_id = Mapping.project_id WHERE Mst_projects.project_id = "
                + project_id
            )
            testcases = [row for row in c.execute(query)]
            # testcases = c.fetchall()
            # select project name from the MstProjects table with the project_id
            query = (
                "SELECT name, project_id FROM Mst_projects WHERE project_id = "
                + project_id
            )
            project_name = [row for row in c.execute(query)]
            conn.close()
            return render_template(
                "testresults.html",
                testcases=testcases,
                projects=projects,
                sel_project=project_name[0][0],
                sel_project_id=project_name[0][1],
            )
    conn.close()
    return render_template("testresults.html", projects=projects)


@app.route("/testresults_by_project", methods=["GET", "POST"])
@login_required
def testresults_by_project():
    conn = sqlite3.connect("testing.db")
    c = conn.cursor()
    # get all project ids and project names from the MstProjects table
    query = "SELECT project_id, name FROM Mst_projects"
    projects = [row for row in c.execute(query)]

    if request.method == "POST":
        project_id = request.form["projects"]
        # query to fetch all the test results for a particular project id from the testresults table, using the mapping table
        query = "SELECT Mst_projects.*, Mst_testcases.*, testresults.* FROM mapping JOIN Mst_projects ON mapping.project_id = Mst_projects.project_id JOIN Mst_testcases ON mapping.testcase_id = Mst_testcases.testcase_id JOIN testresults ON mapping.map_id = testresults.map_id where Mst_projects.project_id = :project_id"
        all_d = [row for row in c.execute(query, {"project_id": project_id})]

        # print(all_d)

        query = "SELECT name FROM Mst_projects WHERE project_id = " + project_id
        project_name = [row for row in c.execute(query)]
        conn.close()
        return render_template(
            "testresults_by_project.html",
            testresults=all_d,
            projects=projects,
            sel_project=project_name[0][0],
        )
    conn.close()
    return render_template("testresults_by_project.html", projects=projects)


def sql_data_to_list_of_dicts(path_to_db, select_query):
    """Returns data from an SQL query as a list of dicts."""
    try:
        con = sqlite3.connect(path_to_db)
        con.row_factory = sqlite3.Row
        things = con.execute(select_query).fetchall()
        unpacked = [{k: item[k] for k in item.keys()} for item in things]
        return unpacked
    except Exception as e:
        print(f"Failed to execute. Query: {select_query}\n with error:\n{e}")
        return []
    finally:
        con.close()


@app.route("/downloadall")
@login_required
def downloadall():
    tr = sql_data_to_list_of_dicts(
        "testing.db",
        "SELECT Mst_projects.*, Mst_testcases.*, testresults.* FROM mapping JOIN Mst_projects ON mapping.project_id = Mst_projects.project_id JOIN Mst_testcases ON mapping.testcase_id = Mst_testcases.testcase_id JOIN testresults ON mapping.map_id = testresults.map_id",
    )

    mapp = sql_data_to_list_of_dicts(
        "testing.db",
        "SELECT Mst_projects.*, Mst_testcases.* FROM mapping JOIN Mst_projects ON mapping.project_id = Mst_projects.project_id JOIN Mst_testcases ON mapping.testcase_id = Mst_testcases.testcase_id JOIN testresults ON mapping.map_id = testresults.map_id",
    )

    tc = sql_data_to_list_of_dicts("testing.db", "Select * from Mst_testcases")

    projs = sql_data_to_list_of_dicts("testing.db", "Select * from Mst_projects")

    all_data = {}
    all_data["testresults"] = tr
    all_data["mapping"] = mapp
    all_data["testcases"] = tc
    all_data["projects"] = projs

    return Response(
        json.dumps(all_data, indent=4),
        mimetype="application/json",
        headers={"Content-Disposition": "attachment;filename=all_data.json"},
    )


@app.route("/noresults", methods=["GET", "POST"])
@login_required
def noresults():
    conn = sqlite3.connect("testing.db")
    c = conn.cursor()
    # get all project ids and project names from the MstProjects table
    query = "SELECT project_id, name FROM Mst_projects"
    projects = [row for row in c.execute(query)]

    if request.method == "POST":
        project_id = request.form["projects"]
        query = (
            "SELECT Mst_testcases.* FROM mapping JOIN Mst_projects ON mapping.project_id = Mst_projects.project_id JOIN Mst_testcases ON mapping.testcase_id = Mst_testcases.testcase_id WHERE map_id NOT IN (SELECT map_id FROM testresults) AND Mst_projects.project_id ="
            + project_id
        )
        testcases = [row for row in c.execute(query)]
        # testcases = c.fetchall()
        # select project name from the MstProjects table with the project_id
        query = "SELECT name FROM Mst_projects WHERE project_id = " + project_id
        project_name = [row for row in c.execute(query)]
        conn.close()
        return render_template(
            "noresults.html",
            testcases=testcases,
            projects=projects,
            sel_project=project_name[0][0],
        )
    conn.close()
    return render_template("noresults.html", projects=projects)

    pass


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))


@login_manager.unauthorized_handler
def unauthorized_handler():
    abort(401)
    # return "Unauthorized"


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, "static"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )


def create_tables():
    """create a new database if the database doesn't already exist
    database name testing.db
    tables
    1. Mst_testcases (testcase_id, name, test category, description, steps, expected_result, automated)
    2. Mst_projects (project_id, name, description)
    3. Mapping (map_id, project_id, testcase_id)
    4. testresults(tr_id, map_id, result_description, config_info, tester, execution_date, pass_fail)
    ON DELETE CASCADE (To delete all values recursively when a primary key is deleted)
    5. users (username, hash)
    """

    conn = sqlite3.connect("testing.db")
    # enforce foreign key rules
    conn.execute("PRAGMA foreign_keys = 1")
    c = conn.cursor()

    # create tables
    c.execute(
        """CREATE TABLE IF NOT EXISTS Mst_testcases (
                testcase_id INTEGER PRIMARY KEY,
                name TEXT,
                test_category TEXT,
                description TEXT,
                steps TEXT,
                expected_result TEXT,
                automated TEXT,
                dateC Text,
                userName Text )"""
    )

    c.execute(
        """CREATE TABLE IF NOT EXISTS Mst_projects (
                project_id INTEGER PRIMARY KEY,
                name TEXT,
                description TEXT,
                dateC Text,
                userName Text  )"""
    )

    c.execute(
        """CREATE TABLE IF NOT EXISTS Mapping (
                map_id INTEGER PRIMARY KEY,
                project_id INTEGER,
                testcase_id INTEGER,
                dateC Text,
                userName Text, 
                FOREIGN KEY(project_id) REFERENCES Mst_projects(project_id) 
                ON DELETE CASCADE,
                FOREIGN KEY(testcase_id) REFERENCES Mst_testcases(testcase_id)
                ON DELETE CASCADE )"""
    )

    c.execute(
        """CREATE TABLE IF NOT EXISTS testresults (
                tr_id INTEGER PRIMARY KEY,
                map_id INTEGER,
                result_description TEXT,
                config_info TEXT,
                tester TEXT,
                execution_date TEXT,
                pass_fail TEXT,
                FOREIGN KEY(map_id) REFERENCES Mapping(map_id)
                ON DELETE CASCADE )"""
    )
    """ add uniqueness constraint on mapping table project id and testcase id"""
    c.execute(
        """CREATE UNIQUE INDEX IF NOT EXISTS unique_mapping_index
                ON Mapping(project_id, testcase_id)"""
    )

    c.execute(""" CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            hash TEXT )""")
    
    conn.close()


if __name__ == "__main__":
    create_tables()
    app.run(
        debug=True, host="0.0.0.0"
    )  # drop the host parameter to make this local-only
    # available across the network at the moment.
