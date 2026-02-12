# 🏃‍♀️ running 🏃
[![image](https://img.shields.io/pypi/v/running.svg)](https://pypi.org/project/running/)
[![image](https://img.shields.io/pypi/pyversions/running.svg)](https://pypi.org/project/running/)

A flexible but user-friendly running pace calculator as a command line tool.

# Installation
```
$ pip install running
```

# Usage
Call `running` with two of the three arguments `pace`, `distance` or `time`, and it will calculate the missing one for you.

```
$ running --pace 4:30/km --distance marathon 
Elapsed time: 3:09:53 [H:]MM:SS
```

You can also just use the first letter of the argument names:
```
$ running -p 4:30 -d marathon
```

Note that distance unit for the pace was omitted, defaulting to kilometer. This can be changed with the `unit` (`-u`) parameter as follows:
```
$ running -p 8:00 -d 10km -u miles
Elapsed time: 49:43 [H:]MM:SS
```

You can also directly specify the units for the pace:
```
$ running -p 6min/mile -t 1hour
Travelled distance: 16.09 km
$ running -d half-marathon -t 1:45:00
Required pace: 04:59 /km
```

You can also view split times with `--splits` (`-s`):
```
$ running -p 4:30 -d marathon --splits
Elapsed time: 3:09:53 [H:]MM:SS

   1 km  04:30
   2 km  09:00
   3 km  13:30
  ...
  42 km  3:09:00
42.195 km  3:09:53
```

Predict race times for other distances with `--predict` (`-r`), using the Riegel formula:
```
$ running -d 10km -t 45:00 --predict
Required pace: 04:30 /km

Race predictions:
          1500m    06:01   (04:01 /km)
         1 mile    06:29   (04:02 /km)
             5K    21:35   (04:19 /km)
            10K    45:00   (04:30 /km)
  Half-marathon  1:39:17   (04:42 /km)
       Marathon  3:27:01   (04:54 /km)
```

The tool is quite flexible in terms of the valid expressions for the arguments, see `running --help` for more examples.

**Ever wondered how fast Usain Bolt would run a marathon?**
```
$ running -p bolt -d marathon
Elapsed time: 1:07:22 [H:]MM:SS
```
