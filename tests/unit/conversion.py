import unittest
from sql_to_laravel_migrations import conversion


class TestConversionMethods(unittest.TestCase):
    maxDiff = None

    def test_table_to_class_name(self):
        self.assertEqual(conversion.table_to_class_name('person'), 'Person')
        self.assertEqual(
            conversion.table_to_class_name('good_person'),
            'GoodPerson')
        self.assertEqual(
            conversion.table_to_class_name('good_PerSon'),
            'GoodPerson')

    def test_class_code_generation(self):
        generated_code = conversion.generate_class_code(
            "GoodPerson", "good_person", [], "Select * from")
        expected_code = """<?php

use Illuminate\Support\Facades\Schema;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Database\Migrations\Migration;

class CreateGoodPersonTable extends Migration
{
    /**
    * Run the migrations.
    Select * from
    * @return void
    */
    public function up()
    {
        Schema::create('good_person', function (Blueprint $table) {

        });
    }

    /**
    * Reverse the migrations.
    *
    * @return void
    */
    public function down()
    {
        Schema::dropIfExists('good_person');
    }
}
?>
"""
        self.assertEqual(generated_code, expected_code)

    def test_generate_table_code(self):
        sql_rows = [
            ["id", "int", "YES", None, 0, 'auto_increment']
        ]
        generated_code = conversion.generate_table_code(
            "good_person", sql_rows, "Select * from")
        expected_code = """<?php

use Illuminate\Support\Facades\Schema;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Database\Migrations\Migration;

class CreateGoodPersonTable extends Migration
{
    /**
    * Run the migrations.
    Select * from
    * @return void
    */
    public function up()
    {
        Schema::create('good_person', function (Blueprint $table) {
            // ["id", "int", "YES", null, 0, "auto_increment"]
            $table->increments('id')->default('0');
            $table->timestamps();
        });
    }

    /**
    * Reverse the migrations.
    *
    * @return void
    */
    public function down()
    {
        Schema::dropIfExists('good_person');
    }
}
?>
"""
        self.assertEqual(generated_code, expected_code)

if __name__ == '__main__':
    unittest.main()
