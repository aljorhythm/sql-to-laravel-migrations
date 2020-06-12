<?php
$config_filename = count($argv) > 1 ? $argv[1] : "config.json";

$config_file = fopen($config_filename, "r") or die("Unable to open file!");
$config = json_decode(fread($config_file, filesize($config_filename)), 2);

fclose($config_file);

$timezone = array_key_exists('php_timezone', $config) ? $config['php_timezone'] : 'Asia/Singapore';
date_default_timezone_set($timezone);

$datetime_prefix_format = 'Y_m_d_His';
$datetime_prefix = date($datetime_prefix_format);

$folder = 'output/' . $datetime_prefix;

if(!is_dir($folder)){
    mkdir($folder, 0777, true);
}

$debug = isset($config['debug']) ? $config['debug'] : false;
$user = $config['user'];
$password = $config['password'];
$host = $config['host'];
$port = $config['port'];
$database = $config['database'];
$exclude_tables = $config['exclude_tables'];
$only_include_tables = $config['only_include_tables'];

$mysqli = new mysqli($host . ":" . $port, $user, $password, $database);

/* check connection */
if ($mysqli->connect_errno) {
    printf("Connect failed: %s\n", $mysqli->connect_error);
    exit();
}

$query = (sprintf("select TABLE_SCHEMA, TABLE_NAME, TABLE_TYPE, TABLE_COMMENT from `information_schema`.`tables` where TABLE_SCHEMA = '%s';", ($database)));

$tables = [];

if($result = $mysqli->query($query)){
  while($row = $result->fetch_array()){
    $tables []= $row;
  };
  $result->close();
}

$table_names = array_map(function($table){return $table[1];}, $tables);

if(count($only_include_tables) > 0){
    $table_names = array_filter($table_names, function($table_name) use ($table_names, $only_include_tables) { return in_array($table_name, $only_include_tables); });
} else {
    $table_names = array_filter($table_names, function($table_name) use ($table_names, $exclude_tables) { return !in_array($table_name, $exclude_tables); });
}

$field_type_name_mappings = [
    'tinyint' => 'tinyInteger',
    'int' => 'integer',
    'varchar' => 'string'
];

$filter_field_type_params = [
    'tinyInteger' => function($x) { return []; },
    'integer' => function($x) { return []; },
    'increments' => function($x) { return []; }
];

$nullable_field_types = [
    'varchar'
];

foreach ($table_names as $table_name){
    echo sprintf("Table: %s", $table_name);
    $query = sprintf("show full columns from %s", $table_name);

    $table_schema_codes = [];
    $exclude_fields = ['created_at', 'updated_at'];

    $fields = [];
    if($result = $mysqli->query($query)){
        while($row = $result->fetch_assoc()){
            $row = array_values($row);
            $field = $row[0];
            $field_type = $row[1];
            $collation = $row[2];
            $null = $row[3];
            $key = $row[4];
            $default = $row[5];
            $extra = $row[6];
            $comment = $row[8];

            if(in_array($field, $exclude_fields)){
                continue;
            }

            $field_type_split = explode('(', $field_type);

            $field_type_name = $field_type_split[0];
            $field_type_name = strtolower($field_type_name);
            $field_type_name = array_key_exists($field_type_name, $field_type_name_mappings) ? $field_type_name_mappings[$field_type_name] : $field_type_name;

            $field_type_settings = count($field_type_split) > 1 ? explode(' ', $field_type_split[1]) : [];

            $field_type_params_string = count($field_type_split) > 1 ? explode(')', $field_type_split[1])[0] : '';
            $field_type_params = $field_type_params_string != '' ? explode(',', $field_type_params_string) : [];
            $field_type_params = array_key_exists($field_type_name, $filter_field_type_params) ? $filter_field_type_params[$field_type_name]($field_type_params) : $field_type_params;

            if($extra == 'auto_increment' && $field == 'id'){
                $field_type_name = 'increments';
            }

            $appends = [];
            if($null == 'YES' && in_array($field_type_name, $nullable_field_types)){
                $appends []= '->nullable()';
            }
            if(in_array('unsigned', $field_type_settings) && $field_type_name != 'increments'){
                $appends []= '->unsigned()';
            }
            if(!is_null($default)){
                if($default == 'CURRENT_TIMESTAMP'){
                    $appends []= sprintf("->default(\DB::raw('%s'))", $default);
                }else{
                    $appends []= sprintf("->default('%s')", $default);
                }
            }
            if($comment) {
                $appends []= "->comment('{$comment}')";
            }

            $migration_params = array_merge([sprintf("'%s'", $field)], $field_type_params);
            $migration_params = array_filter($migration_params, function($param){
              return trim($param) != "";
            });


            $table_schema_code = sprintf("    \$table->%s(%s)%s;", $field_type_name, implode(", ", $migration_params), implode("", $appends));

            $debug and $table_schema_codes []= "// " . json_encode($row);
            $table_schema_codes []= $table_schema_code;
        };
    }

    $table_schema_code = '    $table->timestamps();';
    $table_schema_codes []= ($table_schema_code);

    $query = "SHOW INDEX FROM {$table_name};";

    $indexes = [];
    $results = $mysqli->query($query);
    while($row = $results->fetch_array()){
        if ($row[2] != 'PRIMARY') {
            $indexes[$row[2]]['is_unique'] = $row[1] ? false : true;
            $indexes[$row[2]]['keys'][] = $row[4];
        }
    }

    if (!empty($indexes)) {
        foreach ($indexes as $indexName => $index) {
            $table_schema_codes[] = '    $table->' . ($index['is_unique'] ? 'unique' : 'index') . '(["' . implode('", "', $index['keys']) .'"]);';
        }
    }

    $query = ("SHOW CREATE TABLE {$table_name};");

    $sql = [];
    $results = $mysqli->query($query);
    while($row = $results->fetch_array()){
      $sql []= $row[1];
    }
    $sql = implode('\n', $sql);

    $classname = sprintf("Create%sTable", str_replace(' ', '', str_replace('_', ' ', ucwords($table_name))));

    $table_schema_codes = implode("\n        ", $table_schema_codes);

    $code = "

<?php

use Illuminate\Support\Facades\Schema;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Database\Migrations\Migration;

class $classname extends Migration
{
    /**
     * Run the migrations.
     *" . ($debug ? $sql : '') . "
     * @return void
     */
    public function up()
    {
        Schema::create('$table_name', function (Blueprint \$table) {
        $table_schema_codes
        });
    }

    /**
     * Reverse the migrations.
     *
     * @return void
     */
    public function down()
    {
        Schema::dropIfExists('$table_name');
    }
}

";
    $output_file_name = sprintf("%s/%s_create_%s_table.php", $folder, $datetime_prefix, $table_name);
    echo $code . "\n";
    file_put_contents ( $output_file_name , $code );
    echo "File: $output_file_name";
}
