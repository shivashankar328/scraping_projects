import mysql.connector
from scrapy.exceptions import DropItem
from scrapy.utils.project import get_project_settings


class ShipdetailsPipeline:
    def __init__(self):
        self.settings = get_project_settings()

    def open_spider(self, spider):
        self.connect_mysql()

    def connect_mysql(self):
        try:
            self.cnx = mysql.connector.connect(
                host=self.settings['MYSQL_HOST'],
                port=self.settings['MYSQL_PORT'],
                database=self.settings['MYSQL_DATABASE'],
                user=self.settings['MYSQL_USER'],
                password=self.settings['MYSQL_PASSWORD']
            )
            self.cursor = self.cnx.cursor()
        except mysql.connector.Error as err:
            print("Error: {}".format(err))

    def create_table_if_not_exists(self, item):
        try:
            self.table = 'steamship'
            col_names = ', '.join([f'{key} VARCHAR(255)' for key in item.keys()])
            create_table_query = f"CREATE TABLE IF NOT EXISTS {self.table} ({col_names})"
            self.cursor.execute(create_table_query)
            self.cnx.commit()
        except mysql.connector.Error as err:
            print("Error: {}".format(err))
            self.cnx.rollback()
    def close_spider(self, spider):
        try:
            self.cursor.close()
            self.cnx.close()
        except mysql.connector.Error as err:
            print("Error: {}".format(err))

    def process_item(self, item, spider):
        try:
            self.create_table_if_not_exists(item)
            self.insert_into_mysql(item)
        except mysql.connector.Error as err:
            print("Error: {}".format(err))
            raise DropItem(f"Failed to insert item into MySQL: {err}")
        return item

    def insert_into_mysql(self, item):
        # table = 'steamship'
        columns = ', '.join(item.keys())
        placeholders = ', '.join(['%s'] * len(item))
        sql = f"INSERT INTO {self.table} ({columns}) VALUES ({placeholders})"
        values = tuple(item.values())

        try:
            self.cursor.execute(sql, values)
            self.cnx.commit()
        except mysql.connector.Error as err:
            print("Error: {}".format(err))
            self.cnx.rollback()
            raise DropItem(f"Failed to insert item into MySQL: {err}")
