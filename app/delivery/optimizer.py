import numpy as np
# KNN to calculate the nearest coordinates (addresses) to a specific coordinate (address)
""" 
starting point

{
  "latitude": 37.7749,
  "longitude": -122.4194
}

destination
[{
  "address": "456 Elm St, San Francisco, CA",
  "city": "San Francisco",
  "id": 1,
  "latitude": 37.7749,
  "longitude": -122.4194,
  "postal_code": "94105"
}, ...
]
"""

""" 
{
  lets get the list
}

"""

def euclidean_distance(point1, point2):
    return np.linalg.norm(np.array(point1) - np.array(point2))

def distribute_work(deliveries, delivery_persons, deliveries_per_carrier, remaining):
    print(deliveries)
    assignment_list = []

    for carrier in delivery_persons:
        distances = []
        carrier_coordinates = (carrier.latitude, carrier.longitude)
        
        for delivery in deliveries:
            coordinates = (delivery.locations[0].latitude, delivery.locations[0].longitude)
            distance = euclidean_distance(coordinates, carrier_coordinates)
            distances.append((distance, delivery))

        distances.sort(key=lambda x: x[0])

        nearest_deliveries = [delivery for _, delivery in distances[:deliveries_per_carrier]]

        assignment_list.append((carrier, nearest_deliveries))

        deliveries = [delivery for delivery in deliveries if delivery not in nearest_deliveries]

    if remaining > 0:
        for carrier in delivery_persons:
            remaining_deliveries = deliveries[:remaining]
            assignment_list.append((carrier, remaining_deliveries))
            deliveries = deliveries[remaining:]

    return assignment_list


    
        

