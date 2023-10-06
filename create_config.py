import configparser

config_file = configparser.ConfigParser()

# Sections
config_file.add_section("Transfer")
config_file.add_section("Paths")

# Settings
config_file.set("Transfer", "source_endpoint_id", "28e1658e-6ce6-11e9-bf46-0e4a062367b8")
config_file.set("Transfer", "dest_endpoint_id", "6ce834d6-ff8a-11e6-bad1-22000b9a448b")

# Save
with open(r"config.ini", 'w') as configfileObj:
    config_file.write(configfileObj)
    configfileObj.flush()
    configfileObj.close()

print("Config file 'configurations.ini' created")
