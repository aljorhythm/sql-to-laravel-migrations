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

field_type_name_mappings = {
    'tinyint' : 'tinyInteger',
    'int' : 'integer',
    'varchar' : 'string'
}

filter_field_type_params = {
    'tinyInteger' : lambda x : [],
    'integer' : lambda x : [],
    'increments' : lambda x : []
}

nullable_field_types = [
    'varchar',
    'timestamp',
    'datetime'
]

for table_name in table_names:
    print "Table: {0}".format(table_name)
    query = ("show columns from {0}".format(table_name))
    cursor.execute(query)

    table_schema_codes = []

    exclude_fields = ['created_at', 'updated_at']

    for row in cursor:
        field, field_type, null, key, default, extra = row

        if field in exclude_fields:
            continue

        field_type_split = field_type.split('(')

        field_type_name = field_type_split[0]
        field_type_name = field_type_name.lower()
        field_type_name = field_type_name_mappings[field_type_name] if field_type_name in field_type_name_mappings else field_type_name

        field_type_settings = field_type_split[1].split(' ') if len(field_type_split) > 1 else []

        field_type_params_string = field_type_split[1].split(')')[0] if len(field_type_split) > 1 else ''
        field_type_params = field_type_params_string.split(',') if field_type_params_string != '' else []
        field_type_params = filter_field_type_params[field_type_name](field_type_params) if field_type_name in filter_field_type_params else field_type_params

        if extra == 'auto_increment' and field == 'id':
            field_type_name = 'increments'

        appends = []
        if null == 'YES' and field_type_name in nullable_field_types:
            appends.append('->nullable()')
        if 'unsigned' in field_type_settings and field_type_name != 'increments':
            appends.append('->unsigned()')
        if default is not None:
            if default == 'CURRENT_TIMESTAMP':
                appends.append("->default(\DB::raw('{0}'))".format(default))
            else:
                appends.append("->default('{0}')".format(default))

        migration_params = [ param for param in ["'{0}'".format(field)] + field_type_params if param.strip() != "" ]
        table_schema_code = "$table->{0}({1}){2};".format(field_type_name, ", ".join(migration_params), "".join(appends));

        table_schema_codes.append("// " + json.dumps(row))
        table_schema_codes.append(table_schema_code)

    table_schema_code = "$table->timestamps();";
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

    output_file_name = "{0}/{1}_create_{2}_table.php".format(folder, datetime_prefix, table_name)
    f = open(output_file_name, 'w')
    f.write(code)
    print code
    print "File: {0}".format(output_file_name)

cursor.close()

cnx.close()
