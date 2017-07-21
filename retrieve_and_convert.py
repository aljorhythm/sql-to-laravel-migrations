import mysql.connector
import datetime
import os
import json
import sys

config_file_name = 'config.json' if len(sys.argv) < 2 else sys.argv[1]

with open(config_file_name) as data_file:
    config = json.load(data_file)

datetime_prefix_format = '%Y_%m_%d_%H%M%S'
datetime_prefix = datetime.datetime.now().strftime(datetime_prefix_format)
folder = 'output/' + datetime_prefix
os.mkdir(folder)

user = config['user']
password = config['password']
host = config['host']
port = config['port']
database = config['database']
exclude_tables = config['exclude_tables']
only_include_tables = config['only_include_tables']

cnx = mysql.connector.connect(user=user, password=password,
                              host=host,
                              port=port,
                              database=database)

cursor = cnx.cursor()
query = ("select TABLE_SCHEMA, TABLE_NAME, TABLE_TYPE from `information_schema`.`tables` where TABLE_SCHEMA = '{0}';".format(database))
cursor.execute(query)

table_names = [line[1] for line in cursor]
if len(only_include_tables) > 0:
    table_names = [table_name for table_name in table_names if table_name in only_include_tables]
else:
    table_names = [table_name for table_name in table_names if not table_name in exclude_tables ]

field_type_mappings = {
    'tinyint' : 'tinyInteger',
    'int' : 'integer',
    'varchar' : 'string'
}

filter_params = {
    'tinyInteger' : lambda x : [],
    'integer' : lambda x : []
}

field_type_filter = {
    'id' : 'increments'
}

for table_name in table_names:
    print "Table: {0}".format(table_name)
    query = ("show columns from {0}".format(table_name))
    cursor.execute(query)

    table_schema_codes = []

    for row in cursor:
        field_name, right = row[:2]

        right_split = right.split('(')
        field_type = right_split[0]
        params = right_split[1].split(')')[0].split(',') if len(right_split) > 1 else []

        field_type = field_type.lower()
        field_type = field_type_mappings[field_type] if field_type in field_type_mappings else field_type;
        field_type = field_type_filter[field_name] if field_name in field_type_filter else field_type

        params = filter_params[field_type](params) if field_type in filter_params else params
        migration_params = [ param for param in ["'{0}'".format(field_name)] + params if param.strip() != "" ]
        table_schema_code = "$table->{0}({1});".format(field_type, ", ".join(migration_params));

        table_schema_codes.append(table_schema_code)

    cursor = cnx.cursor()
    query = ("SHOW CREATE TABLE {0}".format(table_name))
    cursor.execute(query)
    sql = []
    for row in cursor:
        sql.append(row[1].encode('utf-8'))
    sql = ''.join(sql)
    code = '''
<?php

use Illuminate\Support\Facades\Schema;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Database\Migrations\Migration;

class {classname} extends Migration
{{
    /**
     * Run the migrations.
     {sql}
     * @return void
     */
    public function up()
    {{
      Schema::create('{table_name}', function (Blueprint $table) {{
        {table_schema_codes}
      }});
    }}

    /**
     * Reverse the migrations.
     *
     * @return void
     */
    public function down()
    {{
        Schema::dropIfExists('{table_name}');
    }}
}}
?>
'''
    code = code.format( sql = sql, classname = "Create{0}Table".format(table_name.replace('_', ' ').title().replace(' ', '')), table_schema_codes = "\n        ".join(table_schema_codes), table_name = table_name)

    f = open("{0}/{1}_create_{2}_table.php".format(folder, datetime_prefix, table_name), 'w')
    f.write(code)

cursor.close()

cnx.close()
