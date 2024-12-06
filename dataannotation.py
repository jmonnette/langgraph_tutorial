import requests
from bs4 import BeautifulSoup

def fetch_document_data(doc_url):
    # Fetch the Google Doc's HTML content
    response = requests.get(doc_url)
    response.raise_for_status()  # raise an exception for HTTP errors

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the first table in the document
    table = soup.find('table')
    if table is None:
        raise ValueError("No table found in the document.")
    
    # Extract the table rows
    rows = table.find_all('tr')

    # List to hold parsed data
    extracted_data = []

    # Skip the header row
    for row in rows[1:]:
        cells = row.find_all('td')
        if len(cells) >= 3:
            x = int(cells[0].get_text().strip())  # x-coordinate
            char = cells[1].get_text().strip()    # character
            y = int(cells[2].get_text().strip())  # y-coordinate
            extracted_data.append({'char': char, 'x': x, 'y': y})

    return extracted_data

def print_unicode_grid(doc_url):
    # Fetch the document data from the Google Doc's table
    document_data = fetch_document_data(doc_url)
    
    # Determine the maximum x and y values
    max_x = max(item['x'] for item in document_data)
    max_y = max(item['y'] for item in document_data)
    
    # Initialize the grid with spaces, of size (max_y+1) x (max_x+1)
    grid = [[' ' for _ in range(max_x + 1)] for _ in range(max_y + 1)]
    
    # Populate the grid with characters, flip y-axis
    for item in document_data:
        char = item['char']
        x = item['x']
        y = item['y']
        grid[max_y - y][x] = char  # Flip the row to account for y increasing upwards
    
    # Print the grid, row by row
    for row in grid:
        print(''.join(row))

# Call the function with the URL to your public Google Doc
print_unicode_grid('https://docs.google.com/document/d/e/2PACX-1vShuWova56o7XS1S3LwEIzkYJA8pBQENja01DNnVDorDVXbWakDT4NioAScvP1OCX6eeKSqRyzUW_qJ/pub')