from src.database.database import TRIAL_URL, DB_NAME, drop_database, engine, drop_all_tables
from src.database.database import create_all_tables, create_database_if_not_exists
from src.database.utils import add_test_data

drop_database(TRIAL_URL, DB_NAME)
create_database_if_not_exists(TRIAL_URL, DB_NAME)
drop_all_tables(engine)
create_all_tables(engine)
add_test_data()
