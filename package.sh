python3 -m pip install --upgrade autopep8
autopep8 --in-place --aggressive --recursive tests/ sql_to_laravel_migrations/
python3 -m pip install --user --upgrade setuptools wheel
python3 setup.py sdist bdist_wheel