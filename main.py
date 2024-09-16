import time
import logging
import tkinter as tk
from tkinter import simpledialog
from mysql.connector import connect
from sync_logic import (
    DB_CONFIG, SHEET_ID, SHEET_RANGE,
    get_google_sheet_service, get_sheet_data, get_mysql_data,
    add_last_updated_column, handle_conflicts, update_sheet_data, update_mysql_data
)
from crud_gui import CRUDApp

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def sync_data(service, db_connection):
    sheet_data = get_sheet_data(service, SHEET_ID, SHEET_RANGE)
    if not sheet_data:
        logging.info("Google Sheets is empty. Skipping synchronization.")
        return

    db_data = get_mysql_data(db_connection)
    sheet_data = add_last_updated_column(service, SHEET_ID, sheet_data)
    final_data, updated = handle_conflicts(sheet_data, db_data)

    if updated:
        update_sheet_data(service, SHEET_ID, SHEET_RANGE, final_data)
        update_mysql_data(db_connection, final_data)
        logging.info("Data synchronized successfully.")
    else:
        logging.info("No updates needed. Data is already in sync.")

def ask_user_for_crud():
    root = tk.Tk()
    root.withdraw()  
    response = simpledialog.askstring("CRUD Operations", "Do you want to perform CRUD operations? (yes/no)")
    root.destroy()
    return response.lower() == 'yes' if response else False

def main():
    try:
        service = get_google_sheet_service()
        db_connection = connect(**DB_CONFIG)

        while True:
            sync_data(service, db_connection)
            if ask_user_for_crud():
                root = tk.Tk()
                app = CRUDApp(root, db_connection)
                root.mainloop()
            else:
                logging.info("User chose not to perform CRUD operations. Continuing with sync.")
            time.sleep(10)  
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    finally:
        if db_connection and db_connection.is_connected():
            db_connection.close()
            logging.info("MySQL connection closed.")

if __name__ == '__main__':
    main()