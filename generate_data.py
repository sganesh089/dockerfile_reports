from faker import Faker
from faker.providers import BaseProvider
from datetime import date as Date
import json
import random

# number of JSON entries
n = 10000

fake = Faker()


# create new provider class to generate Sightdata entries
class MyProvider(BaseProvider):
    def area(self) -> str:
        # Generate area/camera entries on the construction site
        elements = ["Area A", "Area B", "Area C"]
        return elements[random.randint(0, 2)]

    def module(self) -> str:
        # Generate module type
        elements = ["Exclusion Zone Detection", "Loose Object Detection"]  # , "PPE Detection"
        return elements[random.randint(0, 1)]

    def exclusion(self) -> str:
        # Generate value returned from exclusion zone module
        elements = ["Breach", "Close Proximity", "Compliant", "Compliant", "Compliant", "Compliant", "Compliant"]
        return elements[random.randint(0, 6)]

    def looseObject(self) -> str:
        # Generate value returned from loose object module
        elements = ["Unresolved", "Resolved", "Resolved", "Resolved", "Resolved"]
        return elements[random.randint(0, 4)]

    def PPE(self) -> str:
        # Generate value returned from PPE module
        elements = ["Breach", "Compliant", "Compliant", "Compliant"]
        return elements[random.randint(0, 3)]


# then add new provider to faker instance
fake.add_provider(MyProvider)

with open('resources/data3.json', 'w', encoding='utf-8') as f:
    for i in range(0, n):
        module = fake.module()
        # Generate value depending on module
        if module == "Exclusion Zone Detection":
            value = fake.exclusion()

        # elif module == "Loose Object Detection":
        else:
            value = fake.looseObject()
        # else:
        #    value = fake.PPE()

        # Generate data as a JSON entry
        data = {
            'Date': fake.date_time_between(Date(2022, 1, 1), Date.today()).strftime('%Y-%m-%d %H:%M:%S'),
            'Camera': fake.area(),
            'Module': module,
            'Value': value,
        }

        # Write JSON entry in file
        json.dump(data, f, ensure_ascii=False)
        f.write('\n')