import requests, sqlite3, json, os
from itertools import chain
from urllib.parse import urlparse
from multiprocessing import cpu_count
from multiprocessing.pool import ThreadPool

class Helper:
    def __init__(self, database_path='database.db', download_path='downloaded_files'):
        self.database_path = os.path.join(os.getcwd(), database_path)
        self.download_path = os.path.join(os.getcwd(), download_path)
        self.status_counter = 0
        self.file_count = 0

    def request_token(self, project_id):
        payload = {
            "scopes": ["user:project"],
            "data": {
                "projects": [
                    {"id": project_id}
                ]
            }
        }

        headers = {
            "Content-Type": "application/json",
        }

        response = requests.post("https://core.api.dev.holobuilder.eu/v3/auth/token", json=payload, headers=headers)
        return response

    def get_ielements(self, auth_token):
        headers_query = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(auth_token)
        }

        response_query = requests.get("https://v2.project.api.dev.holobuilder.eu/v1/d1691aff-5bfb-4786-bc79-9a00d1d35189/ielements/index", headers=headers_query)

        if response_query.ok:
            iElements = []
            for token in response_query.json()['pageTokens']:
                page = requests.get("https://v2.project.api.dev.holobuilder.eu/v1/d1691aff-5bfb-4786-bc79-9a00d1d35189/ielements", params={"token":token}, headers=headers_query).json()
                iElements.append(page['page'])
            flatten_iElements = list(chain.from_iterable(iElements))
            return flatten_iElements
        return response_query.json()

    def connect_database(self, name):
        conn = sqlite3.connect(name)
        return conn

    def disconnect_database(self, conn):
        conn.close()

    def create_database_table(self, cur):
        cur.execute("""CREATE TABLE IF NOT EXISTS ielements (
                    childrenIds TEXT,
                    children_Ids TEXT,
                    createdAt TEXT,
                    createdBy TEXT,
                    descr TEXT,
                    externalReferences TEXT,
                    fileSize TEXT,
                    id TEXT PRIMARY KEY,
                    labels TEXT,
                    lastModifiedInDb TEXT,
                    metaData TEXT,
                    metaDataMap TEXT,
                    modifiedAt TEXT,
                    modifiedBy TEXT,
                    name TEXT,
                    parentId TEXT,
                    parent_Id TEXT,
                    pose TEXT,
                    rootId TEXT,
                    root_Id TEXT,
                    thumbnailUri TEXT,
                    type TEXT,
                    typeHint TEXT,
                    uri TEXT,
                    full_json TEXT
                    )""")
        return cur
        
    def insert_into_database(self, cur, ielement):
        cur.execute("INSERT INTO ielements VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",(
            json.dumps(ielement.get("childrenIds", None)) if ielement.get("childrenIds", None) else None,
            json.dumps(ielement.get("children_Ids", None)) if ielement.get("children_Ids", None) else None,
            ielement.get("createdAt", None),
            ielement.get("createdBy", None),
            ielement.get("descr", None),
            json.dumps(ielement.get("externalReferences", None)) if ielement.get("externalReferences", None) else None,
            ielement.get("fileSize", None),
            ielement.get("id", None),
            json.dumps(ielement.get("labels", None)) if ielement.get("labels", None) else None,
            ielement.get("lastModifiedInDb", None),
            json.dumps(ielement.get("metaData", None)) if ielement.get("metaData", None) else None,
            json.dumps(ielement.get("metaDataMap", None)) if ielement.get("metaDataMap", None) else None,
            ielement.get("modifiedAt", None),
            ielement.get("modifiedBy", None),
            ielement.get("name", None),
            ielement.get("parentId", None),
            ielement.get("parent_Id", None),
            json.dumps(ielement.get("pose", None)) if ielement.get("pose", None) else None,
            ielement.get("rootId", None),
            ielement.get("root_Id", None),
            ielement.get("thumbnailUri", None),
            ielement.get("type", None),
            ielement.get("typeHint", None),
            ielement.get("uri", None),
            json.dumps(ielement),
            ))

    def query_database(self, cur, string):
        cur.execute(f"""
            SELECT full_json FROM ielements
            WHERE 
                childrenIds LIKE '%{string}%' OR
                children_Ids LIKE '%{string}%' OR
                createdAt LIKE '%{string}%' OR
                createdBy LIKE '%{string}%' OR
                descr LIKE '%{string}%' OR
                externalReferences LIKE '%{string}%' OR
                fileSize LIKE '%{string}%' OR
                id LIKE '%{string}%' OR
                labels LIKE '%{string}%' OR
                lastModifiedInDb LIKE '%{string}%' OR
                metaData LIKE '%{string}%' OR
                metaDataMap LIKE '%{string}%' OR
                modifiedAt LIKE '%{string}%' OR
                modifiedBy LIKE '%{string}%' OR
                name LIKE '%{string}%' OR
                parentId LIKE '%{string}%' OR
                parent_Id LIKE '%{string}%' OR
                pose LIKE '%{string}%' OR
                rootId LIKE '%{string}%' OR
                root_Id LIKE '%{string}%' OR
                thumbnailUri LIKE '%{string}%' OR
                type LIKE '%{string}%' OR
                typeHint LIKE '%{string}%' OR
                uri LIKE '%{string}%'
                """)
        return cur

    def download_url(self, args):
        url, file_name = args[0], args[1]
        file_path = os.path.join(self.download_path, file_name)
        if not os.path.exists(file_path):
            try:
                r = requests.get(url)
                with open(file_path, 'wb') as f:
                    f.write(r.content)
                    self.status_counter += 1
                print(f"downloaded {self.status_counter}/{self.file_count} files")
                return 1
            except Exception as e:
                print("Exception in download_url():", e)
        else:
            print(f"{file_name} already exists")

    def initialize_project(self, project_id):
        response = self.request_token(project_id)
        if response.ok:
            auth_token = response.json()['data']['token']
        else:
            return False, response.json()
        
        iElements = self.get_ielements(auth_token)

        # If the project id is incorrect, the function returns False with the message
        if "data" in iElements and iElements["data"] is None:
            return False, iElements

        conn = self.connect_database(self.database_path)
        cur = conn.cursor()
        cur = self.create_database_table(cur)
        conn.commit()

        for ielement in iElements:
            try:
                self.insert_into_database(cur, ielement)
                conn.commit()
            except sqlite3.IntegrityError as e:
                return False, f"SQLite Integrity error : {e}, Database table with the same data more likely exists already!!"

        self.disconnect_database(conn)

        return True, iElements

    def query_string(self, search_string):
        conn = self.connect_database(self.database_path)
        cur = conn.cursor()
        try:
            cur = self.query_database(cur, search_string)
        except sqlite3.OperationalError as e:
            return False, f"SQLite Operation Error : {e}, Database with the mentioned table does not exist and hence query is not possible! Please initialize first and then try again."
        iElements = [json.loads(item[0]) for item in cur.fetchall()]
        self.disconnect_database(conn)
        if iElements:
            return True, iElements
        return True, "No iElements exist with the matching search string."

    def download_all_files(self):
        if not os.path.exists(self.download_path):
            os.makedirs(self.download_path)

        conn = self.connect_database(self.database_path)
        cur = conn.cursor()
        try:
            cur.execute("SELECT uri FROM ielements WHERE uri IS NOT NULL")
        except sqlite3.OperationalError as e:
            return False, f"SQLite Operation Error : {e}, Database with the mentioned table does not exist and hence query is not possible! Please initialize first and then try again."
        url_list, file_name_list = [], []
        for item in cur.fetchall():
            url = item[0]
            path = urlparse(url).path
            file_name, ext = os.path.splitext(path)
            file_name = file_name.split("/")
            file_name = file_name[-1] + "_" + file_name[-2] + ext    # Some files have same name and hence added extra string from its url
            if ext:
                url_list.append(url)
                file_name_list.append(file_name)

        self.disconnect_database(conn)

        args = zip(url_list, file_name_list)
        self.file_count = len(url_list)

        cpus = cpu_count()
        results = ThreadPool(cpus - 1).imap_unordered(self.download_url, args)
        for _ in results:   # Not using a while loop with status counter since there is a possibility that a file may not be downloaded and the while loop runs forever
            pass            # This is just to make the program wait till the parallel execution is complete

        return True, "Download successful"
    
    def download_all_status(self):
        download_status = f"downloaded {self.status_counter}/{self.file_count} files"
        if self.status_counter == 0:
            return False, "Download has not started yet. Please start the download and recall the API again for the latest update."
        return True, download_status