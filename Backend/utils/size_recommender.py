# utils/size_recommender.py

# Approved Press-On AI Nominal Sizes (0-9)
# Interval boundaries based on midpoint rounding:
#  - Size 0: nominal 18.0 mm (width >= 17.0 mm)
#  - Size 1: nominal 16.0 mm (15.5 mm <= width < 17.0 mm)
#  - Size 2: nominal 15.0 mm (14.5 mm <= width < 15.5 mm)
#  - Size 3: nominal 14.0 mm (13.5 mm <= width < 14.5 mm)
#  - Size 4: nominal 13.0 mm (12.5 mm <= width < 13.5 mm)
#  - Size 5: nominal 12.0 mm (11.5 mm <= width < 12.5 mm)
#  - Size 6: nominal 11.0 mm (10.5 mm <= width < 11.5 mm)
#  - Size 7: nominal 10.0 mm (9.5 mm  <= width < 10.5 mm)
#  - Size 8: nominal 9.0 mm  (8.5 mm  <= width < 9.5 mm)
#  - Size 9: nominal 8.0 mm  (7.5 mm  <= width < 8.5 mm)
#  - < 7.5 mm: Outside supported size range

SIZE_CHART = [
    {"size": "0", "nominal": 18.0, "min": 17.0, "max": float("inf")},
    {"size": "1", "nominal": 16.0, "min": 15.5, "max": 17.0},
    {"size": "2", "nominal": 15.0, "min": 14.5, "max": 15.5},
    {"size": "3", "nominal": 14.0, "min": 13.5, "max": 14.5},
    {"size": "4", "nominal": 13.0, "min": 12.5, "max": 13.5},
    {"size": "5", "nominal": 12.0, "min": 11.5, "max": 12.5},
    {"size": "6", "nominal": 11.0, "min": 10.5, "max": 11.5},
    {"size": "7", "nominal": 10.0, "min": 9.5, "max": 10.5},
    {"size": "8", "nominal": 9.0, "min": 8.5, "max": 9.5},
    {"size": "9", "nominal": 8.0, "min": 7.5, "max": 8.5},
]


def recommend_size(width_mm):
    """
    Authoritative Press-On AI nail size recommendation.
    Converts measured nail width in millimeters to standard press-on nail sizes (0 to 9).

    If width_mm is below 7.5 mm, returns 'Outside supported size range'.
    """
    if width_mm is None:
        return "Unknown"

    try:
        width = round(float(width_mm), 2)
    except (ValueError, TypeError):
        return "Unknown"

    if width < 7.5:
        return "Outside supported size range"

    for item in SIZE_CHART:
        if item["min"] <= width < item["max"]:
            return item["size"]

    if width >= 17.0:
        return "0"

    return "Outside supported size range"