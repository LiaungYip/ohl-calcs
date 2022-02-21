import csv

from ena_db5 import Conductor

with open("conditions.csv") as fh_in:
    reader = csv.DictReader(fh_in)
    conditions = list(reader)

with open("conductor_data/catalog_data.csv") as fh_in:
    with open("outfile.csv", mode='w', newline='') as fh_out:
        writer = csv.writer(fh_out)

        # write condition descriptions header row
        header_row = ["Manufacturer", "Codename", ]
        header_row.extend([c["description"] for c in conditions])
        writer.writerow(header_row)

        # write condition parameters rows x5
        for k in ('t_a', 't_c', 'time_of_day', 'v', 'weathering'):
            header_row = [k, '']
            header_row.extend([c[k] for c in conditions])
            writer.writerow(header_row)

        reader = csv.DictReader(fh_in, dialect="excel", )
        for line in reader:
            manufacturer = line["Manufacturer"]
            codename = line["Codename"]
            _type = line["Type"]
            dia = float(line["Nominal overall diameter (mm)"]) / 1000  # Convert mm -> m
            dc_R = float(line["DC resistance at 20 deg. C (ohm/km)"]) / 1000  # Convert ohm/km -> ohm/m

            if "ACSR" in _type:
                layer_construction = line["Layer Construction"]
            else:
                layer_construction = None

            conductor = Conductor(codename, _type, dia, dc_R, layer_construction)

            ratings = []
            for c in conditions:
                desc = c["description"]
                t_a = float(c["t_a"])
                t_c = float(c["t_c"])
                v = float(c["v"])
                weathering = c["weathering"]
                time_of_day = c["time_of_day"]

                rating = conductor.calc(t_a, t_c, v, weathering, time_of_day)
                ratings.append(rating)

            out_row = [manufacturer, codename, ]
            out_row.extend(ratings)
            writer.writerow(out_row)
