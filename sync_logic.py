import os
import time
import logging
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import mysql.connector
from mysql.connector import Error

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Google Sheets API setup
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SHEET_ID = '1uqjegb9qNSwaAGIe3P7xJdwxNzh6OWglPv3vTV3VaYY'
SHEET_RANGE = 'Sheet1!A1:Z1000'  

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'Superjoin_Hiring_Process'
}

# Column mapping in case the headings in google sheet are slightly different 
COLUMN_MAPPING = {
    'candidate_id': ['Candidate ID', 'CandidateID', 'ID'],
    'candidate_name': ['Candidate Name', 'CandidateName', 'Name'],
    'interview_score': ['Interview Score', 'InterviewScore', 'Score'],
    'strength': ['Strength', 'Strengths'],
    'weakness': ['Weakness', 'Weaknesses'],
    'feedback': ['Feedback', 'Comments'],
    'last_updated': ['Last Updated', 'LastUpdated', 'UpdatedAt']
}

def get_mysql_data(db_connection):
    try:
        with db_connection.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM candidates")
            data = cursor.fetchall()
            #logging.debug(f"Fetched {len(data)} rows from MySQL")
            return data
    except Error as e:
        logging.error(f"Error fetching data from MySQL: {e}")
        return []

def get_google_sheet_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('sheets', 'v4', credentials=creds)

def get_sheet_data(service, spreadsheet_id, range_name):
    try:
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
        values = result.get('values', [])
        if not values:
            logging.debug("No data fetched from Google Sheets")
            return []
        header = values[0]
        data = [header] + [row + [''] * (len(header) - len(row)) for row in values[1:]]
        #logging.debug(f"Fetched {len(data) - 1} rows from Google Sheets")
        return data
    except Exception as e:
        logging.error(f"Error getting sheet data: {e}")
        return []

def get_column_index(header, column_names):
    for name in column_names:
        try:
            index = header.index(name)
            #logging.debug(f"Found column '{name}' at index {index}")
            return index
        except ValueError:
            continue
    logging.warning(f"Could not find any of these columns: {column_names}")
    return -1

def add_last_updated_column(service, spreadsheet_id, sheet_data):
    header = sheet_data[0]
    if 'Last Updated' not in header:
        header.append('Last Updated')
        for row in sheet_data[1:]:
            if len(row) < len(header):  
                row.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            else:
                row[-1] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    else:
        last_updated_index = header.index('Last Updated')
        for row in sheet_data[1:]:
            if len(row) <= last_updated_index or not row[last_updated_index].strip():
                row[last_updated_index] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    body = {
        'values': sheet_data
    }
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=SHEET_RANGE,
        valueInputOption='RAW',
        body=body
    ).execute()
    #logging.info("Added or updated 'Last Updated' column in Google Sheets.")
    return sheet_data

def handle_conflicts(sheet_data, db_data):
    if not sheet_data:
        return [list(COLUMN_MAPPING.keys())], True

    header = sheet_data[0]
    db_dict = {str(row['candidate_id']): row for row in db_data}

    column_indices = {db_col: get_column_index(header, sheet_cols) for db_col, sheet_cols in COLUMN_MAPPING.items()}
    #logging.debug(f"Column indices: {column_indices}")

    updated = False
    final_data = [header]

    sheet_dict = {row[column_indices['candidate_id']]: row for row in sheet_data[1:] if column_indices['candidate_id'] != -1}

    for candidate_id, db_row in db_dict.items():
        if candidate_id in sheet_dict:
            sheet_row = sheet_dict[candidate_id]
            db_last_updated = db_row.get('last_updated')
            try:
                sheet_last_updated = datetime.strptime(sheet_row[column_indices['last_updated']], '%Y-%m-%d %H:%M:%S') if column_indices['last_updated'] != -1 and sheet_row[column_indices['last_updated']] else None
            except (ValueError, TypeError):
                sheet_last_updated = None  
            
            # Check if data has changed
            has_changed = False
            for db_col, sheet_index in column_indices.items():
                if sheet_index != -1 and sheet_row[sheet_index] != str(db_row.get(db_col, '')):
                    has_changed = True
                    break
            
            if has_changed:
                # Update the 'Last Updated' timestamp if the sheet row has been modified
                sheet_row[column_indices['last_updated']] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                new_row = sheet_row
                updated = True
            else:
                new_row = [''] * len(header)
                for db_col, sheet_index in column_indices.items():
                    if sheet_index != -1:
                        new_row[sheet_index] = str(db_row.get(db_col, ''))
                updated = True
            final_data.append(new_row)
        else:
            # New row in the database, append it to the sheet
            new_row = [''] * len(header)
            for db_col, sheet_index in column_indices.items():
                if sheet_index != -1:
                    new_row[sheet_index] = str(db_row.get(db_col, ''))
            final_data.append(new_row)
            updated = True

    for sheet_row in sheet_data[1:]:
        candidate_id = sheet_row[column_indices['candidate_id']]
        if candidate_id not in db_dict:
            updated = True
            final_data.append(sheet_row)

    return final_data, updated

def update_mysql_data(db_connection, sheet_data):
    header = sheet_data[0]
    column_indices = {db_col: get_column_index(header, sheet_cols) for db_col, sheet_cols in COLUMN_MAPPING.items()}

    insert_query = """
    INSERT INTO candidates (candidate_id, candidate_name, interview_score, strength, weakness, feedback, last_updated)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
    candidate_name = VALUES(candidate_name),
    interview_score = VALUES(interview_score),
    strength = VALUES(strength),
    weakness = VALUES(weakness),
    feedback = VALUES(feedback),
    last_updated = VALUES(last_updated);
    """

    try:
        with db_connection.cursor() as cursor:
            for row in sheet_data[1:]:
                candidate_id = row[column_indices['candidate_id']]
                if not candidate_id:
                    continue
                
                data = []
                for db_col, idx in column_indices.items():
                    if idx != -1 and idx < len(row):
                        value = row[idx].strip() if row[idx] else None
                        if db_col == 'interview_score':
                            value = int(value) if value and value.isdigit() else None
                        elif db_col == 'last_updated':
                            value = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        data.append(value)
                    else:
                        data.append(None)
                cursor.execute(insert_query, tuple(data))

        db_connection.commit()
        logging.info("Database has been synchronized with Google Sheets.")
    except Error as e:
        logging.error(f"Error updating MySQL data: {e}")
        db_connection.rollback()

def update_sheet_data(service, spreadsheet_id, range_name, values):
    try:
        body = {
            'values': values
        }
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption='RAW',
            body=body
        ).execute()
        logging.info("Google Sheets has been updated with database changes.")
    except Exception as e:
        logging.error(f"Error updating Google Sheets: {e}")

def create_candidate(db_connection, candidate_data):
    query = """
    INSERT INTO candidates (candidate_id, candidate_name, interview_score, strength, weakness, feedback, last_updated)
    VALUES (%s, %s, %s, %s, %s, %s, %s);
    """
    try:
        with db_connection.cursor() as cursor:
            cursor.execute(query, candidate_data)
        db_connection.commit()
        logging.info("Candidate created successfully.")
    except Error as e:
        logging.error(f"Error creating candidate: {e}")
        db_connection.rollback()

def read_candidates(db_connection):
    query = "SELECT * FROM candidates"
    try:
        with db_connection.cursor(dictionary=True) as cursor:
            cursor.execute(query)
            data = cursor.fetchall()
        logging.info("Fetched candidates from database.")
        return data
    except Error as e:
        logging.error(f"Error reading candidates: {e}")
        return []

def update_candidate(db_connection, candidate_data):
    query = """
    UPDATE candidates
    SET candidate_name = %s, interview_score = %s, strength = %s, weakness = %s, feedback = %s, last_updated = %s
    WHERE candidate_id = %s;
    """
    try:
        with db_connection.cursor() as cursor:
            cursor.execute(query, candidate_data)
        db_connection.commit()
        logging.info("Candidate updated successfully.")
    except Error as e:
        logging.error(f"Error updating candidate: {e}")
        db_connection.rollback()

def delete_candidate(db_connection, candidate_id):
    query = "DELETE FROM candidates WHERE candidate_id = %s"
    try:
        with db_connection.cursor() as cursor:
            cursor.execute(query, (candidate_id,))
        db_connection.commit()
        logging.info("Candidate deleted successfully.")
    except Error as e:
        logging.error(f"Error deleting candidate: {e}")
        db_connection.rollback()

def sync_data():
    try:
        service = get_google_sheet_service()
        db_connection = mysql.connector.connect(**DB_CONFIG)

        sheet_data = get_sheet_data(service, SHEET_ID, SHEET_RANGE)
        if not sheet_data:
            logging.info("Google Sheets is empty. Exiting.")
            return

        db_data = get_mysql_data(db_connection)
        sheet_data = add_last_updated_column(service, SHEET_ID, sheet_data)
        final_data, updated = handle_conflicts(sheet_data, db_data)

        if updated:
            update_sheet_data(service, SHEET_ID, SHEET_RANGE, final_data)
            update_mysql_data(db_connection, final_data)

        return db_connection

    except Exception as e:
        logging.error(f"Unexpected error during synchronization: {e}")
        return None

if __name__ == '__main__':
    sync_data()