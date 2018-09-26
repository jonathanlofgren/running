# 🏃running 🏃

A flexible but user-friendly running pace calculator as a command line tool.

# Installation
```
$ pip install running
```

# Usage
Call `running` with two of the three arguments `pace`, `distance` or `time`, and it will calculate the missing one for you.

```
$ running --pace 4:30/km --distance marathon 
Ellapsed time: 3:09:53 [H:]MM:SS
```

You can also just use the first letter of the argument names:
```
$ running -p 4:30 -d marathon
```

Note that distance unit for the pace was omitted, defaulting to kilometer. This can be changed with the `unit` (`-u`) parameter as follows:
```
$ running -p 8:00 -d 10km -u miles
Ellapsed time: 49:43 [H:]MM:SS
```

You can also directly specify the units for the pace:
```
$ running -p 6min/mile -t 1hour
Travelled distance: 16.09 km
$ running -d half-marathon -t 1:45:00
Required pace: 04:59 /km
```

The tool is quite flexible in terms of the valid expressions for the arguments, see `running --help` for more examples.

**Ever wondered how fast Usain Bolt would run a marathon?**
```
$ running -p bolt -d marathon
Ellapsed time: 1:07:22 [H:]MM:SS
```
