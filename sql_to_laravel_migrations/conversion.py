import json

field_type_name_mappings = {
    'tinyint': 'tinyInteger',
    'int': 'integer',
    'varchar': 'string'
}

filter_field_type_params = {
    'tinyInteger': lambda x: [],
    'integer': lambda x: [],
    'increments': lambda x: []
}

nullable_field_types = [
    'varchar',
    'timestamp',
    'datetime'
]


def table_to_class_name(table_name):
    return table_name.replace('_', ' ').title().replace(' ', '')


def generate_class_code(classname, table_name, table_schema_codes, sql):
    code = """<?php

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
"""
    return code.format(sql=sql, classname="Create{0}Table".format(table_name.replace('_', ' ').title(
    ).replace(' ', '')), table_schema_codes="\n        ".join(table_schema_codes), table_name=table_name)


def generate_table_code(table_name, sql_rows, table_sql):
    exclude_fields = ['created_at', 'updated_at']
    table_schema_codes = []
    for row in sql_rows:
        field, field_type, null, __, default, extra = row

        if field in exclude_fields:
            continue

        field_type_split = field_type.split('(')

        field_type_name = field_type_split[0]
        field_type_name = field_type_name.lower()
        field_type_name = field_type_name_mappings[
            field_type_name] if field_type_name in field_type_name_mappings else field_type_name

        field_type_settings = field_type_split[1].split(
            ' ') if len(field_type_split) > 1 else []

        field_type_params_string = field_type_split[1].split(
            ')')[0] if len(field_type_split) > 1 else ''
        field_type_params = field_type_params_string.split(
            ',') if field_type_params_string != '' else []
        field_type_params = filter_field_type_params[field_type_name](
            field_type_params) if field_type_name in filter_field_type_params else field_type_params

        if extra == 'auto_increment' and field == 'id':
            field_type_name = 'increments'

        appends = []
        if null == 'YES' and field_type_name in nullable_field_types:
            appends.append('->nullable()')
        if 'unsigned' in field_type_settings and field_type_name != 'increments':
            appends.append('->unsigned()')
        if default is not None:
            if default == 'CURRENT_TIMESTAMP':
                appends.append(r"->default(\DB::raw('{0}'))".format(default))
            else:
                appends.append("->default('{0}')".format(default))

        migration_params = [
            param for param in [
                "'{0}'".format(field)] +
            field_type_params if param.strip() != ""]
        table_schema_code = "$table->{0}({1}){2};".format(
            field_type_name, ", ".join(migration_params), "".join(appends))

        table_schema_codes.append("// " + json.dumps(row))
        table_schema_codes.append(table_schema_code)

    table_schema_code = "$table->timestamps();"
    table_schema_codes.append(table_schema_code)
    classname = table_to_class_name(table_name)
    return generate_class_code(
        classname, table_name, table_schema_codes, table_sql)
