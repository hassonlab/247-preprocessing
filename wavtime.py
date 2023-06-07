import glob
import wavinfo
import datetime as dt

# TODO: make input variable
patient = '705'

data = []

# Input directory
main_dir = 'R:/Epilepsy_ECOG/ecog/data/'
# TODO: directory works for all patients?
search = main_dir + 'NY%s/ZoomAudioFiles/**/*.WAV' % patient

# Loop through all audio files for patient
for wavfile in glob.glob(search):
    name = wavfile.split('\\')[-1]

    # Read metadata from audio file header
    try:
        info = wavinfo.WavInfoReader(wavfile)
    except StopIteration:
        data.append((name,'Could not read chunks.','','',''))
        continue

    # Separate info we want to save
    fs = info.fmt.sample_rate
    n_frames = info.data.frame_count
    n_seconds = n_frames / fs
    origin_date = info.bext.originator_date
    origin_time = info.bext.originator_time
    start_date = dt.datetime.strptime(origin_date + ' ' + origin_time, '%Y-%m-%d %H:%M:%S')
    end_date = start_date + dt.timedelta(seconds=n_seconds)
    duration = end_date - start_date

    data.append((name, fs, 
        start_date.strftime('%Y-%m-%d,%H:%M:%S'), 
        end_date.strftime('%Y-%m-%d,%H:%M:%S'), 
        str(duration).split('.')[0]
    ))

    #print(data[-1], origin_date, origin_time)

if len(data) == 0:
    exit()

with open('NY' + patient + '-timestamps' + '.csv', 'w') as f:
    f.write('File,fs,start date, start time, end date, end time,duration\n')
    for datum in data:
        f.write('{},{},{},{},{}\n'.format(*datum))

        
