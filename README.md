[![Codacy Badge](https://api.codacy.com/project/badge/Grade/60bf2812dbb54e03ace2a9baa9f205dd)](https://app.codacy.com/app/borfast/acmemegastore?utm_source=github.com&utm_medium=referral&utm_content=borfast/acmemegastore&utm_campaign=badger)
[![Build Status](https://travis-ci.org/borfast/acmemegastore.svg?branch=master)](https://travis-ci.org/borfast/acmemegastore)
[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/borfast/acmemegastore/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/borfast/acmemegastore/?branch=master)

This is a small sample project I made in the past for a job application. I
decided to publish it on Github, so I cleaned it up, updated it and changed
it so it's not easily found by other applicants trying to cheat.

It implements a new feature for the imaginary Acme Megastore e-commerce
platform. It produces a list of popular purchases, so customers can see who
else bought the same products as them.

It accepts HTTP requests to `/api/recent_purchases/:username` and responds
with a list of recently purchased products, and the names of other users who
recently purchased them.

Originally, data about users, products, and purchases was available via an
external API referred to as "data API", provided to me by an outside server.
In order to openly publish the code without revealing the company and
without depending on their server, I reimplemented the data API using Flask.
All its code is in `acme/data`, specifically the `acme/data/data_server.py`
file. In order to simulate network latency and show caching in effect, the
data API delays its response by a random amount. A full reference for the
data API is available in `doc/data_api.md`. If you run `docker-composer up`,
a container running it will be launched for you. For now, there are there are
no tests for the data API since it wasn't something I wrote for the original
submission. I might add them later.

There were two specific details requested:
* The application must cache API requests so that it can respond as quickly
 as possible.
* If a given username cannot be found, the API should respond with
 "User with username of '{{username}}' was not found"

This is how it was requested that the code determined the "Popular purchases":

* Fetch 5 recent purchases for the given user:
`GET /api/purchases/by_user/:username?limit=5`
* For each of the resulting products, get a list of all people who previously
purchased that product: `GET /api/purchases/by_product/:product_id`
* At the same time, request info about the products:
 `GET /api/products/:product_id`
* Finally, put all of the data together and sort it so that the product with
 the highest number of recent purchases is first.

Example response:
```
[
 {
   "id": 555622,
   "face": "｡◕‿◕｡",
   "price": 1100,
   "size": 27,
   "recent": [
     "Frannie79",
     "Barney_Bins18",
     "Hortense6",
     "Melvina84"
   ]
 },
 ...
]
```

The remainder of this file is my original "report" for the job application.


### README.md

This over-sized readme file is meant to explain the rationale behind some of
the decisions I made while writing this, as well as allow you to navigate the
project and understand how to run it.

Even though this is a ridiculously simple application, I did some things in a
bit more serious way in order to demonstrate some more skills and knowledge
for larger scale and more complex applications.

For example, I could have done all of this in one single file in a
monolithic way but I preferred to keep things as modular, independent
and decoupled as possible to demonstrate some principles which I consider
important, such as dependency injection (note that I'm not talking about a
DI framework or IoC container, just the basic pattern of injecting
dependencies into an object or function instead of creating them in it, or
letting it find the dependency), unit tests, etc.

One of the advantages of DI is that it allows for much easier isolated testing
and as such, I also wrote a few tests. I didn't aim for 100% coverage but the
tests I wrote should be enough for demonstration purposes.  In a real project
I would aim for much higher test coverage.

Another important principle that works in tandem with DI is the Liskov
Substitution Principle (LSP), which I demonstrate on the Cache classes and
which allows for the easy substitution of the RedisCache with a MemoryCache
in the API tests. The current implementation uses Redis as a cache backend
but by having an abstract base cache class defining an "interface" and
having the Api class based on that interface, replacing Redis with something
else would be a simple matter of writing a new cache class implementing the
5 methods from AbstractCache and passing an instance of it to the Api
constructor instead of an instance of RedisCache. I didn't do this for other
classes to save time.

Asyncio and aiohttp were used for the implementation because Acme Megastore's
business is clearly growing at an unprecedented pace and their
e-commerce platform will need to be able to handle many concurrent users, a
goal which is better served by an asynchronous server than traditional
blocking code. Plus, it's more impressive than just plain-old blocking code
and thus I can show off a little more. :-)

Redis was used as a cache backend. I could have just as easily used
memcached but there's no significant difference in performance and Redis is
more versatile, meaning that if necessary it could be used for other purposes
without having to introduce another piece of technology into the application
stack. Still, if a different cache backend was required, it could easily be
replaced as stated above. An important note regarding Redis and the cache: to
keep things simple I did not worry about persistent storage for Redis, which
means that depending on the configuration present in the Redis container, each
time Redis is restarted, all the cache may be wiped.

In order to simplify the task of getting the application up and running and
since Docker is so prevalent these days, I created the necessary files
(`Dockerfile` and `docker-compose.yml`) to run the application without having
to set up anything manually. The last section of this file contains
instructions for running the application in Docker and also manually, if
required, or if you want to run the provided unit tests.


## Project structure

This is not meant to be an exhaustive description of each file and
directory, just a brief overview of the non-obvious, most important files and
of how things are organised.

### Environment variables

The application reads some configuration values from environment variables.

In order to make it easier to set up, it can also read the necessary values 
from a `.env` file in the project root. This file does not exist in the 
repository, since it's unique to each system it will run on. 
 
There is a file called `dot_env_example` which you can use as a base to 
create your own `.env`. The variable names should be self-explanatory.

Fetching configuration data from environment variables allows the
application to run seamlessly on platforms such as Heroku,
which use environment variables to pass configuration settings to
the applications. It also allows you to create custom Docker images more 
easily without having to hard-code any settings. Finally, it allows you
to keep configuration separated from the code, making it safer (no 
credentials to be compromised) and easier to scale or move the application 
to more or different servers.

### Dependencies and Pipenv

This project uses [Pipfile](https://github.com/pypa/pipfile) to declare its 
dependencies. You can install them using [Pipenv](http://pipenv.org/) (see 
the "Installing Python 3.6" section further down for details).

### `fixtures` and `test` directories

In order to avoid having to use the data API while testing, I collected
some data from it and saved it to JSON files so I could make some of the
tests a bit more realistic. These files are saved in the `test/fixtures`
directory. I could also have done this with Faker, with the added bonus of
being more future-proof but this way it was quicker.

Unsurprisingly, the `test` directory contains the unit tests.

### `acme` directory

This is the meat of the project. It's where all the source code is kept. The
main file is `server.py`, from which you can follow the usage of the
other files and the execution logic of the application.

Almost all files here include a single class, which is responsible for a
single thing. For instance, `api.py` contains the `Api` class, which is
responsible for communicating with the data API, and nothing else. Caching
is handled elsewhere (in `cache.py`), assembling the results is handled
elsewhere (in `popular.py`), etc.

The code first creates an instance of the `Megastore` class (which lives in
`Megastore.pyore.py`) and uses it as the handler for the aiohttp
`web.Application` instance. `Megastore` has some dependencies that must be
injected, though, and these dependencies also have other dependencies, so
before instantiating `Megastore` I create instances of those classes (`Api`,
`AsyncHttpClient`, `RedisCache`, etc) and pass them where necessary.

Note that `server.py` is where all the dependencies are created. No
dependency creation occurs within other classes. For bigger projects, a
dependency injection framework may be useful but in this case, it would be
overkill.

## Assumptions and shortcuts

In order to save some time, I made some assumptions and took some shortcuts
where I considered they wouldn't hurt the performance of the application or
the demonstration of my skills. In a real project, I would have clarified
some of these beforehand with a project owner or manager. These are
hopefully all of them, as far as I can recall. They are also documented in
comments in the code where they take place.

* I didn't write tests for absolutely everything, only enough for
demonstration purposes.

* I didn't create abstract base classes / "interfaces" for every case.

* I assumed when someone accesses the API without specifying a username, it
should return a 404.

* When fetching data from the data API, as long as the response doesn't have
an error status code, I immediately decode the response assuming it is a
JSON string.

* When counting the number of purchases per product, I assumed the same
person buying the same product twice counts as two purchases for the purpose
of sorting the final list of popular products by number of purchases. The other
possibility would be to count just one purchase per person, even if that person
bought the same product more than once, which effectively is counting how many
people bought the product and not how many total purchases the product had.

* For the final list of popular products, I assumed the end user is not
interested in knowing how many times someone purchased a certain product, so
any duplicated user names are removed.


## How to run the project

There are two ways to run the project:

1. Isolated in a couple of Docker containers;
2. Manually / directly in your machine.

The first option is probably the easiest. It sets up a couple of Docker
containers with everything ready for you, while the second option requires
that you install everything manually.

Note that in order to run the supplied unit tests you have to use the manual
method (see below). It is not required to have Redis running nor access to
the data API, since these services are all mocked in the tests.


### Running with Docker

For this option you just need Docker and Docker Compose installed. For
Windows and Mac users, the Docker Toolbox contains everything you need and
it's probably the easiest way to go. Linux installation requires a couple
extra steps but it's not complicated. They have instructions here:
https://docs.docker.com/compose/install/

After having Docker and Docker Compose installed, running the project is as
simple as executing `docker-compose up` inside the `docker` directory.

You should see some output from Docker building the images (only the first
time you run it), then Redis will also output some information and the API will
be available at `http://localhost:8080/api/recent_purchases/`

### Running directly on your machine

This option is a bit more involved since it requires installing some
software, namely Python 3.6 (which is not commonly installed in operating
systems our-of-the-box), Redis and a few Python packages.

#### Installing Python 3.6

You need Python 3.5 or newer because of the async/await syntax which is only
available from 3.5 and later.

To install Python I strongly recommend using
[pyenv](https://github.com/yyuu/pyenv) and for the remainder of these 
instructions I assume you are using it. I suggest you use the automatic 
installer, since it installs pyenv and its companion tools for you, as well 
as a handy `pyenv update` command. Pyenv allows you to have multiple Python 
versions installed in your system without conflicting with one another.

After having pyenv installed you need to install Python 3.5 or newer. At the
time of writing the most recent version is 3.6.4 and I will assume that's
the version you will use. You can install it with `pyenv install 3.6.4`. 
This might take a few minutes.

Now you can ask Pipenv to install the project dependencies by running 
`pipenv install --python 3.6.4` if you want only the production dependencies,
or  `pipenv install --dev --python 3.6.4` if you want local development and 
testing dependencies.

Pipenv will install Python 3.6.4 via Pyenv, if it is not yet installed,
create a new virtual environment for the project using the specified Python 
version, and install all the dependencies into it.


#### Installing Redis

Redis can be installed via some package managers on Mac and Linux or
compiled from source. They have instructions for that:
http://redis.io/topics/quickstart

I recommend using a package manager or better yet, especially if you use
Windows (because Redis is not very well supported on Windows), use a Docker
container (you can see how to install Docker above):
`docker run --name acmemegastore-redis -d redis`

This will launch a Docker container named `acmemegastore-redis`. It will
be necessary to change the `REDIS_HOST` setting in `.env` and set it to the
Docker container's IP address, which you can get by running the following
command:
`docker inspect acmemegastore-redis | grep "IPAddress"`

After you're done, you can remove the container and the Redis image
(assuming you don't use it for anything else) with the following commands:
`docker rm acmemegastore-redis` and `docker rmi redis`


#### Running the application

With all the Python packages installed and Redis running, you're ready to
finally launch the application. In the project root, execute `pipenv run python
 -m acme.server`.

For this method, the API is available at
`http://0.0.0.0:8080/api/recent_purchases/` instead of
`http://localhost:8080/api/recent_purchases/`
