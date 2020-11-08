# bioSong

#### A tool for getting xeno-canto bird calls and transforming them for use in TensorFlow

*bioSong is a work in progress. There is no error checking. Use at your own risk.*

#### bioSong connects to the Xeno-Canto API allowing batch downloading of bird calls from a specific species or cournty. Sub-species is currently not allowed.

- .mp3 files are downloaded for user specified search criteria

- .mp3 files are converted to .wav

- files are upsampled or downsampled per user settings

- stft functionality is being implemented in the GUI but not yet functioning

#### Upcoming changes and planned features:

1.  Allow searching for sub-species
    
2.  Allow searching for species recordings from specific countries
    
3.  GUI development (Batch downloading and resamplign works via the gui)
    
4.  User input error checking (This works for some inputs)
    
Stretch goal:
1.  Develop TensorFlow integration
    
    -use to train models for image recognition
    
    -test on personal recordings from Dominica
