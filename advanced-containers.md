---
title: Creating More Complex Container Images
teaching: 30
exercises: 30
---

::::::::::::::::::::::::::::::::::::::: objectives

- Explain how you can include files within container images when you build them.
- Explain how you can access files on the host from your containers.

::::::::::::::::::::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::::::::::: questions

- How can I add local files (e.g. data files) into container
  images at build time?

- How can I access files stored on the host system from within a running Podman
  container?

::::::::::::::::::::::::::::::::::::::::::::::::::

In order to create and use your own container images, you may need more information than
our previous example. You may want to use files from outside the container,
that are not included within the container image, either by copying the files
into the container image, or by making them visible within a running container from their
existing location on your host system. You may also want to learn a little bit
about how to install software within a running container or a container image.
This episode will look at these advanced aspects of running a container or building
a container image. Note that the examples will get gradually
more and more complex -- most day-to-day use of containers and container images can be accomplished
using the first 1--2 sections on this page.

## Linking our container to the computer's filesystem

We often want to use files that live outside of our container, either because they are too big
or are constantly changing. Having a link to our computer from inside the container can be very useful, and often essential for many workflows.

We can create a mount between our computer and the running container by using an additional
option to `podman container run`. We'll also use the variable `${PWD}` which will substitute
in our current working directory. The option will look like this

`--mount type=bind,source=${PWD},target=/data`

What this means is: make my current working directory (on the host computer) -- the source --
*visible* within the container that is about to be started, and inside this container, name the
directory `/data` -- the target.

:::::::::::::::::::::::::::::::::::::::::  callout

## Types of mounts

You will notice that we set the mount `type=bind`, there are other types of mount that
can be used in Podman (e.g. `volume` and `tmpfs`). We do not cover other types of mounts
or the differences between these mount types in the course as it is more of an advanced
topic. You can find more information on the different mount types in
[the Docker documentation](https://docs.docker.com/storage/) and how to use them in
[the Podman documentation](https://docs.podman.io/en/latest/markdown/podman-run.1.html#mount-type-type-type-specific-option).


::::::::::::::::::::::::::::::::::::::::::::::::::

# TODO: Fix mount section to use a proper example

Let's add a new line to the `Dockerfile` we've been using so far to create a copy of `csv_sum.py`.
We can do so by using the `COPY` keyword.

```
COPY csv_sum.py /app/
```

The `csv_sum.py` program takes in a CSV file and gives us another CSV file with all the lines summed up.

Let's build the container and tag it with something new:

```bash
$ podman image build -t alice/csv_sum .
```

To use this container, we need a way to access data on the host computer without copying it in the build step.
Using the bind mount from earlier, we can try and run the file with our input data `plankton.csv` and output `output.csv`:

```bash
$ podman container run --mount type=bind,source=${PWD},target=/data alice/csv_sum python3 /app/csv_sum.py /data/plankton.csv /data/output.csv
```

:::::::::::::::::::::::::::::::::::::::::  callout

## Paths inside containers

Notice how we've specified `/app/` and `/data/` with a leading slash, from the root of the container. While this would be very messy on a real Linux computer,
it's very common to see oddly named directories on the root of a container. `/app` is a very common place to see scripts and code copied to within a container.
Similarly, a bind mounted area may be at a root location such as `/data`, or might be in a more FHS-like place such as `/mnt/data`.

::::::::::::::::::::::::::::::::::::::::::::::::::

You should now see an output CSV file plopped right back into your current working directory. This is bind mounts at work. We can have a container to package
up all of our code into a nice controlled environment, while still allowing access to our files. As we can also say where we want the source to come from, we can also limit a container's
access to our host computer. It's really important to limit the scope of bind mounts, especially when you're running a container for the first time. Remember that the container can
do whatever it wants to the source directory given in the bind mount.

:::::::::::::::::::::::::::::::::::::::::  callout

## Other Commonly Used Podman Run Flags

Podman run has many other useful flags to alter its function.
A couple that are commonly used include `-w` and `-u`.

The `--workdir`/`-w` flag sets the working directory a.k.a. runs the command
being executed inside the directory specified.
For example, the following code would run the `pwd` command in a container
started from the latest ubuntu image in the `/home/ubuntu` directory and print
`/home/ubuntu`. Podman requires the working directory specified to already
exist in the image.

```
podman container run -w /home/ubuntu/ ubuntu pwd
```

The `--user`/`-u` flag lets you specify the username you would like to run the
container as.  This is helpful if you'd like to write files to a mounted folder
and not write them as `root` but rather your own user identity and group.
A common example of the `-u` flag is `--user $(id -u):$(id -g)` which will
fetch the current user's ID and group and run the container as that user.

::::::::::::::::::::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::::::::::  challenge

## Exercise: Checking the options

Our Podman command has gotten much longer! Can you go through each piece of
the Podman command above and explain what it does? How would you characterize
the key components of a Podman command?

:::::::::::::::  solution

## Solution

Here's a breakdown of each piece of the command above

- `podman container run`: use Podman to run a container
- `--mount type=bind,source=${PWD},target=/temp`: connect my current working directory (`${PWD}`) as a folder
  inside the container called `/temp`
- `alice/alpine-python`: name of the container image to use to run the container
- `python3 /temp/sum.py`: what commands to run in the container

More generally, every Podman command will have the form:
`podman [action] [podman options] [podman container image] [command to run inside]`

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::

Mounting a directory can be very useful when you want to run the software inside your container on many different input files.
In other situations, you may want to save or archive an authoritative version of your data by adding it to the container image permanently. That's what we will cover next.

## The Importance of Command Order in a Dockerfile

When you run `podman image build` it executes the build in the order specified
in the `Dockerfile`.
This order is important for rebuilding and you typically will want to put your `RUN`
commands before your `COPY` commands.

Podman builds the layers of commands in order.
This becomes important when you need to rebuild container images.
If you change layers later in the `Dockerfile` and rebuild the container image, Podman doesn't need to
rebuild the earlier layers but will instead used a stored (called "cached") version of
those layers.

For example, in an instance where you wanted to copy `multiply.py` into the container
image instead of `sum.py`.
If the `COPY` line came before the `RUN` line, it would need to rebuild the whole image.
If the `COPY` line came second then it would use the cached `RUN` layer from the previous
build and then only rebuild the `COPY` layer.

## More fancy `Dockerfile` options (optional, for presentation or as exercises)

We can expand on the example above to make our container image even more "automatic".
Here are some ideas:

### Make the `sum.py` script run automatically

```
FROM alpine
RUN apk add --update python3 py3-pip python3-dev
COPY sum.py /home

# Run the sum.py script as the default command
CMD ["python3", "/home/sum.py"]
```

Build and test it:

```bash
$ podman image build -t alpine-sum:v1 .
$ podman container run alpine-sum:v1
```

You'll notice that you can run the container without arguments just fine,
resulting in `sum = 0`, but this is boring. Supplying arguments however
doesn't work:

```bash
podman container run alpine-sum:v1 10 11 12
```

results in

```output
Error: preparing container 8444a537a847f5b4d75a56fec767bfaf59a6f417277c36c0e46422f12c4fe01d for attach:
crun: executable file `10` not found in $PATH:
No such file or directory: OCI runtime attempted to invoke a command that was not found
```

This is because the arguments `10 11 12` are interpreted as a
*command* that replaces the default command given by `CMD ["python3", "/home/sum.py"]` in the image.

To achieve the goal of having a command that *always* runs when a
container is run from the container image *and* can be passed the arguments given on the
command line, use the keyword `ENTRYPOINT` in the `Dockerfile`.

```
FROM alpine

RUN apk add --update python3 py3-pip python3-dev
COPY sum.py /home

# Run the sum.py script as the default command and
# allow people to enter arguments for it
ENTRYPOINT ["python3", "/home/sum.py"]

# Give default arguments, in case none are supplied on
# the command-line
CMD ["10", "11"]
```

Build and test it:

```bash
$ podman image build -t alpine-sum:v2 .
# Most of the time you are interested in the sum of 10 and 11:
$ podman container run alpine-sum:v2
# Sometimes you have more challenging calculations to do:
$ podman container run alpine-sum:v2 12 13 14
```

:::::::::::::::::::::::::::::::::::::::::  callout

## Overriding the ENTRYPOINT

Sometimes you don't want to run the
image's `ENTRYPOINT`. For example if you have a specialized container image
that does only sums, but you need an interactive shell to examine
the container:

```bash
$ podman container run -it alpine-sum:v2 /bin/sh
```

will yield

```output
Please supply integer arguments
```

You need to override the `ENTRYPOINT` statement in the container image like so:

```bash
$ podman container run -it --entrypoint /bin/sh alpine-sum:v2
```

::::::::::::::::::::::::::::::::::::::::::::::::::

### Add the `sum.py` script to the `PATH` so you can run it directly:

```
FROM alpine

RUN apk add --update python3 py3-pip python3-dev

COPY sum.py /home
# set script permissions
RUN chmod +x /home/sum.py
# add /home folder to the PATH
ENV PATH /home:$PATH
```

Build and test it:

```bash
$ podman image build -t alpine-sum:v3 .
$ podman container run alpine-sum:v3 sum.py 1 2 3 4
```

:::::::::::::::::::::::::::::::::::::::::  callout

## Best practices for writing Dockerfiles

Take a look at Nüst et al.'s "[*Ten simple rules for writing Dockerfiles for reproducible data science*](https://doi.org/10.1371/journal.pcbi.1008316)" [1]
for some great examples of best practices to use when writing Dockerfiles.
The [GitHub repository](https://github.com/nuest/ten-simple-rules-dockerfiles) associated with the paper also has a set of [example `Dockerfile`s](https://github.com/nuest/ten-simple-rules-dockerfiles/tree/master/examples)
demonstrating how the rules highlighted by the paper can be applied.

<small>[1] Nüst D, Sochat V, Marwick B, Eglen SJ, Head T, et al. (2020) Ten simple rules for writing Dockerfiles for reproducible data science. PLOS Computational Biology 16(11): e1008316. [https://doi.org/10.1371/journal.pcbi.1008316](https://doi.org/10.1371/journal.pcbi.1008316)</small>


::::::::::::::::::::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::::::::::: keypoints

- Podman allows containers to read and write files from the Podman host using bind mounts.

::::::::::::::::::::::::::::::::::::::::::::::::::


