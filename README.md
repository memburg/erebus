# Erebus

Erebus is a work to help you share content on the internet and preserve your privacy.

## How it works?

| ![](./docs/resources/lenna.gif)                                                                          |
|:--------------------------------------------------------------------------------------------------------:|
| [1] Lenna or Lena is a standard test image used in the field of image processing since 1973. It is a picture of the Swedish model Lena Forsén, shot by photographer Dwight Hooker, cropped from the centerfold of the November 1972 issue of Playboy magazine. In this example we can see what happens behind the scenes during the encryption process. |

## How to run?

Since Erebus is still under development, only Windows is supported; MAC and Linux will eventually be able to run this.

### Windows

To encrypt an image you can run the following command:

```
./erebus -action protect -inputFile ./input/path/example.png -iterations 1000
```

To decrypt an image you can run the following command:

```
./erebus -action unprotect -inputFile ./input/path/example.png -keyPath ./key/path/example.csv
```

## Results


| **Original**                    | **Encrypted (I = 1000)**             | **Encrypted (I = 2000)**             | **Encrypted (I = 5000)**             |
|:-------------------------------:|:------------------------------------:|:------------------------------------:|:------------------------------------:|
| ![](./docs/resources/lenna.png) | ![](./docs/resources/lenna_1000.png) | ![](./docs/resources/lenna_2000.png) | ![](./docs/resources/lenna_5000.png) |

## Documentation in different languages 🚧

This section is still under construction and it's gonna be released soon.

## External links

1. [Lenna (Wikipedia)](https://en.wikipedia.org/wiki/Lenna)