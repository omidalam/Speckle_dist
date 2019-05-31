Genomic loci to compartment distance ImageJ plugin
================
Omid Gholamalamdari
5/24/2019

# Goal

We are often interested in finding the relative distance of a genomic
loci with respect to a nuclear compartment (e.g Nuclear Speckles,
Nucleoulus) in our microscopic experiments. The goal of this document is
describe the algorithm used in an ImageJ plugin. This algorithm is
developed based on conversations between Dr. Andrew Belmont lab members.

# Process

## loci indentification

1.  User draws a ROI containing the genomic loci and the closest nuclear
    compartment.
      - The loci identification is done by the user. (Can automate it
        but it would be challenging for low SNR)
      - The closest nuclear is guess by the user, user can repeat the
        process if there close ties.

## User input

ImageJ user defines following parameters.

1.  Channel number containing nuclear comartment signal a number between
    1-4.
2.  Channel number containing genomic loci signal a number between 1-4.
3.  Threshold value for compartment boundary detection based on percent
    of maximum signal: a number between 0.0-1.0 .
4.  Method to define the genomic loci
      - Maximum intensity pixel: The pixel location of maximum intensity
        in loci signal.
      - Boundary: for huge diffuse signal (e.g. amplified TetO array).
        This can be done by defining a border for signal based on
        thresholding. Requires a Threshold value between 0-1.
      - Center of mass: The pixel location of the center of mass.
        Defined based on the binary thresholded signal. Requires a
        Threshold value between 0-1. (under development)

# Algorithm

## Compartment bounary detection

I’m defining the border of the nuclear speckles as some percentage of
the maximum signal intensity (let’s say 50% of maximum signal). This
boundary would be different for signals with different noise level. For
example figure below shows the line profile a spot with and without
noise. The threshold line for generating the binary image is defined as
max/2. Note that the binary image of the noisy is going to be bigger.
![Boundary detection based on 50% of maximum
signal.](README_files/figure-gfm/unnamed-chunk-1-1.png)

### Noise subtraction

Removing the background noise is crucial for boundary measurements. -
Sources of noise

### Defining nuclear compartment boundary

1.
