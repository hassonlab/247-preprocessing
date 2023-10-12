import configparser

config_file = configparser.ConfigParser()

# Sections
config_file.add_section("Transfer")
config_file.add_section("NYUPaths")
config_file.add_section("PtonPaths")
config_file.add_section("PtonSubpaths")
config_file.add_section("NameFormats")

# Settings
config_file.set("Transfer", "source_endpoint_id", "28e1658e-6ce6-11e9-bf46-0e4a062367b8")
config_file.set("Transfer", "dest_endpoint_id", "6ce834d6-ff8a-11e6-bad1-22000b9a448b")

config_file.set("NYUPaths", "nyu_downsampled_audio_path", "ZoomAudioFilesDownsampled/")
config_file.set("NYUPaths", "nyu_deid_audio_path", "DeidAudio/DeidAudio/")
config_file.set("NYUPaths", "nyu_ecog_path", "Dayfiles/")

#config_file.set("PtonPaths", "scotty_prefix_path", "/mnt/cup/labs")
#config_file.set("PtonPaths", "user_prefix_path", "/Volumes")
config_file.set("PtonPaths", "base_path", "/mnt/cup/labs/hasson/247/subjects")

config_file.set("PtonSubpaths", "audio_512_path", "audio/audio-512Hz/")
config_file.set("PtonSubpaths", "audio_deid_path", "audio/audio-deid/")
config_file.set("PtonSubpaths", "ecog_raw_path", "ecog/ecog-raw/")
config_file.set("PtonSubpaths", "audio_transcribe_path", "audio/audio-transcribe/")
config_file.set("PtonSubpaths", "ecog_processed_path", "ecog/ecog-processed/")
config_file.set("PtonSubpaths", "silence_path", "notes/de-id/")
config_file.set("PtonSubpaths", "log_path", "log/")
config_file.set("PtonSubpaths", "anat_path", "anat/")
config_file.set("PtonSubpaths", "issue_path", "issue/")
config_file.set("PtonSubpaths", "transcript_path", "transcript/xml/")

config_file.set("NameFormats", "file_name_format", "{sid}_Part{part}_{type}.{ext}")

# Save
with open(r"config.ini", 'w') as configfileObj:
    config_file.write(configfileObj)
    configfileObj.flush()
    configfileObj.close()

print("Config file 'configurations.ini' created")
