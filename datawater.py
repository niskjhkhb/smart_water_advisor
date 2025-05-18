import csv
import random

regions = ['Urban', 'Suburban', 'Rural']

# Ideal monthly usage per person (liters)
ideal_per_person_usage = {
    'Urban': 600,      # more efficient, less gardening
    'Suburban': 650,   # moderate usage
    'Rural': 700       # slightly higher for gardening, livestock, etc.
}

num_rows = 200
output_file = 'ideal_water_data.csv'

rows = []
for _ in range(num_rows):
    region = random.choice(regions)
    people = random.randint(1, 6)
    base = ideal_per_person_usage[region] * people
    # Add small random variation +/- 5%
    usage = base * random.uniform(0.95, 1.05)
    usage = round(usage, 2)
    rows.append([region, people, usage])

with open(output_file, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['region', 'number_of_people', 'monthly_usage_liters'])
    writer.writerows(rows)

print(f"✅ {num_rows} rows saved to {output_file}")
