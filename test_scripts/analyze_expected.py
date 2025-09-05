#!/usr/bin/env python3
"""
Analyze the expected output to understand the correct mapping
"""

# Expected output from your comparison
expected_data = [
    ("9780001839236", "Summer Story", 4.995, 3),
    ("9780008547110", "Brambly Hedge Pop-Up Book, The", 14.995, 3),
    ("9780062645425", "Pleasant Fieldmouse", 12.495, 3),
    ("9780062883124", "Frog and Toad Storybook Favorites", 8.495, 3),
    ("9780062916570", "Wild and Free Nature", 11.495, 3),
    ("9780063090002", "Plant the Tiny Seed Board Book", 4.995, 3),
    ("9780063424500", "Kiss for Little Bear, A", 8.995, 3),
    ("9780064435260", "Little Prairie House, A", 4.995, 3),
    ("9780544066656", "Jack and the Beanstalk", 6.495, 2),
    ("9780544880375", "Rain! Board Book", 3.995, 3),
    ("9780547370187", "Little Red Hen, The", 6.495, 2),
    ("9780547370194", "Three Bears, The", 6.495, 2),
    ("9780547370200", "Three Little Pigs, The", 6.495, 2),
    ("9780547449272", "Tons of Trucks", 6.995, 3),
    ("9780547668550", "Little Red Riding Hood", 6.495, 2),
    ("9780694003617", "Goodnight Moon Board Book", 5.495, 3),
    ("9780694006380", "My Book of Little House Paper Dolls", 7.495, 3),
    ("9780694006519", "Jamberry Board Book", 4.995, 3),
    ("9780694013203", "Grouchy Ladybug Board Book, The", 4.995, 3),
    ("9781805074182", "Drawing, Doodling and Coloring Activity Book Usbor", 3.495, 3),
    ("9781805078913", "Little Sticker Dolly Dressing Puppies Usborne", 4.495, 3),
    ("9781836050278", "Little Sticker Dolly Dressing Fairy Usborne", 4.495, 3),
    ("9781911641100", "Place Called Home, A", 22.5, 2),
]

print("Expected ISBN/Title mapping:")
for isbn, title, price, qty in expected_data:
    list_price = price / 0.5  # Back-calculate list price
    print(f"'{isbn}': {{'title': '{title}', 'price': {list_price:.2f}, 'qty': {qty}}},")

print(f"\nTotal expected items: {len(expected_data)}")

# Convert date 04/29/25 to Excel serial number
from datetime import datetime, date

target_date = date(2025, 4, 29)
excel_epoch = date(1900, 1, 1)
# Excel incorrectly treats 1900 as a leap year, so we need to add 1
excel_serial = (target_date - excel_epoch).days + 2
print(f"\nExcel date serial for 04/29/25: {excel_serial}")
