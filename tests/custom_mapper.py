def custom_mapper(entry):
    entry.title += "_modified"
    if 'cell_number' in entry.custom_properties:
        entry.custom_properties["cell_number"] = "11111111"
    return entry
