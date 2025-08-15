import gspread
import streamlit as st
from datetime import datetime
import logging
from typing import List, Dict, Any
from google.oauth2.service_account import Credentials

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Google Sheets IDs
INDIVIDUAL_SHEET_ID = "15R_7NwIfIq66pWApCNtY3xhNR9OLA4UIP5KeKehIaQg"
TEAM_SHEET_ID = "14wBeJQRbHDki2meDxUEITmBoCYa9GfuwgcNMFEYlK8Q"

class SheetsService:
    def __init__(self):
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Google Sheets client using service account credentials"""
        try:
            # Get credentials from Streamlit secrets
            credentials_info = {
                "type": st.secrets["gcp_service_account"]["type"],
                "project_id": st.secrets["gcp_service_account"]["project_id"],
                "private_key_id": st.secrets["gcp_service_account"]["private_key_id"],
                "private_key": st.secrets["gcp_service_account"]["private_key"],
                "client_email": st.secrets["gcp_service_account"]["client_email"],
                "client_id": st.secrets["gcp_service_account"]["client_id"],
                "auth_uri": st.secrets["gcp_service_account"]["auth_uri"],
                "token_uri": st.secrets["gcp_service_account"]["token_uri"],
                "auth_provider_x509_cert_url": st.secrets["gcp_service_account"]["auth_provider_x509_cert_url"],
                "client_x509_cert_url": st.secrets["gcp_service_account"]["client_x509_cert_url"],
                "universe_domain": st.secrets["gcp_service_account"]["universe_domain"]
            }
            
            # Define the scope
            scopes = ['https://www.googleapis.com/auth/spreadsheets']
            
            # Create credentials
            credentials = Credentials.from_service_account_info(credentials_info, scopes=scopes)
            
            # Initialize gspread client
            self.client = gspread.authorize(credentials)
            logger.info("Google Sheets client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Google Sheets client: {str(e)}")
            self.client = None
    
    def _ensure_headers(self, worksheet, headers: List[str]):
        """Ensure the worksheet has the correct headers"""
        try:
            # Get current headers
            current_headers = worksheet.row_values(1)
            
            # If no headers or headers don't match, update them
            if not current_headers or current_headers != headers:
                worksheet.clear()
                worksheet.append_row(headers)
                logger.info(f"Headers updated for worksheet: {worksheet.title}")
                
        except Exception as e:
            logger.error(f"Error ensuring headers: {str(e)}")
            raise
    
    def save_individual_response(self, response_data: Dict[str, Any]) -> bool:
        """Save individual response to Google Sheets"""
        try:
            if not self.client:
                logger.error("Google Sheets client not initialized")
                return False
            
            # Open the individual responses sheet
            sheet = self.client.open_by_key(INDIVIDUAL_SHEET_ID)
            worksheet = sheet.get_worksheet(0)  # First worksheet
            
            # Define headers for individual responses
            headers = [
                "Timestamp", "Name", "CRN", "Contact", "Email", 
                "Selected Team", "Feedback"
            ]
            
            # Ensure headers are correct
            self._ensure_headers(worksheet, headers)
            
            # Prepare row data
            row_data = [
                response_data["timestamp"],
                response_data["name"],
                response_data["crn"],
                response_data["contact"],
                response_data["email"],
                response_data["selected_team"],
                response_data["comments"]
            ]
            
            # Append the row
            worksheet.append_row(row_data)
            logger.info(f"Individual response saved for: {response_data['name']}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving individual response: {str(e)}")
            return False
    
    def save_team_response(self, response_data: Dict[str, Any]) -> bool:
        """Save team response to Google Sheets with merged cells for same team"""
        try:
            if not self.client:
                logger.error("Google Sheets client not initialized")
                return False
            
            # Open the team responses sheet
            sheet = self.client.open_by_key(TEAM_SHEET_ID)
            worksheet = sheet.get_worksheet(0)  # First worksheet
            
            # Define headers for team responses
            headers = [
                "Timestamp", "Team Name", "Selected Team", "Member Count", 
                "Comments", "Member Name", "CRN", "Contact", "Email", "Team Lead"
            ]
            
            # Ensure headers are correct
            self._ensure_headers(worksheet, headers)
            
            # Get current row count to know where to start
            current_rows = len(worksheet.get_all_values())
            start_row = current_rows + 1
            
            # Prepare team data
            team_info = [
                response_data["timestamp"],
                response_data["team_name"],
                response_data["selected_team"],
                str(response_data["member_count"]),
                response_data["comments"]
            ]
            
            # Add each member
            members = response_data["members"]
            for i, member in enumerate(members):
                is_team_lead = "Yes" if i == 0 else "No"
                
                row_data = team_info + [
                    member["name"],
                    member["crn"],
                    member["contact"],
                    member["email"],
                    is_team_lead
                ]
                
                worksheet.append_row(row_data)
            
            # Merge cells for team information (columns A-E) for all rows of this team
            end_row = start_row + len(members) - 1
            
            if len(members) > 1:  # Only merge if more than one member
                try:
                    # Merge timestamp column (A)
                    worksheet.merge_cells(f'A{start_row}:A{end_row}')
                    # Merge team name column (B)
                    worksheet.merge_cells(f'B{start_row}:B{end_row}')
                    # Merge selected team column (C)
                    worksheet.merge_cells(f'C{start_row}:C{end_row}')
                    # Merge member count column (D)
                    worksheet.merge_cells(f'D{start_row}:D{end_row}')
                    # Merge comments column (E)
                    worksheet.merge_cells(f'E{start_row}:E{end_row}')
                    
                    logger.info(f"Merged cells for team: {response_data['team_name']}")
                except Exception as merge_error:
                    logger.warning(f"Could not merge cells: {str(merge_error)}")
            
            logger.info(f"Team response saved for: {response_data['team_name']}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving team response: {str(e)}")
            return False
    
    def test_connection(self) -> tuple[bool, str]:
        """Test the connection to Google Sheets"""
        try:
            if not self.client:
                return False, "Google Sheets client not initialized"
            
            # Try to open a test sheet
            sheet = self.client.open_by_key(INDIVIDUAL_SHEET_ID)
            worksheet = sheet.get_worksheet(0)
            
            # Try to read the first cell
            test_value = worksheet.acell('A1').value
            
            return True, "Google Sheets connection successful"
            
        except Exception as e:
            return False, f"Google Sheets connection failed: {str(e)}"

# Global instance
sheets_service = SheetsService()

def save_individual_response(response_data: Dict[str, Any]) -> bool:
    """Convenience function to save individual response"""
    return sheets_service.save_individual_response(response_data)

def save_team_response(response_data: Dict[str, Any]) -> bool:
    """Convenience function to save team response"""
    return sheets_service.save_team_response(response_data)

def test_sheets_connection() -> tuple[bool, str]:
    """Convenience function to test connection"""
    return sheets_service.test_connection()