import csv

# Read the CSV and extract unique currency codes
currency_codes = set()

with open('data/worldcities.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        code = row['Currency Code'].strip()
        # Handle multiple codes separated by /
        if '/' in code:
            codes = [c.strip() for c in code.split('/')]
            currency_codes.update(codes)
        else:
            currency_codes.add(code)

# Sort and join with commas
sorted_codes = sorted(currency_codes)
print(f"Total unique currency codes: {len(sorted_codes)}\n")
print("Currency codes:")
print(", ".join(sorted_codes))
print(f"\n\nFull API URL:")
api_url = "https://api.forexrateapi.com/v1/latest?api_key=1e5ce0b6f7f9b60ffeb7b5f60dcf095d&base=USD&currencies=" + ",".join(sorted_codes)
print(api_url)

# Save to file for reference
with open('forex_api_url.txt', 'w') as f:
    f.write(f"Total unique currencies: {len(sorted_codes)}\n")
    f.write(f"Codes: {', '.join(sorted_codes)}\n\n")
    f.write(f"API URL:\n{api_url}\n")

print("\n✅ Saved to forex_api_url.txt")
