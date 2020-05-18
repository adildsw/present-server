# -*- coding: utf-8 -*-
"""
Created on Sun Feb 23 00:03:35 2020

@author: AdilDSW
"""

# Standard Built-in Libraries
from bcrypt import hashpw, gensalt

# 3rd-party Libraries
import pymongo

# Local Modules
from utils import status_code

class PresentDatabaseInterface:
    
    def __init__(self):
        self.db_key = {
            'details': {
                'columns': ["org_name", "acc_type", "acc_pwd"],
                'constraints': ["n", "un", "np"],
                'foreign_keys': ["", "", ""],
                'map': ["", "", ""]
                },
            'departments': {
                'columns': ["dept_name", "dept_code"],
                'constraints': ["un", "n"],
                'foreign_keys': ["", ""],
                'map': ["", ""]
                },
            'faculties': {
                'columns': ["faculty_name", "faculty_code", "dept_id", 
                            "faculty_pwd"],
                'constraints': ["n", "un", "nf", "np"],
                'foreign_keys': ["", "", "departments", ""],
                'map': ["", "", "dept_name", ""]
                },
            'classes': {
                'columns': ["class_code", "dept_id", "class_start", 
                            "class_end", "class_section"],
                'constraints': ["un", "nf", "n", "n", "n"],
                'foreign_keys': ["", "departments", "", "", ""],
                'map': ["", "dept_name", "", "", ""]
                },
            'students': {
                'columns': ["student_roll", "student_name", "class_id", 
                            "device_uid"],
                'constraints': ["un", "n", "nf", ""],
                'foreign_keys': ["", "", "classes", ""],
                'map': ["", "", "class_code", ""]
                },
            'courses': {
                'columns': ["course_code", "course_name", "faculty_id", 
                            "class_id", "course_status", "course_info"],
                'constraints': ["n", "n", "nfm", "nfm", "n", "un"],
                'foreign_keys': ["", "", "faculties", "classes", "", ""],
                'map': ["", "", "faculty_code", "class_code", "", ""]
                },
            'sessions': {
                'columns': ["session_code", "course_id", "timestamp", 
                            "op_faculty_code", "session_status", 
                            "control_share"],
                'constraints': ["un", "nf", "n", "n", "n", ""],
                'foreign_keys': ["", "courses", "", "", "", ""],
                'map': ["", "course_info", "", "", "", ""]
                },
            'attendance_logs': {
                'columns': ["log_code", "session_id", "mode", "student_id", 
                            "timestamp"],
                'constraints': ["un", "nf", "n", "nf", "n"],
                'foreign_keys': ["", "sessions", "", "students", ""],
                'map': ["", "session_code", "", "student_roll", ""]
                }
            }
        
        self.doc_names = ['details', 'departments', 'faculties', 'classes', 
                          'students', 'courses', 'sessions', 'attendance_logs']
        
        self.client = None
    
    def init_values(self, ip, port, user, pwd, authdb):
        self.ip = ip
        self.port = port
        self.user = user
        self.pwd = pwd
        self.authdb = authdb
        self.client = pymongo.MongoClient("{}:{}".format(ip, port),
                                         username=user, password=pwd,
                                         authSource=authdb)
        self.present_db = self.client["present_db"]
    
    def check_db_connection(self):
        try:
            if self.client:
                self.client.server_info()
                connected = True
                message = "Database Connection Established Successfully!"
            else:
                connected = False
                message = "Database Not Initialized."
        except Exception as err:
            connected = False
            message = str(err)
        finally:
            return {'connected': connected, 'message': message}
        
    def fetch_data(self, doc_name, query={}):
        try:
            status = ""
            data = []
            query = self.map_to_id(doc_name, query)['data'] if query else {}
            qres = self.present_db[doc_name].find(query)
            for item in qres:
                map_res = self.map_to_fk(doc_name, item)
                if map_res['status'] != "S0":
                    status = map_res['status']
                    break
                item = map_res['data']
                data.append(item)
            if status == "" and data:
                status = "S0"
            elif status == "" and not data:
                status = "S1"
        except Exception as e:
            status = "E9"
            print("ERROR: {}".format(str(e)))
        finally:
            message = status_code[status]
            return {'status': status, 'message': message, 'data': data}
    
    def update_data(self, doc_name, query, mod_query):
        try:
            error_count = 0
            query = self.map_to_id(doc_name, query)['data'] if query else {}
            query_res = self.fetch_data(doc_name, query)
            query_data = query_res['data']
            for q_data in query_data:
                for key, value in mod_query.items():
                    q_data[key] = value
                ccheck = self.constraint_check(doc_name, q_data, 
                                               is_modification=True)
                q_data = ccheck['data']
                q_data = self.hash_pwds(doc_name, q_data)
                q_status = ccheck['status']
                if q_status == "S3":
                    self.present_db[doc_name].update_many(query, 
                                                          {'$set': q_data})
                else:
                    error_count += 1
            status = "S2" if error_count else "S0"
        except Exception as e:
            status = "E9"
            print("ERROR: {}".format(str(e)))
        finally:
            message = status_code[status]
            return {'status': status, 'message': message}
    
    def insert_data(self, doc_name, data):
        try:
            ccheck = self.constraint_check(doc_name, data)
            data = ccheck['data']
            data = self.hash_pwds(doc_name, data)
            status = ccheck['status']
            if status == "S3":
                self.present_db[doc_name].insert_one(data)
                status = "S0"
        except Exception as e:
            status = "E9"
            print("ERROR: {}".format(str(e)))
        finally:
            message = status_code[status]
            return {'status': status, 'message': message}
    
    def insert_many_data(self, doc_name, data):
        try:
            pass_data = []
            fail_data = []
            for item in data:
                ccheck = self.constraint_check(doc_name, item)
                item = ccheck['data']
                item = self.hash_pwds(doc_name, item)
                if ccheck['status'] != "S3":
                    item['message'] = ccheck['message']
                    fail_data.append(item)
                else:
                    pass_data.append(item)
            if len(pass_data) != 0:
                self.present_db[doc_name].insert_many(pass_data)
                
            if len(pass_data) < len(data):
                status = "S2"
            else:
                status = "S0"
        except Exception as e:
            status = "E9"
            print("ERROR: {}".format(str(e)))
        finally:
            message = status_code[status]
            return {'status': status, 'message': message, 
                    'fail_data': fail_data}
        
    def delete_data(self, doc_name, query={}):
        """Deletes record from database.
        
        NOTE: THIS FUNCTION IS IN ALPHA STAGE, USE ONLY FOR REMOVING ATTENDANCE
        """
        try:
            if not query:
                status = "E1"
            else:
                flag = 0
                docs = self.doc_names.copy()
                if doc_name not in docs:
                    status = "E0"
                else:
                    docs.remove(doc_name)
                    query_res = self.fetch_data(doc_name, query)
                    
                    primary_col = ""
                    for idx in range(
                            len(self.db_key[doc_name]['constraints'])):
                        if 'u' in self.db_key[doc_name]['constraints'][idx]:
                            primary_col = self.db_key[doc_name]['columns'][idx]
                            break
                    primary_data = query_res['data'][0][primary_col]
                        
                    for doc in docs:
                        maps = self.db_key[doc]['map']
                        if primary_col in maps:
                            map_idx = maps.index(primary_col)
                            data_res = self.fetch_data(doc)
                            data = data_res['data']
                            for d in data:
                                if d[primary_col] == primary_data:
                                    flag = flag + 1
                                    break
                            if flag > 0:
                                break
                    
                    if flag > 0:
                        status = "E15"
                    else:
                        query = {primary_col: primary_data}
                        self.present_db[doc_name].delete_one(query)
                        status = "S0"
        except Exception as e:
            status = "E9"
            print("ERROR: {}".format(str(e)))
        finally:
            message = status_code[status]
            return {'status': status, 'message': message}
    
    ###########################
    # Constraints Check
    ###########################
    def constraint_check(self, doc_name, data, is_modification=False):
        status = self.column_check(doc_name, data)
        if status == "S0":
            status = self.null_check(doc_name, data)
        if status == "S0" and not is_modification:
            status = self.unique_check(doc_name, data)
        if status == "S0":
            status = self.duplicate_entry_check(doc_name, data)
        if status == "S0":
            map_res = self.map_to_id(doc_name, data)
            status = map_res['status']
            data = map_res['data']
        status = "S3" if status == "S0" else status
        message = status_code[status]
            
        return {'status': status, 'message': message, 'data': data}
    
    def get_id(self, doc_name, key, value):
        query = {key: value}
        res = self.fetch_data(doc_name, query)
        if res['status'] == "S0":
            return res['data'][0]['_id']
        else:
            return None
    
    def get_data_from_id(self, doc_name, _id, key=""):
        query = {'_id': _id}
        res = self.fetch_data(doc_name, query)
        if res['status'] == "S0":
            if key:
                return res['data'][0][key]
            else:
                return res['data'][0]
        else:
            return None
    
    def map_to_id(self, doc_name, data):
        """Takes data of a particular collection as input, removes mapped 
        foreign key values and replaces them with the foreign key _id 
        references. Returns the modified data.
        
        Used when making entry into the database.
        """
        mapped_data = {}
        columns = self.db_key[doc_name]['columns']
        constraints = self.db_key[doc_name]['constraints']
        foreign_keys = self.db_key[doc_name]['foreign_keys']
        maps = self.db_key[doc_name]['map']
        for key, value in data.items():
            if key in maps:
                idx = maps.index(key)
                if 'm' not in constraints[idx]:
                    fk_id = self.get_id(foreign_keys[idx], key, value)
                    if fk_id:
                        mapped_data[columns[idx]] = fk_id
                    else:
                        return {'status': "E6", 
                                'message': status_code["E6"],
                                'data': []}
                else:
                    mapped_value = []
                    for val in value:
                        fk_id = self.get_id(foreign_keys[idx], key, val)
                        if fk_id:
                            mapped_value.append(fk_id)
                        else:
                            return {'status': "E6", 
                                    'message': status_code["E6"],
                                    'data': []}
                    mapped_data[columns[idx]] = mapped_value
            else:
                mapped_data[key] = value
        return {'status': "S0", 'message': status_code["S0"], 
                'data': mapped_data}
    
    def map_to_fk(self, doc_name, data):
        """Takes data of a particular collection as input, removes foreign key
        _id references and replaces them with the mapped foreign key values. 
        Returns the modified data. 
        
        Used when fetching data from database.
        """
        mapped_data = {}
        columns = self.db_key[doc_name]['columns']
        constraints = self.db_key[doc_name]['constraints']
        foreign_keys = self.db_key[doc_name]['foreign_keys']
        maps = self.db_key[doc_name]['map']
        for key, value in data.items():
            if key not in columns:
                mapped_data[key] = value
                continue
            idx = columns.index(key)
            if 'f' in constraints[idx]:
                if 'm' not in constraints[idx]:
                    fk_data = self.get_data_from_id(foreign_keys[idx], value, 
                                                    maps[idx])
                    if fk_data:
                        mapped_data[maps[idx]] = fk_data
                    else:
                        return {'status': "E6", 
                                'message': status_code["E6"],
                                'data': []}
                else:
                    mapped_value = []
                    for val in value:
                        fk_data = self.get_data_from_id(foreign_keys[idx],
                                                        val, maps[idx])
                        if fk_data:
                            mapped_value.append(fk_data)
                        else:
                            return {'status': "E6", 
                                    'message': status_code["E6"],
                                    'data': []}
                    mapped_data[maps[idx]] = mapped_value
            else:
                mapped_data[key] = value
        return {'status': "S0", 'message': status_code["S0"], 
                'data': mapped_data}
    
    def mapped_columns(self, doc_name):
        """Returns the mapped columns of a collection required to make an 
        input, i.e., replaces the columns with the mapped foreign key columns,
        if present. 
        
        Helpful for performing constraint checks like column and null check.
        """
        columns = self.db_key[doc_name]['columns']
        maps = self.db_key[doc_name]['map']
        m_columns = []
        for i in range(len(columns)):
            if maps[i]:
                m_columns.append(maps[i])
            else:
                m_columns.append(columns[i])
        return m_columns
    
    def hash_pwds(self, doc_name, data):
        columns = self.mapped_columns(doc_name)
        constraints = self.db_key[doc_name]['constraints']
        for idx, head in enumerate(columns):
            if 'p' in constraints[idx]:
                data[head] = hashpw(data[head].encode(), gensalt())
        return data
    
    def column_check(self, doc_name, data):
        columns = self.mapped_columns(doc_name)
        for head in columns:
            if head not in data:
                return "E0"
        
        return "S0"
        
    def null_check(self, doc_name, data):
        columns = self.mapped_columns(doc_name)
        constraints = self.db_key[doc_name]['constraints']
        for idx, head in enumerate(columns):
            if 'n' in constraints[idx]:
                if not data[head]:
                    return "E1"
        
        return "S0"
    
    def duplicate_entry_check(self, doc_name, data):
        res = self.fetch_data(doc_name)
        for res_data in res['data']:
            unq_count = 0
            for key, value in data.items():
                if res_data[key] != value:
                    unq_count += 1
            if unq_count == 0:
                return "E2"
        
        return "S0"
    
    def unique_check(self, doc_name, data):
        columns = self.mapped_columns(doc_name)
        constraints = self.db_key[doc_name]['constraints']
        for idx, head in enumerate(columns):
            if 'u' in constraints[idx]:
                query = {head: data[head]}
                res = self.fetch_data(doc_name, query)
                if res['status'] == "S0":
                    return "E2"
                elif res['status'] == "E9":
                    return "E9"
                elif res['status'] == "S1":
                    continue
        
        return "S0"
        

if __name__ == "__main__":
    pdi = PresentDatabaseInterface()
    pdi.init_values("192.168.0.100", "27017", 
                    "administrator", "password", "admin")
    
    # query = {'acc_type':"admin"}
    # query = {'dept_name': 'Information Technology'}
    # print(pdi.get_data_from_id("faculties", "5ea56d7edcfd2030c4ef46d4"))
    # print(pdi.fetch_data("departments", {'dept_code': "IT"}))
    # pdi.present_db["sessions"].update_many({'op_faculty_code': "UKD"}, {'$set': {'session_status': "Active"}})
    
    # doc_name = "departments"
    # data = {'dept_name': 1, 'dept_code': "IT"}
    # print(pdi.constraint_check(doc_name, data))