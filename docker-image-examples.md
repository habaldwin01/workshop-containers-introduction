---
title: Examples of Using Container Images in Practice
teaching: 10
exercises: 15
---

::::::::::::::::::::::::::::::::::::::: objectives

- Use existing container images and Docker in a research project.

::::::::::::::::::::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::::::::::: questions

- How can I use Docker for my own work?

::::::::::::::::::::::::::::::::::::::::::::::::::

Now that we have learned the basics of working with Docker container images and containers,
let's apply what we learned to an example workflow.

You may choose one or more of the following examples to practice using containers.

## GitHub Actions Example

In this [GitHub Actions example](../instructors/e01-github-actions.md), you can learn more about
continuous integration in the cloud and how you can use container images with GitHub to
automate repetitive tasks like testing code or deploying websites.

## Geospatial Example

The Github repository, https://github.com/NOC-OI/docker-gdal-demo contains an example Jupyter notebook which visualises some GeoTIFF files containing data about the extent of Arctic sea ice.
Let's build a container which let's us run this code.



:::::::::::::::::::::::::::::::::::::::  challenge

## Choosing a base image

1. Find a Jupyter base image to use, there are several supplied by the Jupyter project the project, find an appropriate minimal image to use as a base. (Hint: you don't want images from Docker Hub)
2. Download a copy of the Jupyter notebook and datafiles from [the Github repository](https://github.com/NOC-OI/docker-gdal-demo/archive/refs/heads/main.zip).
3. Extract the zip file, this should create a directory called `docker-gdal-demo-main` containing the notebook (gdal-example.ipynb) and several `.tif` files.
4. Run the Jupyter container with the directory you extracted the zip into mounted as `/home/jovyan/work`.

:::::::::::::::  solution

The documentation from [https://jupyter-docker-stacks.readthedocs.io/en/latest/](https://jupyter-docker-stacks.readthedocs.io/en/latest/) mentions the base-notebook image hosted on the quay.io container registry.

```bash
curl https://codeload.github.com/NOC-OI/docker-gdal-demo/zip/refs/heads/main -o main.zip
unzip main.zip #this probably doesn't work in windows cmd/powershell, unzip by right clicking and choosing extract in the file manager.
podman run --mount type=bind,source=$PWD/docker-gdal-demo-main,target=/home/jovyan/work quay.io/jupyter/base-notebook
```

:::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::::::::::::::::


### Exposing Network Ports

At the end of it's startup sequence Jupyter tells us to connect to a URL starting http://127.0.0.1 or http://localhost. 
These refer to a service running on our own computer, but if we try to connect to this we will get an error because the Jupyter server is only accessible inside the container. 
To get access to the Jupyter service we need to expose a network port from our container to our host system. The `-p` option to Podman allows us to map ports from the host to the container.
Jupyter notebook server is accessed via port 8888. We are going to map 8888 port in the container to 8888 port on our (host) computer.

```bash
podman container run --mount type=bind,source=$PWD/docker-gdal-demo-main,target=/home/jovyan/work -p 8888:8888 quay.io/jupyter/base-notebook 
```

### Installing the Dependencies

When we try to run the notebook, we see we don't have the gdal libraries available.

Let's try to install the dependecies inside the container. To do it, we are going to run the container in the interactive mode. 
We do need to install new packages and we will need root access.

```bash
podman container run -it -e GRANT_SUDO=yes --user root quay.io/jupyter/base-notebook /bin/bash
```

We are going to install Python libraries gdal and matplotlib, which we use in this our notebook.

```bash
mamba install gdal matplotlib
```

It worked in the container, lets put it in the Docekrfile and try to build an image.

```Dockerfile
FROM quay.io/jupyter/base-notebook

RUN mamba install gdal matplotlib
```

Let's build the container and name it jupyter-gdal.
```bash
podman build -t jupyter-gdal .
```

Let's run it. Dont' forget to mount our folder with data we want to visualise
```bash
podman container run --mount type=bind,source=$PWD/docker-gdal-demo-main,target=/home/jovyan/work -p 8888:8888 jupyter-gdal
```

:::::::::::::::::::::::::::::::::::::::  challenge

How else could we have solved this problem?

There are several other approaches we could have taken to running this script.
We could have included the notebook file inside the container. Or we could have converted the Jupyter notebook to a Python script which creates an image file and saves that to our home directory.
We could have even included the data inside the container.

Discuss which approach would you take and why.

::::::::::::::::::::::::::::::::::::::::::::::::::


## Seeking Examples

Do you have another example of using Docker in a workflow related to your field?  Please [open a lesson issue] or [submit a pull request] to add it to this episode and the extras section of the lesson.

[submit a pull request]: https://github.com/carpentries-incubator/docker-introduction/pulls

:::::::::::::::::::::::::::::::::::::::: keypoints

- There are many ways you might use Docker and existing container images in your research project.

::::::::::::::::::::::::::::::::::::::::::::::::::
