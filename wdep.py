#!/usr/bin/env python
import argparse
import sys
import re

from pysndfx import AudioEffectsChain


def main():
    # Parsing for command line arguments
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description=(
            "Creates a vaporwave (slowed, with reverb) remix of a given MP3 file, with"
            " multiple audio effects available, and the option of playing over a looped"
            " GIF as a video."
        ),
    )

    parser.add_argument(
        "-o",
        "--output",
        dest="output_name",
        help=(
            "Name of output file(s), instead of audio file name with the addition of"
            " '_slowed+reverb'."
        ),
        type=str,
    )

    required_arguments = parser.add_argument_group("required arguments")

    required_arguments.add_argument(
        "-a",
        "--audio",
        dest="audio_input",
        help="Input audio file to vaporise (.mp3)",
        type=str,
        required=True,
    )

    audio_arguments = parser.add_argument_group(
        "audio arguments",
        "these arguments control audio effects that will be applied by default",
    )

    audio_arguments.add_argument(
        "-s",
        "--speed",
        dest="speed_ratio",
        help="Ratio of new playback speed to old speed.",
        type=float,
        default=0.75,
    )

    audio_arguments.add_argument(
        "-p",
        "--pitch",
        dest="pitch_shift",
        help="Pitch shift (100ths of a semitone).",
        type=float,
        default=-75,
    )

    audio_arguments.add_argument(
        "-l",
        "--lowpass",
        dest="lowpass_cutoff",
        help="Cutoff for lowpass filter (Hz).",
        type=int,
        default=3500,
    )

    audio_arguments_optional = parser.add_argument_group(
        "extra audio arguments", "these arguments control extra, optional audio effects"
    )

    audio_arguments_optional.add_argument(
        "-b",
        "--bass",
        dest="bass_boost",
        help="Add a bass boost effect (e.g. --bass 3).",
        type=int,
        default=3,
    )

    audio_arguments_optional.add_argument(
        "-ga",
        "--gain",
        dest="gain_db",
        help="Applies gain (dB).",
        type=int,
        default=None,
    )

    audio_arguments_optional.add_argument(
        "-op",
        "--oops",
        dest="oops",
        help=(
            "Applies Out Of Phase Stereo effect. This is sometimes known as the"
            " ‘karaoke’ effect as it often has the effect of removing most or all of"
            " the vocals from a recording."
        ),
        action="store_true",
    )

    audio_arguments_optional.add_argument(
        "-ph",
        "--phaser",
        dest="phaser",
        help="Enable phaser effect.",
        action="store_true",
    )

    audio_arguments_optional.add_argument(
        "-tr",
        "--tremolo",
        dest="tremolo",
        help="Enable tremolo effect.",
        action="store_true",
    )

    audio_arguments_optional.add_argument(
        "-co",
        "--compand",
        dest="compand",
        help="Enable compand, which compresses the dynamic range of the audio.",
        action="store_true",
    )

    audio_arguments_optional.add_argument(
        "-nr",
        "--noreverb",
        dest="no_reverb",
        help="Disables reverb.",
        action="store_true",
    )
    
    args = parser.parse_args()

    # Setting name of output file
    if args.output_name is None:
        # If no output name is given, add "_vaporised" to input audio file name
        audio_input_string = re.sub(".mp3", "", str(args.audio_input))
        audio_output = audio_input_string + "_slowed+reverb.mp3"
    else:
        # Otherwise, use the output file name given via the command line
        output_string = re.sub(".mp3", "", str(args.output_name))
        audio_output = output_string + ".mp3"
        if args.audio_input == args.output_name:
            print("ERROR: Input and output name are identical")
            sys.exit()

    # Creating an audio effects chain, beginning with...
    if args.bass_boost:
        # ...bass boost effect
        bass_boost = f'{"bass "}{args.bass_boost}'
        fx = AudioEffectsChain().custom(bass_boost)
        fx = fx.pitch(args.pitch_shift)
    else:
        # ...pitch shift
        fx = AudioEffectsChain().pitch(args.pitch_shift)

    # Adding OOPS to audio effects chain
    if args.oops:
        fx = fx.custom("oops")

    # Adding tremolo effect to the audio effects chain
    if args.tremolo:
        fx = fx.tremolo(freq=500, depth=50)

    # Adding phaser to the audio effects chain
    if args.phaser:
        # fx.phaser(gain_in, gain_out, delay, decay, speed)
        fx = fx.phaser(0.9, 0.8, 2, 0.2, 0.5)

    # Adding gain to the audio effects chain
    if args.gain_db is not None:
        fx = fx.gain(db=args.gain_db)

    # Adding compand to the audio effects chain
    if args.compand:
        fx = fx.compand()

    # Adding lowpass filter, speed alteration to audio effects chain
    fx = fx.speed(args.speed_ratio).lowpass(args.lowpass_cutoff)

    if args.no_reverb is False:
        # Adding reverb to audio effects chain
        fx = fx.reverb()

    # Applying audio effects
    fx(args.audio_input, audio_output)



if __name__ == "__main__":
    main()
