#!/usr/bin/env python3
"""
Check Google Sheets structure and write a simple test
"""
from google.auth import default
from googleapiclient.discovery import build

# Initialize
credentials, _ = default()
service = build("sheets", "v4", credentials=credentials)
spreadsheet_id = "1cYfpnM_CjgdV1j9hlY-2l0QJMYDWB_hCeXb9KGbgwEo"

# Get spreadsheet metadata
try:
    spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheets = spreadsheet.get("sheets", [])

    print("Available sheets:")
    for sheet in sheets:
        title = sheet["properties"]["title"]
        sheet_id = sheet["properties"]["sheetId"]
        print(f"  - {title} (ID: {sheet_id})")

    # Try writing to the first available sheet
    if sheets:
        first_sheet = sheets[0]["properties"]["title"]
        print(f"\nTrying to write test data to: {first_sheet}")

        test_data = [["Test", "Data", "From", "Python"]]

        result = (
            service.spreadsheets()
            .values()
            .append(
                spreadsheetId=spreadsheet_id,
                range=first_sheet,
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body={"values": test_data},
            )
            .execute()
        )

        print(f"✅ SUCCESS: Test data written")
        print(
            f"Updated range: {result.get('updates', {}).get('updatedRange', 'Unknown')}"
        )

except Exception as e:
    print(f"❌ ERROR: {e}")
