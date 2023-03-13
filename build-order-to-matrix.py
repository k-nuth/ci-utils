import json

def main():
    matrix = {"config": []}

    with open("platform.json", "r") as platform_file:
        platform_data = json.load(platform_file)

        with open("build_order.json", "r") as read_file:
            data = json.load(read_file)
            for level in data:
                for reference in level:
                    for platform in platform_data['config']:
                        platform["name"] = f'{platform["name"]} - {reference["ref"]}'
                        platform["reference"] = reference["ref"]
                        matrix["config"].append(platform)

            if len(matrix["config"]) == 0:
                matrix["config"].append({"reference": "null"})

    # print(matrix)
    with open("matrix.json", "w") as write_file:
        json.dump(matrix, write_file)
        write_file.write("\n")

if __name__ == "__main__":
    main()
